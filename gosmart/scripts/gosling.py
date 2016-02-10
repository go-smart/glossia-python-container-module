import os
import click
import logging
import asyncio
import tarfile
import time
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

    def __init__(self, exit, target, interpreter, archive, loop=None, **kwargs):
        self._exit = exit

        self._archive = archive
        self._target = target
        self._interpreter = interpreter

        patterns = kwargs['patterns'] if 'patterns' in kwargs else []
        patterns.append('input')
        kwargs['patterns'] = patterns

        logging.info('Patterns: %s' % str(kwargs['patterns']))

        AIOEventHandler.__init__(self, loop)
        PatternMatchingEventHandler.__init__(self, **kwargs)

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

        yield from execute(location, self._loop, self._target, self._interpreter, self._archive, self._exit)

        self.active = True


@asyncio.coroutine
def execute(location, loop, target, interpreter, archive, exit):
    target_directory = os.path.join(output_directory, 'run')
    try:
        os.makedirs(target_directory)
    except FileExistsError:
        pass

    if archive:
        with tarfile.open(os.path.join(location, archive)) as tar:
            for name in tar.getnames():
                if not os.path.abspath(os.path.join(target_directory, name)).startswith(target_directory):
                    logging.error("This archive contains unsafe filenames: %s %s" % (os.path.abspath(os.path.join(target_directory, name)), target_directory))
                    return

            tar.extractall(path=target_directory)

        location = target_directory

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
        process = asyncio.create_subprocess_exec(
            *command,
            stdout=open(log_file, 'w'),
            stderr=open(err_file, 'w'),
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
def run(loop, target, interpreter, archive):
    observer = Observer()

    event_handler = DockerInnerHandler(partial(exit, loop, observer), target, interpreter, archive, loop=loop)

    observer.schedule(event_handler, '/shared')
    observer.start()

    logging.info('Observation thread started')


@click.command()
@click.option('--target', default=None, help='script or executable to run (rel. to input folder/start-archive if applicable)')
@click.option('--interpreter', default=None, help='interpreter to use for running target')
@click.option('--archive', default=None, help='watch for start-archive instead of single file')
@click.option('--override', is_flag=True, help='go straight to execution')
@click.option('--delay', default=0, help='wait for N secs before starting watching')
@click.option('--final', default='output', help='location of the final output directory to be sent to GSSA, rel. to /shared')
def cli(target, interpreter, archive, override, delay, final):
    """Manage a single script run for docker-launch"""

    os.makedirs(log_directory, exist_ok=True)

    logfile_handler = logging.FileHandler(os.path.join(log_directory, "docker_inner.log"))
    logging.getLogger().addHandler(logfile_handler)

    logging.info("Starting up...")

    loop = asyncio.get_event_loop()

    if override:
        logging.info("Instructed to override input-waiting")
        exit_cb = partial(exit, loop, None)
        asyncio.async(execute('/shared/input', loop, target, interpreter, archive, exit_cb))
    else:
        if delay:
            time.sleep(delay)
        asyncio.async(run(loop, target, interpreter, archive))

    try:
        loop.run_forever()
    finally:
        loop.close()

    logging.info('Moving output to final location')

    os.rename(os.path.join('/shared', final), os.path.join('/shared', 'output.final'))

    logging.info('Loop closed and exiting...')
