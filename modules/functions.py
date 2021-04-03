import glob
import os
import pwd
import shutil
import stat
import sys
import tarfile
import urllib.parse as urlparse
import urllib.request as urllib2
from subprocess import check_call
from distutils.dir_util import copy_tree

from slugify import slugify
from tqdm import tqdm


def debug(msg):
    print("> {0}".format(msg))


def message(msg):
    print("{0}".format(msg))


def error(msg):
    print("ERROR: {0}".format(msg))
    sys.exit(1)


def download_file(url, dest=None):
    """
    Download and save a file specified by url to dest directory,
    """
    u = urllib2.urlopen(url)

    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    filename = os.path.basename(path)

    if not filename:
        filename = "downloaded.file"

    if dest:
        filename = os.path.join(dest, filename)

    with open(filename, "wb") as f:
        debug("Downloading...")
        message("")

        meta = u.info()
        meta_func = meta.getheaders if hasattr(meta, "getheaders") else meta.get_all
        meta_length = meta_func("Content-Length")
        file_size = None
        pbar = None

        if meta_length:
            file_size = int(meta_length[0])

        if file_size:
            pbar = tqdm(total=file_size)

        file_size_dl = 0
        block_sz = 8192

        while True:
            dbuffer = u.read(block_sz)

            if not dbuffer:
                break

            dbuffer_len = len(dbuffer)
            file_size_dl += dbuffer_len
            f.write(dbuffer)

            if pbar:
                pbar.update(dbuffer_len)

        if pbar:
            pbar.close()
            message("")

        return filename


def get_download_filename(url):
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    filename = os.path.basename(path)

    if not filename:
        filename = "downloaded.file"

    return filename


def list_subdirs(from_path):
    dirs = filter(
        lambda x: os.path.isdir(os.path.join(from_path, x)), os.listdir(from_path)
    )
    return dirs


def remove_all_files(base_path, files_to_remove):
    for file_to_remove in files_to_remove:
        try:
            file_to_remove = os.path.join(base_path, file_to_remove)

            if os.path.isdir(file_to_remove):
                shutil.rmtree(file_to_remove)
            else:
                os.remove(file_to_remove)
        except IOError as e:
            # we will ignore this message, is not important now
            # debug('Error removing file: {0} - {1}'.format(file_to_remove, e.strerror))
            pass
        except OSError as e:
            # we will ignore this message, is not important now
            # debug('Error removing file: {0} - {1}'.format(file_to_remove, e.strerror))
            pass


def create_dir(dir_path):
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)


def remove_dir(dir_path):
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)


def remove_file(filename):
    if os.path.isfile(filename):
        os.remove(filename)


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def make_tarfile_from_list(output_filename, paths):
    tar = tarfile.open(output_filename, "w:gz")

    for item in paths:
        tar.add(item)

    tar.close()


def write_to_file(dirname, filename, content):
    full_file_path = os.path.join(dirname, filename)
    remove_file(full_file_path)
    create_dir(dirname)

    with open(full_file_path, "w") as f:
        f.write(content)
        f.close()


def find_files(directory, pattern):
    files = [
        f
        for (dir, subdirs, fs) in os.walk(directory)
        for f in fs
        if f.endswith(pattern)
    ]

    return files


def is_test_user():
    user = pwd.getpwuid(os.getuid())[0]
    return user == "paulo"


def file_has_content(file, content):
    with open(file) as f:
        if content in f.read():
            return True

    return False


def get_file_content(file):
    file = open(file, mode="r")
    content = file.read()
    file.close()
    return content


def prepend_to_file(file, content):
    file_content = content + "\n" + get_file_content(file)
    file_dest = open(file, "w")
    file_dest.write(file_content)
    file_dest.close()


def append_to_file(file, content):
    file_content = get_file_content(file) + "\n" + content
    file_dest = open(file, "w")
    file_dest.write(file_content)
    file_dest.close()


def replace_in_file(filename, old_string, new_string):
    with open(filename, encoding="utf-8") as f:
        s = f.read()
        if old_string not in s:
            # print('"{old_string}" not found in {filename}.'.format(**locals()))
            return

    # Safely write the changed content, if found in the file
    with open(filename, "w", encoding="utf-8") as f:
        # print('Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals()))
        s = s.replace(old_string, new_string)
        f.write(s)
        f.close()


def replace_line_in_file(filename, line, content):
    with open(filename) as f:
        lines = f.readlines()
        lines[line - 1] = content
        f.close()

        with open(filename, "w") as f:
            f.writelines(lines)
            f.close()


def get_file_line_content(filename, line):
    with open(filename) as f:
        lines = f.readlines()
        content = lines[line - 1]
        f.close()

        return content

    return None


def file_line_has_content(filename, line, content):
    line_content = get_file_line_content(filename, line)
    return line_content == content


def file_line_comment(filename, line, comment="#"):
    line_content = get_file_line_content(filename, line)

    if not line_content.startswith(comment):
        replace_line_in_file(filename, line, comment + line_content)


def file_line_comment_range(filename, line_start, line_end, comment="#"):
    for x in range(line_start, line_end + 1):
        file_line_comment(filename, x, comment)


def copy_all_inside(root_path, dst):
    create_dir(dst)
    copy_tree(root_path, dst, update=1)


def copy_dir(src, dst, symlinks=False, ignore=None, ignore_file=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)

    lst = os.listdir(src)

    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]

    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except:
                pass  # lchmod not available
        elif os.path.isdir(s):
            copy_dir(s, d, symlinks, ignore, ignore_file)
        else:
            if ignore_file is not None:
                ignored_file = ignore_file(s)
            else:
                ignored_file = False

            if not ignored_file:
                shutil.copy2(s, d)


def copy_file(from_path, to_path):
    create_dir(os.path.dirname(to_path))
    shutil.copyfile(from_path, to_path)


def copy_file2(from_path, to_path):
    create_dir(os.path.dirname(to_path))
    shutil.copy2(from_path, to_path)
