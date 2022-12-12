import os


def check_dir(dir_path):
    if os.path.exists(dir_path) and os.path.isdir(dir_path) and os.access(dir_path, os.W_OK):
        return True
    else:
        return False


def check_file_existed(file_path):
    if os.path.exists(file_path):
        return True
    else:
        return False


def search_file(file_path, file_type):
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if os.path.splitext(file)[1] == file_type:
                return file
