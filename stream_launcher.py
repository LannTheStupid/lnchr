from argparse import ArgumentParser
from sys import stderr
from subprocess import call

from rfc3987 import match
from appdirs import user_data_dir

__author__ = 'ikamashev'
APPLICATION_NAME = 'stream_launcher'
MOST_USED_FILE = ''

nick_dict = {
    'holly': 'http://twitch.tv/holly_forve',
    'fr0st': 'http://twitch.tv/fr0stix',
    'belka': 'http://cybergame.tv/lenko-romashka/',
    'seehaja': 'http://goodgame.ru/channel/kettari/',
    'sky': 'http://twitch.tv/skymaybe'
}


def count_usage(url):


def assemble_command(arguments: object):
    streamer = arguments.streamer
    url = ''

    if match(streamer, 'absolute_URI'):
        url = streamer
        count_usage(url)
    elif streamer in nick_dict:
        url = nick_dict[streamer]
    else:
        print("nick", streamer, "is not defined yet", file=stderr)
        return 1

    quality = ''
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


def launch_the_stream():
    cmdParser = ArgumentParser(description='Wrapper for livestreamer tool')
    cmdParser.add_argument('streamer', help="Streamer's nick name or URL of the stream")
    cmdParser.add_argument('mode', help='Video or audio only', choices=['audio', 'video'])
    cmdParser.add_argument('-n', '--dry-run', help='Write the command string to stdout, but do not execute it',
                           action='store_true')
    arguments = cmdParser.parse_args()
    return assemble_command(arguments)

if __name__ == '__main__':
    launch_the_stream()