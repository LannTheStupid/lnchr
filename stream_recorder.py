from argparse import ArgumentParser
from subprocess import call
from sys import stderr

from rfc3987 import match

from application_local_file import Nicknames, UserStat

APPLICATION_NAME = 'stream_launcher'
ALIAS_FILE_NAME = 'aliases.dat'


def record_the_stream(arguments, statistics, nicknames):
    streamer = arguments.streamer

    if match(streamer, 'absolute_URI'):
        url = streamer
        statistics.add_usage(url)
    elif nicknames.find(streamer):
        url = nicknames.get(streamer)
    else:
        print("Nickname", streamer, "has not been defined yet", file=stderr)
        return 1

    statistics.save()
    player_command = ''
    if arguments.mode == 'video':
        quality = 'best'
        player_command = '--file-caching=10000'
    elif url.find('twitch') >= 0:
        quality = 'audio'
    else:
        quality = 'worst'
        player_command = '--novideo'

    exec_string = "livestreamer " + "--player \"'C:\\Program Files\\VideoLAN\\VLC\\vlc.exe' " + player_command + "\"" \
                  + ' ' + url + ' ' + quality

    if arguments.dry_run:
        print("The resulting command string:")
        print("[ ", exec_string, " ]");
        return 0
    else:
        print('The real execution starts here')
        return call(exec_string, shell=False)


def record_the_stream():
    command_parser = ArgumentParser(description='Wrapper for livestreamer tool')
    command_parser.add_argument('streamer', nargs='?', help="Streamer's nick name or URL of the stream")
    command_parser.add_argument('-d', '--directory', help='The directory where records will be stored.', default='./')
    command_parser.add_argument('-t', '--time', help='Time to wait between attempts to reconnect to the stream', default = )
    group = command_parser.add_mutually_exclusive_group()
    group.add_argument('-n', '--dry-run', help='Write the command string to stdout, but do not execute it',
                       action='store_true')
    group.add_argument('-a', '--aliases', help='Print available aliases and exit',
                       action='store_true')
    arguments = command_parser.parse_args()

    rv = 0
    nicknames = Nicknames(APPLICATION_NAME, ALIAS_FILE_NAME)
    nicknames.load()
    if arguments.aliases:
        print(str(nicknames))
    else:
        rv = record_the_stream(arguments, nicknames)

    return rv


if __name__ == '__main__':
    record_the_stream()
