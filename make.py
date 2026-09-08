#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Make tool

Usage:
  make.py <task-name>
  make.py [options]
  make.py -h | --help

Options:
  -h --help                         Show this screen.
  -d --debug                        Enable debug mode.
  --version                         Show version.

Examples:
  python3 make.py -h

Tasks:
  - format

  - build-depot-tools
  - build-emsdk

  - build-pdfium-ios
  - patch-ios
  - build-ios
  - install-ios
  - test-ios
  - archive-ios

  - build-pdfium-macos
  - patch-macos
  - build-macos
  - install-macos
  - test-macos
  - archive-macos

  - build-pdfium-linux
  - patch-linux
  - build-linux
  - install-linux
  - test-linux
  - archive-linux

  - build-pdfium-windows
  - patch-windows
  - build-windows
  - install-windows
  - test-windows
  - archive-windows

  - build-pdfium-android
  - patch-android
  - build-android
  - install-android
  - test-android
  - archive-android

  - build-pdfium-wasm
  - patch-wasm
  - build-wasm
  - install-wasm
  - test-wasm
  - test-wasmtime
  - generate-wasm
  - publish-wasm
  - publish-to-web-wasm
  - archive-wasm
"""

from docopt import docopt
from pygemstones.system import bootstrap as b
from pygemstones.util import log as l

import modules.android as android
import modules.common as common
import modules.config as c
import modules.ios as ios
import modules.linux as linux
import modules.macos as macos
import modules.wasm as wasm
import modules.windows as windows


def main(options):
    # Shows every option received when debug is on.
    if ("--debug" in options and options["--debug"]) or (
        "-d" in options and options["-d"]
    ):
        c.debug = True

    if c.debug:
        l.bold("You have executed with options:", l.YELLOW)
        l.m(str(options))
        l.nl()

    # Reads the task name from the options.
    if "<task-name>" in options:
        task = options["<task-name>"]

    # Rejects an empty task name.
    if not task:
        l.e("Task is invalid. Use 'python3 make.py -h' for help.")

    #######################
    # Common tasks.
    #######################

    # Formats the source files.
    if task == "format":
        common.run_task_format()

    # Clones the depot tools.
    elif task == "build-depot-tools":
        common.run_task_build_depot_tools()

    # Installs the Emscripten SDK.
    elif task == "build-emsdk":
        common.run_task_build_emsdk()

    #######################
    # Tasks for iOS.
    #######################

    # Clones and syncs pdfium for iOS.
    elif task == "build-pdfium-ios":
        ios.run_task_build_pdfium()

    # Patches the iOS checkout.
    elif task == "patch-ios":
        ios.run_task_patch()

    # Builds the iOS libraries.
    elif task == "build-ios":
        ios.run_task_build()

    # Stages the iOS libraries.
    elif task == "install-ios":
        ios.run_task_install()

    # Tests the iOS libraries.
    elif task == "test-ios":
        ios.run_task_test()

    # Archives the iOS libraries.
    elif task == "archive-ios":
        ios.run_task_archive()

    #######################
    # Tasks for macOS.
    #######################

    # Clones and syncs pdfium for macOS.
    elif task == "build-pdfium-macos":
        macos.run_task_build_pdfium()

    # Patches the macOS checkout.
    elif task == "patch-macos":
        macos.run_task_patch()

    # Builds the macOS libraries.
    elif task == "build-macos":
        macos.run_task_build()

    # Stages the macOS libraries.
    elif task == "install-macos":
        macos.run_task_install()

    # Tests the macOS libraries.
    elif task == "test-macos":
        macos.run_task_test()

    # Archives the macOS libraries.
    elif task == "archive-macos":
        macos.run_task_archive()

    #######################
    # Tasks for Linux.
    #######################

    # Clones and syncs pdfium for Linux.
    elif task == "build-pdfium-linux":
        linux.run_task_build_pdfium()

    # Patches the Linux checkout.
    elif task == "patch-linux":
        linux.run_task_patch()

    # Builds the Linux libraries.
    elif task == "build-linux":
        linux.run_task_build()

    # Stages the Linux libraries.
    elif task == "install-linux":
        linux.run_task_install()

    # Tests the Linux libraries.
    elif task == "test-linux":
        linux.run_task_test()

    # Archives the Linux libraries.
    elif task == "archive-linux":
        linux.run_task_archive()

    #######################
    # Tasks for Windows.
    #######################

    # Clones and syncs pdfium for Windows.
    elif task == "build-pdfium-windows":
        windows.run_task_build_pdfium()

    # Patches the Windows checkout.
    elif task == "patch-windows":
        windows.run_task_patch()

    # Builds the Windows libraries.
    elif task == "build-windows":
        windows.run_task_build()

    # Stages the Windows libraries.
    elif task == "install-windows":
        windows.run_task_install()

    # Tests the Windows libraries.
    elif task == "test-windows":
        windows.run_task_test()

    # Archives the Windows libraries.
    elif task == "archive-windows":
        windows.run_task_archive()

    #######################
    # Tasks for Android.
    #######################

    # Clones and syncs pdfium for Android.
    elif task == "build-pdfium-android":
        android.run_task_build_pdfium()

    # Patches the Android checkout.
    elif task == "patch-android":
        android.run_task_patch()

    # Builds the Android libraries.
    elif task == "build-android":
        android.run_task_build()

    # Stages the Android libraries.
    elif task == "install-android":
        android.run_task_install()

    # Tests the Android libraries.
    elif task == "test-android":
        android.run_task_test()

    # Archives the Android libraries.
    elif task == "archive-android":
        android.run_task_archive()

    #######################
    # Tasks for WASM.
    #######################

    # Clones and syncs pdfium for WASM.
    elif task == "build-pdfium-wasm":
        wasm.run_task_build_pdfium()

    # Patches the WASM checkout.
    elif task == "patch-wasm":
        wasm.run_task_patch()

    # Builds the WASM libraries.
    elif task == "build-wasm":
        wasm.run_task_build()

    # Stages the WASM libraries.
    elif task == "install-wasm":
        wasm.run_task_install()

    # Tests the WASM libraries.
    elif task == "test-wasm":
        wasm.run_task_test()

    # Tests the WASM libraries with wasmtime.
    elif task == "test-wasmtime":
        wasm.run_task_test_wasmtime()

    # Generates the WASM package.
    elif task == "generate-wasm":
        wasm.run_task_generate()

    # Publishes the WASM package.
    elif task == "publish-wasm":
        wasm.run_task_publish()

    # Publishes the WASM package to the web.
    elif task == "publish-to-web-wasm":
        wasm.run_task_publish_to_web()

    # Archives the WASM libraries.
    elif task == "archive-wasm":
        wasm.run_task_archive()

    #######################
    # Unknown task.
    #######################

    # Reports an unknown task.
    else:
        l.e("Task is invalid")


if __name__ == "__main__":
    # Initializes the environment.
    b.init()

    # Runs the command line interface.
    args = docopt(__doc__, version="2.0.0")
    main(args)
