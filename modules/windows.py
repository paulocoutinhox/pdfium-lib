import glob
import os
import tarfile

from pygemstones.io import file as f
from pygemstones.system import runner as r
from pygemstones.util import log as l

import modules.config as c
import modules.pdfium as p


# -----------------------------------------------------------------------------
def run_task_build_pdfium():
    p.get_pdfium_by_target("windows")


# -----------------------------------------------------------------------------
def run_task_patch():
    l.colored("Patching files...", l.YELLOW)

    source_dir = os.path.join("build", "windows", "pdfium")

    # shared library
    source_file = os.path.join(source_dir, "BUILD.gn")

    line_content = 'component("pdfium") {'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.replace_in_file(
            source_file, 'component("pdfium") {', 'shared_library("pdfium") {'
        )
        l.bullet("Applied: shared library", l.GREEN)
    else:
        l.bullet("Skipped: shared library", l.PURPLE)

    l.ok()


# -----------------------------------------------------------------------------
def run_task_build():
    l.colored("Building libraries...", l.YELLOW)

    current_dir = f.current_dir()

    # configs
    for config in c.configurations_windows:
        # targets
        for target in c.targets_windows:
            main_dir = os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(target["target_os"], target["target_cpu"], config),
            )

            f.recreate_dir(main_dir)

            os.chdir(
                os.path.join(
                    "build",
                    target["target_os"],
                    "pdfium",
                )
            )

            # generating files...
            l.colored(
                'Generating files to arch "{0}" and configuration "{1}"...'.format(
                    target["target_cpu"], config
                ),
                l.YELLOW,
            )

            arg_is_debug = "true" if config == "debug" else "false"

            args = []
            args.append('target_os=\\"{0}\\"'.format(target["pdfium_os"]))
            args.append('target_cpu=\\"{0}\\"'.format(target["target_cpu"]))
            args.append("use_goma=false")
            args.append("is_debug={0}".format(arg_is_debug))
            args.append("treat_warnings_as_errors=false")
            args.append("pdf_use_skia=false")
            args.append("pdf_enable_xfa=false")
            args.append("pdf_enable_v8=false")
            args.append("pdf_is_standalone=true")
            args.append("is_component_build=false")

            if config == "release":
                args.append("symbol_level=0")

            args_str = " ".join(args)

            command = [
                "gn",
                "gen",
                os.path.join(
                    "out",
                    "{0}-{1}-{2}".format(
                        target["target_os"], target["target_cpu"], config
                    ),
                ),
                '--args="{0}"'.format(args_str),
            ]
            r.run(" ".join(command), shell=True)

            # compiling...
            l.colored(
                'Compiling to arch "{0}" and configuration "{1}"...'.format(
                    target["target_cpu"], config
                ),
                l.YELLOW,
            )

            command = [
                "ninja",
                "-C",
                os.path.join(
                    "out",
                    "{0}-{1}-{2}".format(
                        target["target_os"], target["target_cpu"], config
                    ),
                ),
                "pdfium",
                "-v",
            ]
            r.run(command, shell=True)

            os.chdir(current_dir)

    l.ok()


# -----------------------------------------------------------------------------
def run_task_install():
    l.colored("Installing libraries...", l.YELLOW)

    # configs
    for config in c.configurations_windows:
        f.recreate_dir(os.path.join("build", "windows", config))
        f.create_dir(os.path.join("build", "windows", config, "lib"))

        # targets
        for target in c.targets_windows:
            # dll
            source_lib_path = os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(target["target_os"], target["target_cpu"], config),
                "pdfium.dll",
            )

            target_lib_path = os.path.join(
                "build",
                target["target_os"],
                config,
                "lib",
                target["target_cpu"],
                "pdfium.dll",
            )

            f.copy_file(source_lib_path, target_lib_path)

            # pdb
            source_lib_path = os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(target["target_os"], target["target_cpu"], config),
                "pdfium.dll.pdb",
            )

            target_lib_path = os.path.join(
                "build",
                target["target_os"],
                config,
                "lib",
                target["target_cpu"],
                "pdfium.dll.pdb",
            )

            f.copy_file(source_lib_path, target_lib_path)

            # lib
            source_lib_path = os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(target["target_os"], target["target_cpu"], config),
                "pdfium.dll.lib",
            )

            target_lib_path = os.path.join(
                "build",
                target["target_os"],
                config,
                "lib",
                target["target_cpu"],
                "pdfium.dll.lib",
            )

            f.copy_file(source_lib_path, target_lib_path)

            # fix include path
            source_include_path = os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "public",
            )

            headers = f.find_files(source_include_path, "*.h", True)

            for header in headers:
                f.replace_in_file(header, '#include "public/', '#include "../')

        # headers
        l.colored("Copying header files...", l.YELLOW)

        include_dir = os.path.join("build", "windows", "pdfium", "public")
        include_cpp_dir = os.path.join(include_dir, "cpp")
        target_include_dir = os.path.join("build", "windows", config, "include")
        target_include_cpp_dir = os.path.join(target_include_dir, "cpp")

        f.recreate_dir(target_include_dir)
        f.copy_files(include_dir, target_include_dir, "*.h")
        f.copy_files(include_cpp_dir, target_include_cpp_dir, "*.h")

    l.ok()


# -----------------------------------------------------------------------------
def run_task_test():
    l.colored("Testing...", l.YELLOW)

    current_dir = os.getcwd()
    sample_dir = os.path.join(current_dir, "sample")
    build_dir = os.path.join(sample_dir, "build")

    f.recreate_dir(build_dir)

    os.chdir(build_dir)

    # generate project
    command = ["cmake", "../"]
    r.run(command)

    # build
    command = ["cmake", "--build", "."]
    r.run(command)

    # copy assets
    f.copy_file(
        os.path.join(sample_dir, "assets", "f1.pdf"),
        os.path.join(build_dir, "f1.pdf"),
    )

    # run
    command = ["./sample"]
    r.run(command)

    # finish
    os.chdir(current_dir)

    l.ok()


# -----------------------------------------------------------------------------
def run_task_archive():
    l.colored("Archiving...", l.YELLOW)

    current_dir = f.current_dir()
    lib_dir = os.path.join(current_dir, "build", "windows")
    output_filename = os.path.join(current_dir, "windows.tgz")

    tar = tarfile.open(output_filename, "w:gz")

    for configuration in c.configurations_windows:
        tar.add(
            name=os.path.join(lib_dir, configuration),
            arcname=os.path.basename(os.path.join(lib_dir, configuration)),
            filter=lambda x: (
                None if "_" in x.name and not x.name.endswith(".h") else x
            ),
        )

    tar.close()

    l.ok()
