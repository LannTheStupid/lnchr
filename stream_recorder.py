from argparse import ArgumentParser, ArgumentTypeError
from datetime import timedelta
from pathlib import PurePath
from subprocess import call
from sys import argv, exit
from time import sleep, time

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


def record_and_report(dry_run, exec_list):
    if dry_run:
        print('Dry run invoked. The command string is')
        print("[", ' '.join(exec_list), "]")
        raise Exception('Dry run: exiting.')
    else:
        start_time = time()
        rv = call(exec_list, shell=False)
        if rv == 0: print('Recording time:', timedelta(seconds=round(time() - start_time)))
    return rv


def record(arguments, nicknames):
    (alias, url) = parse_streamer_url(arguments.streamer[0], nicknames)
    if not alias:
        exit(1)
    exec_list_head = ['streamlink', url, 'best']
    if url.find('twitch') >= 0:
        exec_list_head.append('--twitch-disable-hosting')
    exec_list_head.append('-o')
    for (attempt, filename) in next_try(arguments.retries, arguments.directory, alias):
        exec_list = exec_list_head + [filename]
        try:
            print('Recording stream', alias, 'from', url)
            rv = record_and_report(arguments.dry_run, exec_list)
            print('Attempt', attempt, 'return code', rv)
            print('Sleep for', arguments.time, 's')
            sleep(arguments.time)
        except OSError as err:
            print('Error launching streamlink: {0}, code {1}'.format(err.strerror, err.errno))
            exit(2)
    return 0


def natural_number(parameter):
    value = int(parameter)
    if value < 1 or value != parameter:
        msg = '{0} is not a natural number'.format(parameter)
        raise ArgumentTypeError(msg)
    return value


def create_parser():
    command_parser = ArgumentParser(description='Stream Recorder. Uses streamlink to get the data')
    command_parser.add_argument('streamer', nargs=1, help="Streamer's nick name or URL of the stream")
    command_parser.add_argument('-d', '--directory',
                                help='The directory where recorded files are stored.',
                                type=PurePath,
                                default=DEFAULT_ROOT_DIRECTORY,
                                )
    command_parser.add_argument('-t', '--time', help='Time (in seconds) between attempts to reconnect to the stream',
                                default=DEFAULT_TIMEOUT, type=natural_number)
    command_parser.add_argument('-r', '--retries', help='Number of attempts before the stream is considered down',
                                default=DEFAULT_ATTEMPTS, type=natural_number)
    group = command_parser.add_mutually_exclusive_group()
    group.add_argument('-n', '--dry-run', help='Write the command string to stdout, but do not execute it',
                       action='store_true')
    group.add_argument('-a', '--aliases', help='Print available aliases and exit',
                       action='store_true')
    return command_parser


def record_the_stream():
    command_parser = create_parser()

    if len(argv) == 1:
        command_parser.print_help()
        exit(1)

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
