import os
import click
import logging
import asyncio
import tarfile
from functools import partial
from hachiko.hachiko import AIOEventHandler
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

input_directory = '/shared/input'
output_directory = '/shared/output'
log_directory = '/shared/output/logs'
start_script = 'start.py'


class DockerInnerHandler(AIOEventHandler, PatternMatchingEventHandler):
    active = False

    def __init__(self, exit, magic_script_pattern, loop=None, **kwargs):
        self._exit = exit

        script_location = os.path.join(input_directory, magic_script_pattern)

        patterns = kwargs['patterns'] if 'patterns' in kwargs else []
        patterns.append(script_location)
        kwargs['patterns'] = patterns

        logging.info('Patterns: %s' % str(kwargs['patterns']))

        AIOEventHandler.__init__(self, loop)
        PatternMatchingEventHandler.__init__(self, **kwargs)

        if os.path.exists(script_location):
            self._loop.call_soon_threadsafe(
                asyncio.async,
                self.handle_exists(script_location, os.path.isdir(script_location))
            )

    @asyncio.coroutine
    def on_moved(self, event):
        if event.dest_path.endswith('/input'):
            yield from self.handle_exists(os.path.join(event.dest_path, 'start.tar.gz'), event.is_directory)

    @asyncio.coroutine
    def handle_exists(self, location, is_directory):
        logging.info("Spotted new start script")

        if self.active:
            logging.error("Already started a script")
            return

        log_file = os.path.join(log_directory, 'job.out')
        err_file = os.path.join(log_directory, 'job.err')

        target_directory = os.path.join(output_directory, 'run')
        try:
            os.makedirs(target_directory)
        except FileExistsError:
            pass

        with tarfile.open(location) as tar:
            for name in tar.getnames():
                if not os.path.abspath(os.path.join(target_directory, name)).startswith(target_directory):
                    logging.error("This archive contains unsafe filenames: %s %s" % (os.path.abspath(os.path.join(target_directory, name)), target_directory))
                    return

            tar.extractall(path=target_directory)

        location = os.path.join(target_directory, start_script)
        if not os.path.exists(location):
            logging.error("This archive is missing a %s" % start_script)

        try:
            self.process = asyncio.create_subprocess_exec(
                *["/usr/bin/python", location],
                stdout=open(log_file, 'w'),
                stderr=open(err_file, 'w'),
                cwd=target_directory
            )
            process = yield from self.process
            asyncio.async(process.wait()).add_done_callback(self._exit)

            self.active = True
        except Exception as e:
            logging.error("Exception raised launching user script: %s"
                          % str(e))
            self._loop.call_soon_threadsafe(partial(self._exit, None))


def exit(loop, observer, future=None):
    exit_file = os.path.join(log_directory, 'exit_status')

    with open(exit_file, 'w') as f:
        if not future:
            f.write('-9999\nNo future returned')
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

    observer.stop()
    loop.stop()
    logging.info("Stopped event loop")
    observer.join()
    logging.info("Observer exited")


@asyncio.coroutine
def run(loop, magic_script):
    observer = Observer()

    event_handler = DockerInnerHandler(partial(exit, loop, observer), magic_script, loop=loop)

    observer.schedule(event_handler, '/shared')
    observer.start()

    logging.info('Observation thread started')


@click.command()
def cli():
    """Manage a single script run for docker-launch"""

    magic_script = "start.tar.gz"

    os.makedirs(log_directory)

    logging.basicConfig(
        filename=os.path.join(log_directory, "docker_inner.log"),
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logging.info('Starting up...')

    loop = asyncio.get_event_loop()

    asyncio.async(run(loop, magic_script))

    try:
        loop.run_forever()
    finally:
        loop.close()

    logging.info('Moving output to final location')

    os.rename(os.path.join('/shared', 'output'), os.path.join('/shared', 'output.final'))

    logging.info('Loop closed and exiting...')
