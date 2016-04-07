from json import load, dump
from operator import itemgetter
from os import makedirs
from os.path import join
from pprint import pformat
from appdirs import user_data_dir


class ApplicationLocalFile:
    def __init__(self, appname_, filename_):
        self.dir_name = user_data_dir(appname_, False)
        self.file_name = join(self.dir_name, filename_)

    def load(self):
        try:
            with open(self.file_name, 'r') as f:
                return load(f)
        except:
            pass

    def save(self, o):
        if o:
            makedirs(self.dir_name, exist_ok=True)
            with open(self.file_name, 'w+') as f:
                dump(o, f)

    def __str__(self):
        return pformat(self.dir_name, self.file_name)


class Nicknames(ApplicationLocalFile):
    def __init__(self, appname_, filename_):
        super().__init__(appname_, filename_)
        self.nick_dict = super().load()

    def find(self, nick):
        return nick in self.nick_dict

    def get(self, nick):
        if nick in self.nick_dict:
            return self.nick_dict[nick]
        else:
            return False

    def assign(self, nick, URL):
        self.nick_dict[nick] = URL

    def save(self):
        super().save(self.nick_dict)

    def __str__(self):
        return pformat(sorted(self.nick_dict.items()))


class UserStat(ApplicationLocalFile):
    def __init__(self, appname_, filename_):
        self.urlCounter = {}
        super().__init__(appname_, filename_)

    def add_usage(self, url):
        if url in self.urlCounter:
            self.urlCounter[url] += 1
        else:
            self.urlCounter[url] = 1

    def save(self):
        super().save(self.urlCounter)

    def load(self):
        self.urlCounter = super().load()

    def fltr(self, pred):
        before = len(self.urlCounter)
        self.urlCounter = {k: v for (k, v) in self.urlCounter.items() if pred(k, v)}
        return before - len(self.urlCounter)

    def __str__(self):
        if self.urlCounter:
            return pformat(sorted(self.urlCounter.items(),
                                  key=itemgetter(1),
                                  reverse=True))
        else:
            return '{}'