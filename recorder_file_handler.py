from datetime import date

def file_name_generator(alias):
    file_name_stem = alias + '.' + date.today().strftime('%Y.%m.%d')
    for i in range(1, 10):
        yield(file_name_stem + '.' + str(i) + '.ts')