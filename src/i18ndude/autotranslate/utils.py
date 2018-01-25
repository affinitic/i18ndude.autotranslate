# encoding: utf-8
from os import remove
from shutil import move
from tempfile import mkstemp


def replace(source_file_path, pattern, substring, line_number):
    fh, target_file_path = mkstemp()
    match = False
    with open(target_file_path, 'w') as target_file:
        with open(source_file_path, 'r') as source_file:
            for count, line in enumerate(source_file):
                if pattern in line:
                    match = True
                target_file.write(line.replace(pattern, substring))
            source_file.close()
        target_file.close()
    remove(source_file_path)
    move(target_file_path, source_file_path)
    return match
