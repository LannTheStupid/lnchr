from json import load, dump
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