from argparse import ArgumentParser
from os import makedirs
from sys import stderr
from subprocess import call
from pprint import pformat
from os.path import join
from json import load, dump
from operator import itemgetter

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
    'sky': 'http://twitch.tv/skymaybe',
    'J': 'http://twitch.tv/entropicJ',
    'paniko': 'http://twitch.tv/pani_ko'
}


class UserStat:
    def __init__(self):
        self.urlCounter = {}
        self.dirname = user_data_dir(APPLICATION_NAME, False)
        self.fname = join(self.dirname, STAT_FILE_NAME)

    def load(self):
        try:
            with open(self.fname, 'r') as f:
                self.urlCounter = load(f)
        except:
            pass

    def save(self):
        if self.urlCounter:
            makedirs(self.dirname, exist_ok=True)
            with open(self.fname, 'w+') as f:
                dump(self.urlCounter, f)

    def add_usage(self, url):
        if url in self.urlCounter:
            self.urlCounter[url] += 1
        else:
            self.urlCounter[url] = 1

    def toString(self):
        return pformat(sorted(self.urlCounter.items(),
                              key=itemgetter(1),
                              reverse=True))


def assemble_command(arguments, statistics):
    streamer = arguments.streamer

    if match(streamer, 'absolute_URI'):
        url = streamer
        statistics.add_usage(url)
    elif streamer in nick_dict:
        url = nick_dict[streamer]
    else:
        print("nick", streamer, "is not defined yet", file=stderr)
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
        print(statistics.toString())
    else:
        rv = assemble_command(arguments, statistics)

    return rv


if __name__ == '__main__':
    launch_the_stream()
