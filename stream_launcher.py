from argparse import ArgumentParser
from sys import stderr
from subprocess import call
from pprint import pprint
from os.path import join
from json import load, dump

from appdirs import user_data_dir
from rfc3987 import match

__author__ = 'ikamashev'
APPLICATION_NAME = 'stream_launcher'
STAT_FILE_NAME = 'most_used.dat'

nick_dict = {
    'holly': 'http://twitch.tv/holly_forve',
    'fr0st': 'http://twitch.tv/fr0stix',
    'belka': 'http://cybergame.tv/lenko-romashka/',
    'seehaja': 'http://goodgame.ru/channel/kettari/',
    'sky': 'http://twitch.tv/skymaybe'
}


class UserStat:
    def __init__(self):
        self.urlCounter = {}
        self.fname = join(user_data_dir(APPLICATION_NAME), STAT_FILE_NAME)

    def __open(self, mode):
        try:
            rv = open(self.fname, mode)
        except FileNotFoundError:
            rv = None
        except IOError as err:
            print("Can't open statistics: file {0}, error {1}".format(self.fname, err), file=stderr)
            rv = None
        return rv

    def load(self):
        f = self.__open('r')
        if f:
            self.urlCounter = load(f)

    def save(self):
        f = self.__open('w')
        if f:
            dump(self.urlCounter,f)

    def add_usage(self, url):
        if url in self.urlCounter:
            self.urlCounter[url] += 1
        else:
            self.urlCounter[url] = 0

    def print(self):
        pprint(self.urlCounter)


def assemble_command(arguments, statistics):
    streamer = arguments.streamer
    url = ''

    if match(streamer, 'absolute_URI'):
        url = streamer
        statistics.add_usage(url)
    elif streamer in nick_dict:
        url = nick_dict[streamer]
    else:
        print("nick", streamer, "is not defined yet", file=stderr)
        return 1

    statistics.save()
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
    cmdParser.add_argument('streamer', nargs='?', help="Streamer's nick name or URL of the stream")
    cmdParser.add_argument('mode', nargs='?', help='Video or audio only', choices=['audio', 'video'])
    group = cmdParser.add_mutually_exclusive_group()
    group.add_argument('-n', '--dry-run', help='Write the command string to stdout, but do not execute it',
                       action='store_true')
    group.add_argument('-s', '--stat', help='Print usage statistics and exit',
                       action='store_true')
    arguments = cmdParser.parse_args()

    rv = 0
    statistics = UserStat()
    statistics.load()
    if arguments.stat:
        statistics.print()
    else:
        rv = assemble_command(arguments, statistics)

    return rv


if __name__ == '__main__':
    launch_the_stream()
