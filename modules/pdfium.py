import os

from pygemstones.io import file as f
from pygemstones.system import runner as r
from pygemstones.util import log as l

import modules.config as c


# -----------------------------------------------------------------------------
def get_pdfium_by_target(target):
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
    r.run(command, cwd=cwd)

    l.colored("Syncing repository with gclient...", l.YELLOW)

    cwd = build_dir
    command = ["gclient", "sync"]
    r.run(command, cwd=cwd)

    l.colored("Checkout to git commit {0}...".format(c.pdfium_git_commit), l.YELLOW)

    cwd = target_dir
    command = ["git", "checkout", c.pdfium_git_commit]
    r.run(command, cwd=cwd)

    l.ok()
