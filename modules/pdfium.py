import os

from pygemstones.io import file as f
from pygemstones.system import runner as r
from pygemstones.system import platform as p
from pygemstones.util import log as l

import modules.config as c


# -----------------------------------------------------------------------------
def get_pdfium_by_target(target, append_target_os=None):
    need_use_shell = False

    if p.is_windows():
        need_use_shell = True

    l.colored("Building PDFium...", l.YELLOW)

    build_dir = os.path.join("build", target)
    f.create_dir(build_dir)

    l.colored("Removing old PDFium directory...", l.YELLOW)
    target_dir = os.path.join(build_dir, "pdfium")
    f.remove_dir(target_dir)

    l.colored("Cloning PDFium with gclient...", l.YELLOW)

    cwd = build_dir
    command = [
        "gclient",
        "config",
        "--unmanaged",
        "https://pdfium.googlesource.com/pdfium.git",
    ]
    r.run(command, cwd=cwd, shell=need_use_shell)

    if append_target_os:
        l.colored(
            "Appending target os ({0}) to gclient file...".format(append_target_os),
            l.YELLOW,
        )
        gclient_file = os.path.join(build_dir, ".gclient")
        f.append_to_file(gclient_file, "target_os = [ '{0}' ]".format(append_target_os))

    l.colored("Syncing repository with gclient...", l.YELLOW)

    cwd = build_dir
    command = ["gclient", "sync"]
    r.run(command, cwd=cwd, shell=need_use_shell)

    l.colored("Checkout to git commit {0}...".format(c.pdfium_git_commit), l.YELLOW)

    cwd = target_dir
    command = ["git", "checkout", c.pdfium_git_commit]
    r.run(command, cwd=cwd, shell=need_use_shell)

    l.ok()
