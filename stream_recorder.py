from argparse import ArgumentParser
from subprocess import call
from pathlib import PurePath
from time import sleep, time
from datetime import timedelta

from rfc3987 import match, parse

from application_local_file import Nicknames
from recorder_file_handler import get_file_name

APPLICATION_NAME = 'stream_recorder'
LAUNCHER_APPLICATION_NAME = 'stream_launcher'
ALIAS_FILE_NAME = 'aliases.dat'
DEFAULT_ROOT_DIRECTORY = 'c:\\tmp'
DEFAULT_TIMEOUT = 120. # (2 minutes)
DEFAULT_ATTEMPTS = 10


def parse_streamer_url(url, nicknames):
    if match(url, 'absolute_URI'):
        rv1 = [x for x in parse(url)['path'].split('/') if x][-1]
        rv2 = url
        return rv1, rv2
    elif nicknames.find(url):
        return url, nicknames.get(url)
    else:
        print("Nickname \"{0}\" has not been defined yet".format(url))
        return None, None


#   Generates pairs of attempt number and current record file.
#   Exits when the number of attempts is reached (it assumes that either files will be less than attempts
#   or that a write error happens)
def next_try(retries, directory, alias):
    file_name_generator = get_file_name(directory, alias, retries)
    for attempt in range(0, retries):
        yield(attempt, next(file_name_generator))


def record_and_report(dry_run, exec_string):
    if dry_run:
        print('Dry run invoked. The command string is')
        print(exec_string)
        rv = 0
    else:
        start_time = time()
        rv = call(exec_string)
        delta_time = time() - start_time
        print('Recording time:', timedelta(seconds = delta_time))
    return rv


def record(arguments, nicknames):
    (alias, url) = parse_streamer_url(arguments.streamer, nicknames)
    if not alias:
        exit(1)
    exec_string_stem = 'livestreamer ' + url + ' best -o'
    for (attempt, filename) in next_try(arguments.retries, arguments.directory, alias):
        exec_string = exec_string_stem + ' ' + filename
        try:
            print('Recording stream', alias, 'from', url)
            rv = record_and_report(arguments.dry_run, exec_string)
            print('Recorded into', filename, 'with return code', rv, 'attempt', attempt)
            print('Sleeping for (seconds):', arguments.time)
            sleep(arguments.time)
        except OSError as err:
            print('Error launching livestreamer: {0}, code {1}'.format(err.strerror, err.errno))
            exit (2)
    return 0


def record_the_stream():
    command_parser = ArgumentParser(description='Stream Recorder. Uses livestreamer to get the data')
    command_parser.add_argument('streamer', nargs='?', help="Streamer's nick name or URL of the stream")
    command_parser.add_argument('-d', '--directory',
                                help='The directory where recorded files are stored.',
                                type=PurePath,
                                default=DEFAULT_ROOT_DIRECTORY,
                                )
    command_parser.add_argument('-t', '--time', help='Time (in seconds) between attempts to reconnect to the stream',
                                default=DEFAULT_TIMEOUT, type=float)
    command_parser.add_argument('-r', '--retries', help='Number of attempts before the stream is considered down',
                                default=DEFAULT_ATTEMPTS, type=int)
    group = command_parser.add_mutually_exclusive_group()
    group.add_argument('-n', '--dry-run', help='Write the command string to stdout, but do not execute it',
                       action='store_true')
    group.add_argument('-a', '--aliases', help='Print available aliases and exit',
                       action='store_true')
    arguments = command_parser.parse_args()

    rv = 0
    nicknames = Nicknames(LAUNCHER_APPLICATION_NAME, ALIAS_FILE_NAME)
    nicknames.load()
    if arguments.aliases:
        print(str(nicknames))
    else:
        rv = record(arguments, nicknames)

    return rv


if __name__ == '__main__':
    record_the_stream()
