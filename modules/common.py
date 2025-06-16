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
        args.append("default_min_sdk_version=21")
        args.append("pdf_is_standalone=true")
        args.append("pdf_bundle_freetype=true")
    elif target_os == "ios":
        args.append("ios_enable_code_signing=false")
        args.append("use_blink=true")
        args.append("pdf_is_standalone=false")
        args.append("use_custom_libcxx=false")
        args.append('target_environment="{0}"'.format(target_environment))

        if enable_v8 and target_cpu == "arm64":
            args.append('arm_control_flow_integrity="none"')
        args.append("clang_use_chrome_plugins=false")

        # static lib
        if not shared:
            args.append("pdf_is_complete_lib=true")
    elif target_os == "linux":
        args.append("clang_use_chrome_plugins=false")
        args.append("pdf_is_standalone=true")
    elif target_os.startswith("mac"):
        args.append('mac_deployment_target="10.13.0"')
        args.append("clang_use_chrome_plugins=false")
        args.append("pdf_is_standalone=true")
        args.append("use_custom_libcxx=false")
        args.append("use_sysroot=false")
        args.append("use_allocator_shim=false")

        # static lib
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
