#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Make tool

Usage:
  make.py run <task-name>
  make.py [options]
  make.py -h | --help  

Options:
  -h --help                         Show this screen.
  -d --debug                        Enable debug mode.
  --version                         Show version.
  
Examples:
  python make.py -h

Tasks:
  - build-depot-tools
  - build-pdfium
  - apply-patch-ios
  - build-ios
  - install-ios
"""

import os
import shutil
import stat
import sys
import tarfile
import glob

from docopt import docopt
from slugify import slugify
from tqdm import tqdm

from subprocess import call, check_call
from shutil import copyfile, copytree

import urllib.request as urllib2
import urllib.parse as urlparse


def main(options):
    make_debug = False
    make_task = ""
    ios_archs = ["arm", "arm64", "x64"]
    ios_configurations = ["release"]  # debug

    # show all params for debug
    if ("--debug" in options and options["--debug"]) or (
        "-d" in options and options["-d"]
    ):
        make_debug = True

    if make_debug:
        debug("You have executed with options:")
        message(str(options))
        message("")

    # bind options
    if "<task-name>" in options:
        make_task = options["<task-name>"]

    # validate data
    debug("Validating data...")

    # validate task
    if not make_task:
        error("Task is invalid")

    # build depot tools
    if make_task == "build-depot-tools":
        run_task_build_depot_tools()

    # build pdfium
    elif make_task == "build-pdfium":
        run_task_build_pdfium()

    # apply patch ios
    elif make_task == "apply-patch-ios":
        run_task_apply_patch_ios()

    # install ios
    elif make_task == "install-ios":
        run_task_install_ios(ios_archs=ios_archs, ios_configurations=ios_configurations)

    # build ios
    elif make_task == "build-ios":
        run_task_build_ios(ios_archs=ios_archs, ios_configurations=ios_configurations)

    message("")
    debug("FINISHED!")


def run_task_build_pdfium():
    debug("Building PDFIUM...")

    remove_dir(os.path.join("pdfium"))

    command = " ".join(
        [
            "gclient",
            "config",
            "--unmanaged",
            "https://pdfium.googlesource.com/pdfium.git",
        ]
    )
    check_call(command, shell=True)

    command = " ".join(["gclient", "sync"])
    check_call(command, shell=True)

    cwd = "pdfium"
    command = " ".join(["git", "checkout", "f86f81aa33dabb615273492885aa9de76a6ccf68"])
    check_call(command, cwd=cwd, shell=True)


def run_task_apply_patch_ios():
    debug("Apply iOS patchs...")

    cwd = "pdfium"

    command = " ".join(["patch", "-p1", "--forward", "<", "../patchs/ios.patch"])
    call(command, cwd=cwd, shell=True)

    command = " ".join(
        [
            "patch",
            "-u",
            "build/config/mac/sdk_info.py",
            "--forward",
            "-i",
            "../patchs/sdk-info.patch",
        ]
    )
    call(command, cwd=cwd, shell=True)

    command = " ".join(
        [
            "patch",
            "-u",
            "build/mac/find_sdk.py",
            "--forward",
            "-i",
            "../patchs/find-sdk.patch",
        ]
    )
    call(command, cwd=cwd, shell=True)

    command = " ".join(
        [
            "patch",
            "-u",
            "build/toolchain/mac/filter_libtool.py",
            "--forward",
            "-i",
            "../patchs/filter-libtool.patch",
        ]
    )
    call(command, cwd=cwd, shell=True)

    command = " ".join(
        ["patch", "-u", "BUILD.gn", "--forward", "-i", "../patchs/build.patch"]
    )
    call(command, cwd=cwd, shell=True)

    command = " ".join(["patch", "-u", ".gn", "--forward", "-i", "../patchs/gn.patch"])
    call(command, cwd=cwd, shell=True)

    command = " ".join(
        [
            "patch",
            "-u",
            "build_overrides/build.gni",
            "--forward",
            "-i",
            "../patchs/build-override.patch",
        ]
    )
    call(command, cwd=cwd, shell=True)

    command = " ".join(
        [
            "patch",
            "-u",
            "third_party/libjpeg_turbo/BUILD.gn",
            "--forward",
            "-i",
            "../patchs/libjpeg-turbo.patch",
        ]
    )
    call(command, cwd=cwd, shell=True)


def run_task_build_depot_tools():
    debug("Building Depot Tools...")

    remove_dir("depot-tools")

    command = " ".join(
        [
            "git",
            "clone",
            "https://chromium.googlesource.com/chromium/tools/depot_tools.git",
            "depot-tools",
        ]
    )
    check_call(command, shell=True)

    debug("Execute on your terminal: export PATH=$PATH:$PWD/depot-tools")


def run_task_install_ios(ios_archs, ios_configurations):
    debug("Installing iOS libraries...")

    # configs
    for config in ios_configurations:
        remove_dir(os.path.join("build", "ios", config))
        create_dir(os.path.join("build", "ios", config))

        # archs
        for arch in ios_archs:
            folder = os.path.join(
                "pdfium", "out", "{0}-{1}".format(config, arch), "obj", "**", "*.a"
            )

            # skia_shared and pdfium_base have only a few object files and due to that there is no point in creating their own .a files.
            # we can link the .o files directly.
            skia_o = os.path.join(
                "pdfium",
                "out",
                "{0}-{1}".format(config, arch),
                "obj",
                "third_party",
                "skia_shared",
                "*.o",
            )

            base_o = os.path.join(
                "pdfium",
                "out",
                "{0}-{1}".format(config, arch),
                "obj",
                "third_party",
                "pdfium_base",
                "*.o",
            )

            files = glob.glob(folder, recursive=True)
            files.append(skia_o)
            files.append(base_o)

            files_str = " ".join(files)

            lib_file_out = os.path.join(
                "build", "ios", config, "libpdfium_{0}.a".format(arch)
            )

            # we have removed symbols to squeeze final results. -no_warning_for_no_symbols will save us from useless warnings.
            command = " ".join(
                [
                    "libtool",
                    "-static -no_warning_for_no_symbols",
                    files_str,
                    "-o",
                    lib_file_out,
                ]
            )

            check_call(command, shell=True)

        # universal
        folder = os.path.join("build", "ios", config, "*.a")
        files = glob.glob(folder)
        files_str = " ".join(files)
        lib_file_out = os.path.join("build", "ios", config, "libpdfium.a")

        command = " ".join(["lipo", "-create", files_str, "-o", lib_file_out])
        check_call(command, shell=True)

        command = " ".join(["file", lib_file_out])
        check_call(command, shell=True)

        command = " ".join(["ls", "-lh ", lib_file_out])
        check_call(command, shell=True)

        command = " ".join(
            ["nm", "-C ", lib_file_out, "|", "grep", "FPDF_CloseDocument"]
        )
        call(command, shell=True)

        # only to test in my machine
        # copyfile(lib_file_out, '/Users/paulo/Downloads/UXReader-iOS/UXReader/UXReader/PDFium/libpdfium.a')


def run_task_build_ios(ios_archs, ios_configurations):
    debug("Building iOS libraries...")

    current_dir = os.getcwd()

    # configs
    for config in ios_configurations:
        # archs
        for arch in ios_archs:
            main_dir = os.path.join("pdfium", "out", "{0}-{1}".format(config, arch))

            remove_dir(main_dir)
            create_dir(main_dir)

            os.chdir("pdfium")

            # generating files...
            debug(
                'Generating files to arch "{0}" and configuration "{1}"...'.format(
                    arch, config
                )
            )

            arg_is_debug = "true" if config == "debug" else "false"

            # adding symbol_level=0 will squeeze the final result significantly, but it is needed for debug builds.
            args = 'target_os="ios" ios_deployment_target="9.0" target_cpu="{0}" arm_use_neon=false use_goma=false is_debug={1} pdf_use_skia=false pdf_use_skia_paths=false pdf_enable_xfa=false pdf_enable_v8=false pdf_is_standalone=true is_component_build=false clang_use_chrome_plugins=false ios_enable_code_signing=false enable_ios_bitcode=true {2}'.format(
                arch, arg_is_debug, "symbol_level=0" if arg_is_debug else ""
            )

            command = " ".join(
                [
                    "gn",
                    "gen",
                    "out/{0}-{1}".format(config, arch),
                    "--args='{0}'".format(args),
                ]
            )

            check_call(command, shell=True)

            # compiling...
            debug(
                'Compiling to arch "{0}" and configuration "{1}"...'.format(
                    arch, config
                )
            )

            command = " ".join(
                ["ninja", "-C", "out/{0}-{1}".format(config, arch), "pdfium"]
            )

            check_call(command, shell=True)

            os.chdir(current_dir)


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


if __name__ == "__main__":
    # main CLI entrypoint
    args = docopt(__doc__, version="1.0.0")
    main(args)
