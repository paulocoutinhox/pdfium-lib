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
import modules.macos as macos
import modules.wasm as wasm


def main(options):
    # show all params for debug
    if ("--debug" in options and options["--debug"]) or (
        "-d" in options and options["-d"]
    ):
        c.debug = True

    if c.debug:
        l.bold("You have executed with options:", l.YELLOW)
        l.m(str(options))
        l.nl()

    # bind options
    if "<task-name>" in options:
        task = options["<task-name>"]

    # validate task
    if not task:
        l.e("Task is invalid. Use 'python3 make.py -h' for help.")

    #######################
    # Common
    #######################

    # format
    if task == "format":
        common.run_task_format()

    # build depot tools
    elif task == "build-depot-tools":
        common.run_task_build_depot_tools()

    # build emsdk
    elif task == "build-emsdk":
        common.run_task_build_emsdk()

    #######################
    # iOS
    #######################

    # build pdfium - ios
    elif task == "build-pdfium-ios":
        ios.run_task_build_pdfium()

    # patch - ios
    elif task == "patch-ios":
        ios.run_task_patch()

    # build - ios
    elif task == "build-ios":
        ios.run_task_build()

    # install - ios
    elif task == "install-ios":
        ios.run_task_install()

    # test - ios
    elif task == "test-ios":
        ios.run_task_test()

    # archive - ios
    elif task == "archive-ios":
        ios.run_task_archive()

    #######################
    # macOS
    #######################

    # build pdfium - macos
    elif task == "build-pdfium-macos":
        macos.run_task_build_pdfium()

    # patch - macos
    elif task == "patch-macos":
        macos.run_task_patch()

    # build - macos
    elif task == "build-macos":
        macos.run_task_build()

    # install - macos
    elif task == "install-macos":
        macos.run_task_install()

    # test - macos
    elif task == "test-macos":
        macos.run_task_test()

    # archive - macos
    elif task == "archive-macos":
        macos.run_task_archive()

    #######################
    # Android
    #######################

    # build pdfium - android
    elif task == "build-pdfium-android":
        android.run_task_build_pdfium()

    # patch - android
    elif task == "patch-android":
        android.run_task_patch()

    # build - android
    elif task == "build-android":
        android.run_task_build()

    # install - android
    elif task == "install-android":
        android.run_task_install()

    # test - android
    elif task == "test-android":
        android.run_task_test()

    # archive - android
    elif task == "archive-android":
        android.run_task_archive()

    #######################
    # WASM
    #######################

    # build pdfium - wasm
    elif task == "build-pdfium-wasm":
        wasm.run_task_build_pdfium()

    # patch - wasm
    elif task == "patch-wasm":
        wasm.run_task_patch()

    # build - wasm
    elif task == "build-wasm":
        wasm.run_task_build()

    # install - wasm
    elif task == "install-wasm":
        wasm.run_task_install()

    # test - wasm
    elif task == "test-wasm":
        wasm.run_task_test()

    # generate - wasm
    elif task == "generate-wasm":
        wasm.run_task_generate()

    # publish - wasm
    elif task == "publish-wasm":
        wasm.run_task_publish()

    # publish to web - wasm
    elif task == "publish-to-web-wasm":
        wasm.run_task_publish_to_web()

    # archive - wasm
    elif task == "archive-wasm":
        wasm.run_task_archive()

    #######################
    # Invalid
    #######################

    # invalid
    else:
        l.e("Task is invalid")


if __name__ == "__main__":
    # initialization
    b.init()

    # main CLI entrypoint
    args = docopt(__doc__, version="2.0.0")
    main(args)
