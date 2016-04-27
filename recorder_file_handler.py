from datetime import date
from re import compile, match, findall
from pathlib import Path, PurePath

DEFAULT_ROOT_DIRECTORY = 'c:\\tmp'


def file_name_generator(alias):
    file_name_stem = alias + '.' + date.today().strftime('%Y.%m.%d')
    for i in range(1, 10):
        yield(file_name_stem + '.' + str(i) + '.ts')
