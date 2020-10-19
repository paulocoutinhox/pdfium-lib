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
  - format

  - build-depot-tools  
  
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
"""

from docopt import docopt

import modules.common as common
import modules.functions as f
import modules.config as c
import modules.ios as ios
import modules.macos as macos
import modules.android as android


def main(options):
    # show all params for debug
    if ("--debug" in options and options["--debug"]) or (
        "-d" in options and options["-d"]
    ):
        c.make_debug = True

    if c.make_debug:
        f.debug("You have executed with options:")
        f.message(str(options))
        f.message("")

    # bind options
    if "<task-name>" in options:
        make_task = options["<task-name>"]

    # validate data
    f.debug("Validating data...")

    # validate task
    if not make_task:
        f.error("Task is invalid")

    # build depot tools
    if make_task == "format":
        common.run_task_format()

    # build depot tools
    elif make_task == "build-depot-tools":
        common.run_task_build_depot_tools()

    #######################
    # iOS
    #######################

    # build pdfium - ios
    elif make_task == "build-pdfium-ios":
        ios.run_task_build_pdfium()

    # patch - ios
    elif make_task == "patch-ios":
        ios.run_task_patch()

    # build - ios
    elif make_task == "build-ios":
        ios.run_task_build()

    # install - ios
    elif make_task == "install-ios":
        ios.run_task_install()

    # test - ios
    elif make_task == "test-ios":
        ios.run_task_test()

    # archive - ios
    elif make_task == "archive-ios":
        ios.run_task_archive()

    #######################
    # macOS
    #######################

    # build pdfium - macos
    elif make_task == "build-pdfium-macos":
        macos.run_task_build_pdfium()

    # patch - macos
    elif make_task == "patch-macos":
        macos.run_task_patch()

    # build - macos
    elif make_task == "build-macos":
        macos.run_task_build()

    # install - macos
    elif make_task == "install-macos":
        macos.run_task_install()

    # test - macos
    elif make_task == "test-macos":
        macos.run_task_test()

    # archive - macos
    elif make_task == "archive-macos":
        macos.run_task_archive()

    #######################
    # Android
    #######################

    # build pdfium - android
    elif make_task == "build-pdfium-android":
        android.run_task_build_pdfium()

    # patch - android
    elif make_task == "patch-android":
        android.run_task_patch()

    # build - android
    elif make_task == "build-android":
        android.run_task_build()

    # install - android
    elif make_task == "install-android":
        android.run_task_install()

    # test - android
    elif make_task == "test-android":
        android.run_task_test()

    # archive - android
    elif make_task == "archive-android":
        android.run_task_archive()

    #######################
    # Invalid
    #######################

    # invalid
    else:
        f.error("Task is invalid")

    f.message("")
    f.debug("FINISHED!")


if __name__ == "__main__":
    # main CLI entrypoint
    args = docopt(__doc__, version="1.0.0")
    main(args)
