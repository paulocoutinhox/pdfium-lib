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
  
  - build-macos
  - install-macos

  - sample
"""

import os
import shutil
import stat
import sys
import tarfile
import glob
import pwd

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

    target_configurations = ["release"]  # release and/or debug

    targets_macos = [{"target_os": "mac", "target_cpu": "x64"}]

    targets_ios = [
        {"target_os": "ios", "target_cpu": "arm"},
        {"target_os": "ios", "target_cpu": "arm64"},
        {"target_os": "ios", "target_cpu": "x64"},
    ]

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

    # build ios
    elif make_task == "build-ios":
        run_task_build(targets=targets_ios, target_configurations=target_configurations)

    # install ios
    elif make_task == "install-ios":
        run_task_install_ios(
            targets=targets_ios, target_configurations=target_configurations
        )

    # build macos
    elif make_task == "build-macos":
        run_task_build(
            targets=targets_macos, target_configurations=target_configurations
        )

    # install macos
    elif make_task == "install-macos":
        run_task_install_macos(
            targets=targets_macos, target_configurations=target_configurations
        )

    # sample
    elif make_task == "sample":
        run_task_sample()

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
    command = " ".join(["git", "checkout", "7740980a8de4915c8c8e55966647b01ced4c39ef"])
    check_call(command, cwd=cwd, shell=True)


def run_task_apply_patch_ios():
    debug("Apply iOS patchs...")

    cwd = "pdfium"

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

    command = " ".join(
        [
            "patch",
            "-u",
            "core/fxge/BUILD.gn",
            "--forward",
            "-i",
            "../patchs/build-fxge.patch",
        ]
    )
    call(command, cwd=cwd, shell=True)

    command = " ".join(
        [
            "patch",
            "-u",
            "core/fxcrt/fx_system.h",
            "--forward",
            "-i",
            "../patchs/fx-system.patch",
        ]
    )
    call(command, cwd=cwd, shell=True)

    command = " ".join(
        [
            "patch",
            "-u",
            "core/fxge/apple/apple_int.h",
            "--forward",
            "-i",
            "../patchs/apple-int.patch",
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


def run_task_build(targets, target_configurations):
    debug("Building libraries...")

    current_dir = os.getcwd()

    # configs
    for config in target_configurations:

        # targets
        for target in targets:
            main_dir = os.path.join(
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            )

            remove_dir(main_dir)
            create_dir(main_dir)

            os.chdir("pdfium")

            # generating files...
            debug(
                'Generating files to arch "{0}" and configuration "{1}"...'.format(
                    target["target_cpu"], config
                )
            )

            arg_is_debug = "true" if config == "debug" else "false"

            # adding symbol_level=0 will squeeze the final result significantly, but it is needed for debug builds.
            args = []
            args.append('target_os="{0}"'.format(target["target_os"]))
            args.append('target_cpu="{0}"'.format(target["target_cpu"]))
            args.append("use_goma=false")
            args.append("is_debug={0}".format(arg_is_debug))
            args.append("pdf_use_skia=false")
            args.append("pdf_use_skia_paths=false")
            args.append("pdf_enable_xfa=false")
            args.append("pdf_enable_v8=false")
            args.append("pdf_is_standalone=false")
            args.append("is_component_build=false")
            args.append("clang_use_chrome_plugins=false")

            if target["target_os"] == "ios":
                args.append('ios_deployment_target="9.0"')
                args.append("ios_enable_code_signing=false")

                if target["target_cpu"] == "x64":
                    args.append("arm_use_neon=true")
                elif target["target_cpu"] == "arm":
                    args.append("arm_use_neon=false")
                    args.append("enable_ios_bitcode=true")
                elif target["target_cpu"] == "arm64":
                    args.append("arm_use_neon=true")
                    args.append("enable_ios_bitcode=true")

            if config == "release":
                args.append("symbol_level=0")

            args_str = " ".join(args)

            command = " ".join(
                [
                    "gn",
                    "gen",
                    "out/{0}-{1}-{2}".format(
                        config, target["target_os"], target["target_cpu"]
                    ),
                    "--args='{0}'".format(args_str),
                ]
            )

            check_call(command, shell=True)

            # compiling...
            debug(
                'Compiling to arch "{0}" and configuration "{1}"...'.format(
                    target["target_cpu"], config
                )
            )

            command = " ".join(
                [
                    "ninja",
                    "-C",
                    "out/{0}-{1}-{2}".format(
                        config, target["target_os"], target["target_cpu"]
                    ),
                    "pdfium",
                ]
            )

            check_call(command, shell=True)

            os.chdir(current_dir)


def run_task_install_ios(targets, target_configurations):
    debug("Installing libraries...")

    # configs
    for config in target_configurations:
        remove_dir(os.path.join("build", "ios", config))
        create_dir(os.path.join("build", "ios", config))

        # targets
        for target in targets:
            files = get_compiled_files(config, target)

            files_str = " ".join(files)

            lib_file_out = os.path.join(
                "build", "ios", config, "libpdfium_{0}.a".format(target["target_cpu"])
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

        debug("Merging libraries (lipo)...")
        command = " ".join(["lipo", "-create", files_str, "-o", lib_file_out])
        check_call(command, shell=True)

        debug("File data...")
        command = " ".join(["file", lib_file_out])
        check_call(command, shell=True)

        debug("File size...")
        command = " ".join(["ls", "-lh ", lib_file_out])
        check_call(command, shell=True)

        # debug("Library symbols...")
        # command = " ".join(
        #     ["nm", "-C ", lib_file_out, "|", "grep", "FPDF_CloseDocument"]
        # )
        # call(command, shell=True)

        # only to test in my machine
        if is_test_user():
            copyfile(
                lib_file_out,
                "/Users/paulo/Downloads/PDFiumTest/PDFiumTest/libpdfium/lib/libpdfium.a",
            )


def run_task_install_macos(targets, target_configurations):
    debug("Installing libraries...")

    # configs
    for config in target_configurations:
        remove_dir(os.path.join("build", "macos", config))
        create_dir(os.path.join("build", "macos", config))

        # targets
        for target in targets:
            files = get_compiled_files(config, target)

            files_str = " ".join(files)

            lib_file_out = os.path.join(
                "build", "macos", config, "libpdfium_{0}.a".format(target["target_cpu"])
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
        folder = os.path.join("build", "macos", config, "*.a")
        files = glob.glob(folder)
        files_str = " ".join(files)
        lib_file_out = os.path.join("build", "macos", config, "libpdfium.a")

        debug("Merging libraries (lipo)...")
        command = " ".join(["lipo", "-create", files_str, "-o", lib_file_out])
        check_call(command, shell=True)

        debug("File data...")
        command = " ".join(["file", lib_file_out])
        check_call(command, shell=True)

        debug("File size...")
        command = " ".join(["ls", "-lh ", lib_file_out])
        check_call(command, shell=True)

        # debug("Library symbols...")
        # command = " ".join(
        #     ["nm", "-C ", lib_file_out, "|", "grep", "FPDF_CloseDocument"]
        # )
        # call(command, shell=True)


def run_task_sample():
    debug("Building sample...")

    current_dir = os.getcwd()
    sample_dir = os.path.join(current_dir, "sample")
    build_dir = os.path.join(sample_dir, "build")

    remove_dir(build_dir)
    create_dir(build_dir)

    os.chdir(build_dir)

    # generate project
    command = " ".join(["cmake", "../"])

    check_call(command, shell=True)

    # build
    command = " ".join(["cmake", "--build", "."])
    check_call(command, shell=True)

    # copy assets
    copyfile(
        os.path.join(sample_dir, "assets", "f2.pdf"), os.path.join(build_dir, "f1.pdf")
    )

    # run
    command = " ".join(["./sample"])
    check_call(command, shell=True)

    # finish
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


def is_test_user():
    user = pwd.getpwuid(os.getuid())[0]
    return user == "paulo"


def get_compiled_files(config, target):
    folder = os.path.join(
        "pdfium",
        "out",
        "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
        "obj",
        "**",
        "*.a",
    )

    files = glob.glob(folder, recursive=True)

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdftext",
            "fpdftext",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fxcrt",
            "fxcrt",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfapi",
            "page",
            "page",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfapi",
            "render",
            "render",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfapi",
            "parser",
            "parser",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfapi",
            "edit",
            "edit",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfapi",
            "cmaps",
            "cmaps",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfapi",
            "font",
            "font",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfdoc",
            "fpdfdoc",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fxcodec",
            "fxcodec",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fxge",
            "fxge",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fdrm",
            "fdrm",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "fxjs",
            "fxjs",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "fpdfsdk",
            "pwl",
            "pwl",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "fpdfsdk",
            "formfiller",
            "formfiller",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "fpdfsdk",
            "fpdfsdk",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "fx_freetype",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "fx_agg",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "skia_shared",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "pdfium_base",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "fx_lcms2",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "fx_libopenjpeg",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "zlib",
            "zlib_x86_simd",
            "*.o",
        )
    )

    if target["target_os"] == "ios":
        if target["target_cpu"] == "arm64":
            files.append(
                os.path.join(
                    "pdfium",
                    "out",
                    "{0}-{1}-{2}".format(
                        config, target["target_os"], target["target_cpu"]
                    ),
                    "obj",
                    "third_party",
                    "zlib",
                    "zlib_adler32_simd",
                    "*.o",
                )
            )

            files.append(
                os.path.join(
                    "pdfium",
                    "out",
                    "{0}-{1}-{2}".format(
                        config, target["target_os"], target["target_cpu"]
                    ),
                    "obj",
                    "third_party",
                    "zlib",
                    "zlib_inflate_chunk_simd",
                    "*.o",
                )
            )

    if target["target_os"] == "mac":
        files.append(
            os.path.join(
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
                "obj",
                "buildtools",
                "third_party",
                "libc++abi",
                "libc++abi",
                "*.o",
            )
        )

        files.append(
            os.path.join(
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
                "obj",
                "third_party",
                "yasm",
                "yasm",
                "*.o",
            )
        )

        files.append(
            os.path.join(
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
                "obj",
                "third_party",
                "yasm",
                "genstring",
                "*.o",
            )
        )

        files.append(
            os.path.join(
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
                "obj",
                "third_party",
                "yasm",
                "genperf",
                "*.o",
            )
        )

        files.append(
            os.path.join(
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
                "obj",
                "third_party",
                "yasm",
                "re2c",
                "*.o",
            )
        )

        files.append(
            os.path.join(
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
                "obj",
                "third_party",
                "yasm",
                "genmacro",
                "*.o",
            )
        )

        files.append(
            os.path.join(
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
                "obj",
                "third_party",
                "zlib",
                "zlib_inflate_chunk_simd",
                "*.o",
            )
        )

        files.append(
            os.path.join(
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
                "obj",
                "third_party",
                "zlib",
                "zlib_crc32_simd",
                "*.o",
            )
        )

        files.append(
            os.path.join(
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
                "obj",
                "third_party",
                "zlib",
                "zlib_adler32_simd",
                "*.o",
            )
        )

    return files


if __name__ == "__main__":
    # main CLI entrypoint
    args = docopt(__doc__, version="1.0.0")
    main(args)
