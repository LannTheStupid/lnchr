from argparse import ArgumentParser
from sys import stderr
from subprocess import call
from pprint import pformat
from operator import itemgetter
from rfc3987 import match

from application_local_file import ApplicationLocalFile

APPLICATION_NAME = 'stream_launcher'
STAT_FILE_NAME = 'most_used.dat'
ALIAS_FILE_NAME = 'aliases.dat'

class Nicknames(ApplicationLocalFile):
    def __init__(self, filename_):
        super().__init__(APPLICATION_NAME, filename_)
        self.nick_dict = super().load()

    def find(self, nick):
        return nick in self.nick_dict

    def get(self, nick):
        if nick in self.nick_dict:
            return self.nick_dict[nick]
        else:
            return False

    def __str__(self):
        return pformat(sorted(self.nick_dict.items()))

class UserStat(ApplicationLocalFile):
    def __init__(self, filename_):
        self.urlCounter = {}
        super().__init__(APPLICATION_NAME, filename_)

    def add_usage(self, url):
        if url in self.urlCounter:
            self.urlCounter[url] += 1
        else:
            self.urlCounter[url] = 1

    def save_data(self):
        super().save(self.urlCounter)

    def load_data(self):
        self.urlCounter = super().load()

    def __str__(self):
        if self.urlCounter:
            return pformat(sorted(self.urlCounter.items(),
                                  key=itemgetter(1),
                                  reverse=True))
        else:
            return '{}'

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

    statistics.save_data()
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
    group.add_argument('-a', '--aliases', help='Print available aliases and exit',
                       action='store_true')
    arguments = cmdParser.parse_args()

    rv = 0
    statistics = UserStat(STAT_FILE_NAME)
    statistics.load_data()
    nicknames = Nicknames(ALIAS_FILE_NAME)
    nicknames.load()
    if arguments.stat:
        print(str(statistics))
    elif arguments.aliases:
        print(str(nicknames))
    else:
        rv = assemble_command(arguments, statistics, nicknames)

    return rv


if __name__ == '__main__':
    launch_the_stream()
