import os
from subprocess import check_call

import modules.config as c
import modules.functions as f


def run_task_build_pdfium():
    f.debug("Building PDFium...")

    for target in c.targets:
        build_dir = os.path.join("build", target)
        f.create_dir(build_dir)

        target_dir = os.path.join(build_dir, "pdfium")
        f.remove_dir(target_dir)

        cwd = build_dir
        command = " ".join(
            [
                "gclient",
                "config",
                "--unmanaged",
                "https://pdfium.googlesource.com/pdfium.git",
            ]
        )
        check_call(command, cwd=cwd, shell=True)

        cwd = build_dir
        command = " ".join(["gclient", "sync"])
        check_call(command, cwd=cwd, shell=True)

        cwd = target_dir
        command = " ".join(["git", "checkout", c.pdfium_git_commit])
        check_call(command, cwd=cwd, shell=True)


def run_task_build_depot_tools():
    f.debug("Building depot tools...")

    build_dir = os.path.join("build")
    f.create_dir(build_dir)

    tools_dir = os.path.join(build_dir, "depot-tools")
    f.remove_dir(tools_dir)

    cwd = build_dir
    command = " ".join(
        [
            "git",
            "clone",
            "https://chromium.googlesource.com/chromium/tools/depot_tools.git",
            "depot-tools",
        ]
    )
    check_call(command, cwd=cwd, shell=True)

    f.debug("Execute on your terminal: export PATH=$PATH:$PWD/build/depot-tools")


def run_task_format():
    f.debug("Formating...")

    # make.py
    command = " ".join(
        [
            "black",
            "make.py",
        ]
    )
    check_call(command, shell=True)

    # modules
    command = " ".join(
        [
            "black",
            "modules/",
        ]
    )
    check_call(command, shell=True)

    f.debug("Finished")
