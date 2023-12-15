import os

from pygemstones.io import file as f
from pygemstones.system import runner as r
from pygemstones.util import log as l

import modules.config as c


# -----------------------------------------------------------------------------
def get_pdfium_by_target(target, append_target_os=True, enable_v8=False):
    l.colored("Building PDFium...", l.YELLOW)

    build_dir = os.path.join("build", target)
    f.create_dir(build_dir)

    # remove old data
    l.colored("Removing old PDFium directory...", l.YELLOW)
    target_dir = os.path.join(build_dir, "pdfium")
    f.remove_dir(target_dir)

    # clone pdfium
    l.colored("Cloning PDFium with gclient...", l.YELLOW)
    config_args = [
        "gclient",
        "config",
        "--unmanaged",
        "https://pdfium.googlesource.com/pdfium.git",
    ]

    if not enable_v8:
        config_args.extend(["--custom-var", "checkout_configuration=minimal"])

    r.run(config_args, cwd=build_dir)

    # append target os
    if append_target_os:
        l.colored(
            "Appending target os ({}) to gclient file...".format(append_target_os),
            l.YELLOW,
        )
        gclient_file = os.path.join(build_dir, ".gclient")
        f.append_to_file(gclient_file, "target_os = [ '{}' ]".format(append_target_os))

    l.colored(f"Syncing repository with branch {c.pdfium_git_branch}...", l.YELLOW)
    r.run(
        [
            "gclient",
            "sync",
            "-r",
            f"origin/{c.pdfium_git_branch}",
            "--no-history",
            "--shallow",
        ],
        cwd=build_dir,
    )

    # reset and clean directories
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
