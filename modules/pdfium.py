import os
import sys

from pygemstones.io import file as f
from pygemstones.system import runner as r
from pygemstones.util import log as l

import modules.config as c


# -----------------------------------------------------------------------------
# Runs a gclient command, on any platform.
def run_gclient(args, cwd):
    # On windows gclient is a batch file, which cannot be started without a shell.
    if sys.platform == "win32":
        r.run(" ".join(args), cwd=cwd, shell=True)
    else:
        r.run(args, cwd=cwd)


# -----------------------------------------------------------------------------
def get_pdfium_by_target(target, append_target_os=True, enable_v8=False):
    l.colored("Building PDFium...", l.YELLOW)

    build_dir = os.path.join("build", target)
    f.create_dir(build_dir)

    # Removes the previous checkout.
    l.colored("Removing old PDFium directory...", l.YELLOW)
    target_dir = os.path.join(build_dir, "pdfium")
    f.remove_dir(target_dir)

    # Clones pdfium with gclient.
    l.colored("Cloning PDFium with gclient...", l.YELLOW)
    config_args = [
        "gclient",
        "config",
        "--unmanaged",
        "https://pdfium.googlesource.com/pdfium.git",
    ]

    if not enable_v8:
        config_args.extend(["--custom-var", "checkout_configuration=minimal"])

    run_gclient(config_args, build_dir)

    # Appends the target os to the gclient file.
    if append_target_os:
        l.colored(
            "Appending target os ({}) to gclient file...".format(target),
            l.YELLOW,
        )
        gclient_file = os.path.join(build_dir, ".gclient")
        f.append_to_file(gclient_file, "target_os = [ '{}' ]".format(target))

    l.colored(f"Syncing repository with branch {c.pdfium_git_branch}...", l.YELLOW)
    run_gclient(
        [
            "gclient",
            "sync",
            "-r",
            f"origin/{c.pdfium_git_branch}",
            "--no-history",
            "--shallow",
        ],
        build_dir,
    )

    # Reverts the directories a previous patch task may have changed.
    folders_to_reset = [
        "pdfium",
        "pdfium/build",
        "pdfium/third_party/libjpeg_turbo",
        "pdfium/base/allocator/partition_allocator",
    ]

    for folder in folders_to_reset:
        full_path = os.path.join(build_dir, folder)

        if os.path.exists(full_path):
            r.run(["git", "reset", "--hard"], cwd=full_path)
            r.run(["git", "clean", "-df"], cwd=full_path)

    l.ok()
