import os
import shutil
import subprocess
import time
import zipfile

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

    os.environ["DEPOT_TOOLS_UPDATE"] = "0"
    os.environ["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"

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

    l.colored(
        "Execute on your terminal the following file according to your system:",
        l.PURPLE,
    )
    l.m("File: emsdk_env")
    l.m("Directory: " + cwd)

    l.ok()


# -----------------------------------------------------------------------------
def run_task_format():
    # Requires black to be installed.
    try:
        subprocess.check_output(["black", "--version"])
    except OSError:
        l.e("Black is not installed, check: https://github.com/psf/black")

    l.colored("Formating files...", l.YELLOW)

    # Formats the entry point.
    command = [
        "black",
        "make.py",
    ]
    r.run(command)

    # Formats the modules.
    command = [
        "black",
        "modules/",
    ]
    r.run(command)

    l.ok()


# -----------------------------------------------------------------------------
# Packs directories into a zip file, keeping the unix modes and the symlinks.
def create_archive(output_filename, sources, keep=None):
    if os.path.exists(output_filename):
        os.remove(output_filename)

    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as archive:
        for source_dir, arcname in sources:
            for root, _, files in os.walk(source_dir):
                for name in sorted(files):
                    path = os.path.join(root, name)

                    if keep and not keep(path):
                        continue

                    entry = os.path.join(arcname, os.path.relpath(path, source_dir))
                    add_to_archive(archive, path, entry)


# -----------------------------------------------------------------------------
# Writes one file into an open archive, as a symlink when the source is one.
def add_to_archive(archive, path, entry):
    mode = os.lstat(path).st_mode
    info = zipfile.ZipInfo(entry, time.localtime(os.path.getmtime(path))[:6])
    info.external_attr = (mode & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED

    if os.path.islink(path):
        archive.writestr(info, os.readlink(path))
        return

    with open(path, "rb") as source, archive.open(info, "w") as target:
        shutil.copyfileobj(source, target)


# -----------------------------------------------------------------------------
def get_build_args(
    config,
    shared,
    target_os,
    target_cpu,
    target_environment=None,
    libc=None,
    enable_v8=False,
):
    args = []

    arg_is_debug = "true" if config == "debug" else "false"

    args.append(f"is_debug={arg_is_debug}")
    args.append("pdf_use_partition_alloc=false")
    args.append(f'target_cpu="{target_cpu}"')
    args.append(f'target_os="{target_os}"')
    args.append(f"pdf_enable_v8={str(enable_v8).lower()}")
    args.append(f"pdf_enable_xfa={str(enable_v8).lower()}")
    args.append("treat_warnings_as_errors=false")
    args.append("is_component_build=false")

    if config == "release":
        args.append("symbol_level=0")

    if enable_v8:
        args.append("v8_use_external_startup_data=false")
        args.append("v8_enable_i18n_support=false")

    if target_os == "android":
        args.append("clang_use_chrome_plugins=false")
        args.append("default_min_sdk_version=23")
        args.append("pdf_is_standalone=true")
        args.append("pdf_bundle_freetype=true")
    elif target_os == "ios":
        args.append("ios_enable_code_signing=false")
        args.append("use_blink=true")
        args.append("pdf_is_standalone=true")
        args.append("use_custom_libcxx=false")
        args.append('target_environment="{0}"'.format(target_environment))
        args.append('ios_deployment_target="12.0"')

        if enable_v8 and target_cpu == "arm64":
            args.append('arm_control_flow_integrity="none"')
        args.append("clang_use_chrome_plugins=false")

        # A static build needs the complete library.
        if not shared:
            args.append("pdf_is_complete_lib=true")
    elif target_os == "linux":
        args.append("clang_use_chrome_plugins=false")
        args.append("pdf_is_standalone=true")

        # The bundled libc++ never reaches a static library and its symbols carry the __Cr ABI namespace, which no system runtime provides.
        args.append("use_custom_libcxx=false")

        # A static build needs the complete library.
        if not shared:
            args.append("pdf_is_complete_lib=true")

            # Enabling lld makes the compiler emit crel relocations, which only binutils 2.44 and newer can read.
            # The published archive has to link with the GNU linker people already have.
            args.append("use_lld=false")
    elif target_os == "win":
        args.append("clang_use_chrome_plugins=false")
        args.append("pdf_is_standalone=true")
        args.append("use_custom_libcxx=false")

        # A static build needs the complete library.
        if not shared:
            args.append("pdf_is_complete_lib=true")
    elif target_os.startswith("mac"):
        args.append('mac_deployment_target="11.0.0"')
        args.append("clang_use_chrome_plugins=false")
        args.append("pdf_is_standalone=true")
        args.append("use_custom_libcxx=false")
        args.append("use_sysroot=false")
        args.append("use_allocator_shim=false")

        # A static build needs the complete library.
        if not shared:
            args.append("pdf_is_complete_lib=true")
    elif target_os.startswith("emscripten"):
        args.append("pdf_is_complete_lib=true")
        args.append("is_clang=false")
        args.append("use_custom_libcxx=false")

    if libc == "musl":
        args.append("is_musl=true")
        args.append("is_clang=false")
        args.append("use_custom_libcxx=false")

        if enable_v8:
            if target_cpu == "arm":
                args.append(
                    'v8_snapshot_toolchain="//build/toolchain/linux:clang_x86_v8_arm"'
                )
            elif target_cpu == "arm64":
                args.append(
                    'v8_snapshot_toolchain="//build/toolchain/linux:clang_x64_v8_arm64"'
                )
            else:
                args.append(
                    f'v8_snapshot_toolchain="//build/toolchain/linux:{target_cpu}"'
                )

    return args
