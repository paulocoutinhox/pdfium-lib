import os
import subprocess

from pygemstones.io import file as f
from pygemstones.system import runner as r
from pygemstones.util import log as l

import modules.config as c


# -----------------------------------------------------------------------------
def run_task_build_depot_tools():
    l.colored("Building depot tools...", l.YELLOW)

    build_dir = os.path.join("build")
    f.create_dir(build_dir)

    tools_dir = os.path.join(build_dir, "depot-tools")
    f.remove_dir(tools_dir)

    cwd = build_dir
    command = [
        "git",
        "clone",
        "https://chromium.googlesource.com/chromium/tools/depot_tools.git",
        "depot-tools",
    ]
    r.run(command, cwd=cwd)

    l.colored("Execute on your terminal:", l.PURPLE)

    l.m("export PATH=$PATH:$PWD/build/depot-tools")
    l.colored("Or on Windows:", l.PURPLE)
    l.m("set PATH=%PATH%;{0}".format(os.path.abspath(tools_dir)))

    l.ok()


# -----------------------------------------------------------------------------
def run_task_build_emsdk():
    l.colored("Building Emscripten SDK...", l.YELLOW)

    build_dir = os.path.join("build")
    f.create_dir(build_dir)

    tools_dir = os.path.join(build_dir, "emsdk")
    f.remove_dir(tools_dir)

    cwd = build_dir
    command = [
        "git",
        "clone",
        "https://github.com/emscripten-core/emsdk.git",
    ]
    r.run(command, cwd=cwd)

    cwd = tools_dir
    command = " ".join(["./emsdk", "install", c.emsdk_version])
    r.run(command, cwd=cwd, shell=True)

    cwd = tools_dir
    command = " ".join(["./emsdk", "activate", c.emsdk_version])
    r.run(command, cwd=cwd, shell=True)

    cwd = tools_dir
    command = " ".join(["source", "emsdk_env.sh"])
    r.run(command, cwd=cwd, shell=True)

    l.ok()


# -----------------------------------------------------------------------------
def run_task_format():
    # check
    try:
        subprocess.check_output(["black", "--version"])
    except OSError:
        l.e("Black is not installed, check: https://github.com/psf/black")

    # start
    l.colored("Formating files...", l.YELLOW)

    # make.py
    command = [
        "black",
        "make.py",
    ]
    r.run(command)

    # modules
    command = [
        "black",
        "modules/",
    ]
    r.run(command)

    l.ok()
