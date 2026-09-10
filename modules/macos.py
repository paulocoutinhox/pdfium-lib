import glob
import os

from pygemstones.io import file as f
from pygemstones.system import runner as r
from pygemstones.util import log as l

import modules.common as cm
import modules.config as c
import modules.patch as patch
import modules.pdfium as p


# -----------------------------------------------------------------------------
def run_task_build_pdfium():
    p.get_pdfium_by_target("macos")


# -----------------------------------------------------------------------------
def run_task_patch():
    l.colored("Patching files...", l.YELLOW)

    # Turns the library target into a shared one.
    if c.shared_lib_macos:
        patch.apply_shared_library("macos")

    # Removes the component build guards from the public headers.
    if c.shared_lib_macos:
        patch.apply_public_headers("macos")

    l.ok()


# -----------------------------------------------------------------------------
def run_task_build():
    l.colored("Building libraries...", l.YELLOW)

    current_dir = f.current_dir()

    # Walks every configuration.
    for config in c.configurations_macos:
        # Walks every target.
        for target in c.targets_macos:
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

            # Generates the ninja files.
            l.colored(
                'Generating files to arch "{0}" and configuration "{1}"...'.format(
                    target["target_cpu"], config
                ),
                l.YELLOW,
            )

            args = cm.get_build_args(
                config,
                c.shared_lib_macos,
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

            # Compiles the library.
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

    # Walks every configuration.
    for config in c.configurations_macos:
        f.recreate_dir(os.path.join("build", "macos", config))
        f.create_dir(os.path.join("build", "macos", config, "lib"))

        # Walks every target.
        for target in c.targets_macos:
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
                "libpdfium_{0}.a".format(target["target_cpu"]),
            )

            f.copy_file(source_lib_path, target_lib_path)

            # Rewrites the public includes so they resolve outside the checkout.
            source_include_path = os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "public",
            )

            headers = f.find_files(source_include_path, "*.h", True)

            for header in headers:
                f.replace_in_file(header, '#include "public/', '#include "../')

        # Merges the per architecture libraries into a universal one.
        folder = os.path.join("build", "macos", config, "lib", "*.a")
        files = glob.glob(folder)
        files_str = " ".join(files)
        lib_file_out = os.path.join("build", "macos", config, "lib", "libpdfium.a")

        l.colored("Merging libraries (lipo)...", l.YELLOW)
        command = ["lipo", "-create", files_str, "-o", lib_file_out]
        r.run(" ".join(command), shell=True)

        l.colored("File data...", l.YELLOW)
        command = ["file", lib_file_out]
        r.run(" ".join(command), shell=True)

        l.colored("File size...", l.YELLOW)
        command = ["ls", "-lh ", lib_file_out]
        r.run(" ".join(command), shell=True)

        # Copies the public headers.
        l.colored("Copying header files...", l.YELLOW)

        include_dir = os.path.join("build", "macos", "pdfium", "public")
        include_cpp_dir = os.path.join(include_dir, "cpp")
        target_include_dir = os.path.join("build", "macos", config, "include")
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

    # Walks every configuration.
    for config in c.configurations_macos:
        f.recreate_dir(build_dir)

        os.chdir(build_dir)

        cmake_config = config.capitalize()

        # Generates the sample project.
        command = [
            "cmake",
            "-DPDFIUM_CONFIG={0}".format(config),
            "-DCMAKE_BUILD_TYPE={0}".format(cmake_config),
            "../",
        ]
        r.run(command)

        # Builds the sample.
        command = ["cmake", "--build", ".", "--config", cmake_config]
        r.run(command)

        # Copies the assets the sample opens.
        f.copy_file(
            os.path.join(sample_dir, "assets", "f1.pdf"),
            os.path.join(build_dir, "f1.pdf"),
        )

        # Runs the sample.
        command = ["./sample"]
        r.run(command)

        # Returns to the starting directory.
        os.chdir(current_dir)

    l.ok()


# -----------------------------------------------------------------------------
# Drops the per architecture libraries that lipo already merged.
def keep_in_archive(path):
    name = os.path.basename(path)
    return "_" not in name or name.endswith(".h")


# -----------------------------------------------------------------------------
def run_task_archive():
    l.colored("Archiving...", l.YELLOW)

    current_dir = f.current_dir()
    lib_dir = os.path.join(current_dir, "build", "macos")
    output_filename = os.path.join(current_dir, "macos.zip")

    sources = [
        (os.path.join(lib_dir, configuration), configuration)
        for configuration in c.configurations_macos
    ]

    cm.create_archive(output_filename, sources, keep_in_archive)

    l.ok()
