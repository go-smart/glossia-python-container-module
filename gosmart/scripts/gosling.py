import os
import sys

import click
import logging
import asyncio
import tarfile
import time
import shutil
from functools import partial
from hachiko.hachiko import AIOEventHandler
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger().addHandler(logging.StreamHandler())

input_directory = '/shared/input'
output_directory = '/shared/output'
log_directory = '/shared/output/logs'


class DockerInnerHandler(AIOEventHandler, PatternMatchingEventHandler):
    active = False

    def __init__(self, exit, target, interpreter, archive, passthrough, loop=None, **kwargs):
        self._exit = exit

        self._archive = archive
        self._target = target
        self._passthrough = passthrough
        self._interpreter = interpreter

        patterns = kwargs['patterns'] if 'patterns' in kwargs else []
        patterns.append('input')
        kwargs['patterns'] = patterns

        logging.info('Patterns: %s' % str(kwargs['patterns']))

        AIOEventHandler.__init__(self, loop)
        PatternMatchingEventHandler.__init__(self, **kwargs)

        if os.path.exists(input_directory):
            asyncio.async(self.execute(input_directory))

    @asyncio.coroutine
    def execute(self, location):
        self.active = True

        yield from execute(
            location,
            self._loop,
            self._target,
            self._interpreter,
            self._archive,
            self._exit,
            self._passthrough
        )

    @asyncio.coroutine
    def on_moved(self, event):
        if event.dest_path.endswith('/input'):
            yield from self.handle_exists(event.dest_path)

    @asyncio.coroutine
    def handle_exists(self, location):
        logging.info("Spotted new start script")

        if self.active:
            logging.error("Already started a script")
            return

        yield from self.execute(location)


@asyncio.coroutine
def execute(location, loop, target, interpreter, archive, exit, passthrough=False):
    target_directory = os.path.join(output_directory, 'run')

    try:
        shutil.rmtree(target_directory)
    except FileNotFoundError:
        pass

    if archive:
        try:
            with tarfile.open(os.path.join(location, archive)) as tar:
                os.makedirs(target_directory)

                for name in tar.getnames():
                    if not os.path.abspath(os.path.join(target_directory, name)).startswith(target_directory):
                        logging.error("This archive contains unsafe filenames: %s %s" % (os.path.abspath(os.path.join(target_directory, name)), target_directory))
                        return

                tar.extractall(path=target_directory)
        except IsADirectoryError:
            try:
                os.makedirs(os.path.dirname(target_directory))
            except FileExistsError:
                pass

            shutil.copytree(archive, target_directory)

        location = target_directory
    else:
        os.makedirs(target_directory)

    shutil.copytree(input_directory, os.path.join(target_directory, 'input'))

    if target:
        location = os.path.join(location, target)
        if not os.path.exists(location):
            logging.error("Missing a %s" % target)
    else:
        location = ''

    log_file = os.path.join(log_directory, 'job.out')
    err_file = os.path.join(log_directory, 'job.err')

    command = (interpreter.split(' ') if interpreter else []) + [location]
    logging.info("Running user command: {command}".format(command=" ".join(command)))
    try:
        if passthrough:
            stdout, stderr = sys.stdout, sys.stdout
        else:
            stdout, stderr = open(log_file, 'w'), open(err_file, 'w')

        process = asyncio.create_subprocess_exec(
            *command,
            stdout=stdout,
            stderr=stderr,
            cwd=target_directory
        )
        process = yield from process
        asyncio.async(process.wait()).add_done_callback(exit)
    except Exception as e:
        logging.error("Exception raised launching user script: %s"
                      % str(e))
        loop.call_soon_threadsafe(partial(exit, None))


def exit(loop, observer=None, future=None):
    logging.info("Exiting post-user-command")
    exit_file = os.path.join(log_directory, 'exit_status')

    with open(exit_file, 'w') as f:
        if not future:
            f.write("-9999\nNo future returned")
        elif future.result() != 0:
            try:
                err_file = os.path.join(log_directory, 'job.err')
                with open(err_file, 'r') as err:
                    snippet = '\n'.join(err.readlines()[-10:])
            except:
                snippet = "Could not retrieve STDERR"
            f.write('%d\nError in script: %s' % (future.result(), snippet))
        else:
            f.write('0\nOK')

    if observer:
        observer.stop()
    loop.stop()

    logging.info("Stopped event loop")

    if observer:
        observer.join()
        logging.info("Observer exited")


@asyncio.coroutine
def run(loop, target, interpreter, archive, passthrough):
    observer = Observer()

    event_handler = DockerInnerHandler(partial(exit, loop, observer), target, interpreter, archive, passthrough, loop=loop)

    observer.schedule(event_handler, '/shared')
    observer.start()

    logging.info('Observation thread started')


@click.command()
@click.option('--target', default=None, help='script or executable to run (rel. to input folder/start-archive if applicable)')
@click.option('--interpreter', default=None, help='interpreter to use for running target')
@click.option('--archive', default=None, help='watch for start-archive instead of single file')
@click.option('--override', is_flag=True, help='go straight to execution')
@click.option('--static', is_flag=True, help='do not think about third-party observation or moving output')
@click.option('--delay', default=0, help='wait for N secs before starting watching')
@click.option('--final', default='output', help='location of the final output directory to be sent to GSSA, rel. to /shared')
@click.option('--passthrough', is_flag=True, help='pass through subprocess output, rather than silently logging')
def cli(target, interpreter, archive, override, static, delay, final, passthrough):
    """Manage a single script run for docker-launch"""

    os.makedirs(log_directory, exist_ok=True)

    logfile_handler = logging.FileHandler(os.path.join(log_directory, "docker_inner.log"))
    logging.getLogger().addHandler(logfile_handler)

    logging.info("Starting up...")

    loop = asyncio.get_event_loop()

    if override:
        logging.info("Instructed to override input-waiting")
        exit_cb = partial(exit, loop, None)
        asyncio.async(execute(input_directory, loop, target, interpreter, archive, exit_cb, passthrough))
    else:
        if delay:
            time.sleep(delay)
        asyncio.async(run(loop, target, interpreter, archive, passthrough))

    try:
        loop.run_forever()
    finally:
        loop.close()

    logging.info('Moving output to final location')

    # This two-step approach ensures copying to Glossia is triggered by a move in shared/ and that
    # everything is on the same FS etc. before it happens
    if not static:
        try:
            os.rename(os.path.join('/shared', final), os.path.join('/shared', 'output.tmp'))
        except FileNotFoundError:
            os.makedirs(os.path.join('/shared', 'output.tmp'))

        try:
            os.rename(log_directory, os.path.join('/shared', 'output.tmp', 'logs'))
        except FileExistsError:
            logging.warning('Not copying logs to output as directory already exists')
        os.rename(os.path.join('/shared', 'output.tmp'), os.path.join('/shared', 'output.final'))

    logging.info('Loop closed and exiting...')
