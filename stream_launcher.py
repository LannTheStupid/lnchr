from argparse import ArgumentParser
from subprocess import call
from sys import stderr, argv, exit

from rfc3987 import match, parse

from application_local_file import Nicknames, UserStat

APPLICATION_NAME = 'stream_launcher'
STAT_FILE_NAME = 'most_used.dat'
ALIAS_FILE_NAME = 'aliases.dat'


def assemble_command(arguments, statistics, nicknames):
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
        print("[ ", exec_string, " ]")
        return 0
    else:
        print('The real execution starts here')
        return call(exec_string, shell=False)


def create_parser():
    command_parser = ArgumentParser(description='Wrapper for livestreamer tool')
    command_parser.add_argument('streamer', nargs='?', help="Streamer's nick name or URL of the stream")
    command_parser.add_argument('mode', nargs='?', help='Video or audio only', choices=['audio', 'video'])
    command_parser.add_argument('-n', '--dry-run', help='Write the command string to stdout, but do not execute it',
                       action='store_true')
    group = command_parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--stat', help='Print usage statistics and exit', action='store_true')
    group.add_argument('-a', '--aliases', help='Print available aliases and exit', action='store_true')
    group.add_argument('-c', '--clear', help='Clear all the statistics with frequencies less than parameter (1 by default)', nargs='?', const='1')
    group.add_argument('-l', '--let', help="Assign an alias to the stream's URL", nargs=2)
    return command_parser


def launch_the_stream():
    parser = create_parser()
    if len(argv) == 1:
        parser.print_help()
        exit(1)

    arguments = parser.parse_args()

    rv = 0
    statistics = UserStat(APPLICATION_NAME, STAT_FILE_NAME)
    statistics.load()
    nicknames = Nicknames(APPLICATION_NAME, ALIAS_FILE_NAME)
    nicknames.load()
    if arguments.stat:
        print(str(statistics))
    elif arguments.aliases:
        print(str(nicknames))
    elif arguments.clear:
        trimmed = statistics.fltr(lambda key, value: value > int(arguments.clear))
        statistics.save()
        print("Statistics cleared: {0}".format(trimmed))
    elif len(arguments.let) == 2:
        (nick, URL) = arguments.let
        nicknames.assign(nick, URL)
        # Extract the last part of URL path as a streamer nick
        streamer = [x for x in parse(URL)['path'].split('/') if x][-1]
        trimmed = statistics.fltr(lambda key, value: streamer not in key)
        statistics.save()
        nicknames.save()
        print("{0} was assigned to {1}; {2} statistics records cleaned".format(nick, URL, trimmed))
    else:
        rv = assemble_command(arguments, statistics, nicknames)

    return rv


if __name__ == '__main__':
    launch_the_stream()
