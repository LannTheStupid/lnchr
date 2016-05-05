from datetime import date
from pathlib import Path


def count_digits(n):
    if n < 1:
        return 1
    else:
        rv = 0
        while n > 0:
            rv += 1
            n //= 10
        return rv


def file_name_generator(alias, attempts = 10):
    file_name_stem = alias + '.' + date.today().strftime('%Y.%m.%d')
    digits = count_digits(attempts - 1)
    limit = 10 ** digits
    for i in range(1, limit):
        yield((file_name_stem + '.{:0>' + str(digits) + 'd}.ts').format(i))


# This generator guarantees that every returned full path points to the first
#   non-existent file in the name range defined by the number of attempts
def get_file_name(directory, alias, attempts = 10):
    for filename in file_name_generator(alias, attempts):
        full_file_name = Path(directory, filename)
        if full_file_name.is_file(): continue
        else:
            while True:
                yield str(full_file_name)
                if full_file_name.is_file():break
