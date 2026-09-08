import os
import tarfile

from pygemstones.io import file as f
from pygemstones.system import runner as r
from pygemstones.util import log as l

import modules.common as cm
import modules.config as c
import modules.patch as patch
import modules.pdfium as p


# -----------------------------------------------------------------------------
def run_task_build_pdfium():
    p.get_pdfium_by_target("linux")


# -----------------------------------------------------------------------------
def run_task_patch():
    l.colored("Patching files...", l.YELLOW)

    # shared lib
    if c.shared_lib_linux:
        patch.apply_shared_library("linux")

    # public headers
    if c.shared_lib_linux:
        patch.apply_public_headers("linux")

    l.ok()


# -----------------------------------------------------------------------------
def run_task_build():
    l.colored("Building libraries...", l.YELLOW)

    current_dir = f.current_dir()

    # configs
    for config in c.configurations_linux:
        # targets
        for target in c.targets_linux:
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

            args = cm.get_build_args(
                config,
                c.shared_lib_linux,
                target["pdfium_os"],
                target["target_cpu"],
            )

            args_str = " ".join(args)

            command = [
                "gn",
                "gen",
                "out/{0}-{1}-{2}".format(
                    target["target_os"], target["target_cpu"], config
                ),
                "--args='{0}'".format(args_str),
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
                "out/{0}-{1}-{2}".format(
                    target["target_os"], target["target_cpu"], config
                ),
                "pdfium",
                "-v",
            ]
            r.run(command)

            os.chdir(current_dir)

    l.ok()


# -----------------------------------------------------------------------------
def run_task_install():
    l.colored("Installing libraries...", l.YELLOW)

    # configs
    for config in c.configurations_linux:
        f.recreate_dir(os.path.join("build", "linux", config))
        f.create_dir(os.path.join("build", "linux", config, "lib"))

        # targets
        for target in c.targets_linux:
            source_lib_path = os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(target["target_os"], target["target_cpu"], config),
                "obj",
                "libpdfium.a",
            )

            target_lib_path = os.path.join(
                "build",
                target["target_os"],
                config,
                "lib",
                target["target_cpu"],
                "libpdfium.a",
            )

            f.copy_file(source_lib_path, target_lib_path)

            l.colored("File data...", l.YELLOW)
            command = ["file", target_lib_path]
            r.run(" ".join(command), shell=True)

            l.colored("File size...", l.YELLOW)
            command = ["ls", "-lh", target_lib_path]
            r.run(" ".join(command), shell=True)

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

        include_dir = os.path.join("build", "linux", "pdfium", "public")
        include_cpp_dir = os.path.join(include_dir, "cpp")
        target_include_dir = os.path.join("build", "linux", config, "include")
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

    # configs
    for config in c.configurations_linux:
        f.recreate_dir(build_dir)

        os.chdir(build_dir)

        cmake_config = config.capitalize()

        # generate project
        command = [
            "cmake",
            "-DPDFIUM_CONFIG={0}".format(config),
            "-DCMAKE_BUILD_TYPE={0}".format(cmake_config),
            "../",
        ]
        r.run(command)

        # build
        command = ["cmake", "--build", ".", "--config", cmake_config]
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
    lib_dir = os.path.join(current_dir, "build", "linux")
    output_filename = os.path.join(current_dir, "linux.tgz")

    tar = tarfile.open(output_filename, "w:gz")

    for configuration in c.configurations_linux:
        tar.add(
            name=os.path.join(lib_dir, configuration),
            arcname=os.path.basename(os.path.join(lib_dir, configuration)),
        )

    tar.close()

    l.ok()
