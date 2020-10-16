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
  - build-pdfium

  - apply-patch-ios
  - build-ios
  - install-ios  
  - test-ios
  - archive-ios
  
  - apply-patch-macos
  - build-macos
  - install-macos
  - test-macos
  - archive-macos
"""

from docopt import docopt

import modules.common as common
import modules.functions as f
import modules.config as c
import modules.ios as ios
import modules.macos as macos


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

    # build pdfium
    elif make_task == "build-pdfium":
        common.run_task_build_pdfium()

    # apply patch ios
    elif make_task == "apply-patch-ios":
        ios.run_task_apply_patch()

    # build ios
    elif make_task == "build-ios":
        ios.run_task_build()

    # install ios
    elif make_task == "install-ios":
        ios.run_task_install()

    # test ios
    elif make_task == "test-ios":
        ios.run_task_test()

    # archive ios
    elif make_task == "archive-ios":
        ios.run_task_archive()

    # apply patch macos
    elif make_task == "apply-patch-macos":
        macos.run_task_apply_patch()

    # build macos
    elif make_task == "build-macos":
        macos.run_task_build()

    # install macos
    elif make_task == "install-macos":
        macos.run_task_install()

    # test macos
    elif make_task == "test-macos":
        macos.run_task_test()

    # archive macos
    elif make_task == "archive-macos":
        macos.run_task_archive()

    f.message("")
    f.debug("FINISHED!")


if __name__ == "__main__":
    # main CLI entrypoint
    args = docopt(__doc__, version="1.0.0")
    main(args)
