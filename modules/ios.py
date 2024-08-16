import glob
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
    p.get_pdfium_by_target("ios")


# -----------------------------------------------------------------------------
def run_task_patch():
    l.colored("Patching files...", l.YELLOW)

    source_dir = os.path.join("build", "ios", "pdfium")

    # shared lib
    if c.shared_lib_ios:
        patch.apply_shared_library("ios")

    # public headers
    patch.apply_public_headers("ios")

    # rules - test
    source_file = os.path.join(source_dir, "build", "config", "ios", "rules.gni")

    line_content = 'data_deps += [ "//testing/iossim" ]'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.replace_in_file(source_file, 'data_deps += [ "//testing/iossim" ]', "")
        l.bullet("Applied: rules - test", l.GREEN)
    else:
        l.bullet("Skipped: rules - test", l.PURPLE)

    # core fxge
    source_file = os.path.join(source_dir, "core", "fxge", "BUILD.gn")

    line_content = "if (is_mac) {"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = "  if (is_mac || is_ios) {"
        f.set_file_line_content(source_file, line_number, content, new_line=True)
        l.bullet("Applied: core fxge", l.GREEN)
    else:
        l.bullet("Skipped: core fxge", l.PURPLE)

    # ios automatically manage certs
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "ios",
        "ios_sdk_overrides.gni",
    )

    line_content = "if (is_ios) { ios_automatically_manage_certs = true }"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        content = "if (is_ios) { ios_automatically_manage_certs = true }"
        f.append_to_file(source_file, content)
        l.bullet("Applied: ios automatically manage certs", l.GREEN)
    else:
        l.bullet("Skipped: ios automatically manage certs", l.PURPLE)

    l.ok()


# -----------------------------------------------------------------------------
def run_task_build():
    l.colored("Building libraries...", l.YELLOW)

    current_dir = f.current_dir()

    # configs
    for config in c.configurations_ios:
        # targets
        for target in c.targets_ios:
            main_dir = os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "out",
                "{0}-{1}-{2}-{3}".format(
                    target["target_os"],
                    target["target_cpu"],
                    target["target_environment"],
                    config,
                ),
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

            args = cm.get_build_args(config, target["pdfium_os"], target["target_cpu"])
            args_str = " ".join(args)

            command = [
                "gn",
                "gen",
                "out/{0}-{1}-{2}-{3}".format(
                    target["target_os"],
                    target["target_cpu"],
                    target["target_environment"],
                    config,
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
                "out/{0}-{1}-{2}-{3}".format(
                    target["target_os"],
                    target["target_cpu"],
                    target["target_environment"],
                    config,
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
    for config in c.configurations_ios:
        f.recreate_dir(os.path.join("build", "ios", config))
        f.create_dir(os.path.join("build", "ios", config, "lib"))

        # targets
        for target in c.targets_ios:
            source_lib_path = os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "out",
                "{0}-{1}-{2}-{3}".format(
                    target["target_os"],
                    target["target_cpu"],
                    target["target_environment"],
                    config,
                ),
                "obj",
                "libpdfium.a",
            )

            target_lib_path = os.path.join(
                "build",
                target["target_os"],
                config,
                "lib",
                "libpdfium_{0}-{1}.a".format(
                    target["target_cpu"], target["target_environment"]
                ),
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

        # universal
        universal_libs = []
        for env in ["simulator", "device"]:
            folder = os.path.join("build", "ios", config, "lib", "*-{0}.a".format(env))
            files = glob.glob(folder)
            files_str = " ".join(files)
            f.create_dir(os.path.join("build", "ios", config, "lib", env))
            lib_file_out = os.path.join(
                "build", "ios", config, "lib", env, "libpdfium.a"
            )

            l.colored("Merging {0} libraries (lipo)...".format(env), l.YELLOW)
            command = ["lipo", "-create", files_str, "-o", lib_file_out]
            r.run(" ".join(command), shell=True)

            universal_libs.append(lib_file_out)

            l.colored("File data...", l.YELLOW)
            command = ["file", lib_file_out]
            r.run(" ".join(command), shell=True)

            l.colored("File size...", l.YELLOW)
            command = ["ls", "-lh ", lib_file_out]
            r.run(" ".join(command), shell=True)

        # headers
        l.colored("Copying header files...", l.YELLOW)

        include_dir = os.path.join("build", "ios", "pdfium", "public")
        include_cpp_dir = os.path.join(include_dir, "cpp")
        target_include_dir = os.path.join("build", "ios", config, "include")
        target_include_cpp_dir = os.path.join(target_include_dir, "cpp")

        f.recreate_dir(target_include_dir)
        f.copy_files(include_dir, target_include_dir, "*.h")
        f.copy_files(include_cpp_dir, target_include_cpp_dir, "*.h")

        # xcframework
        xcframework_out = os.path.join("build", "ios", config, "pdfium.xcframework")
        command = ["xcodebuild", "-create-xcframework"]

        for lib in universal_libs:
            command.append("-library")
            command.append(lib)
            command.append("-headers")
            command.append(target_include_dir)

        command.append("-output")
        command.append(xcframework_out)

        r.run(" ".join(command), shell=True)

    l.ok()


# -----------------------------------------------------------------------------
def run_task_test():
    l.colored("Testing...", l.YELLOW)

    for config in c.configurations_ios:
        for env in ["simulator", "device"]:
            lib_dir = os.path.join("build", "ios", config, "lib", env)
            command = ["file", os.path.join(lib_dir, "libpdfium.a")]
            r.run(command)

        framework_dir = os.path.join("build", "ios", config, "pdfium.xcframework")
        command = ["ls", "-lah", framework_dir]
        r.run(command)

    l.ok()


# -----------------------------------------------------------------------------
def run_task_archive():
    l.colored("Archiving...", l.YELLOW)

    current_dir = os.getcwd()
    lib_dir = os.path.join(current_dir, "build", "ios")
    output_filename = os.path.join(current_dir, "ios.tgz")

    tar = tarfile.open(output_filename, "w:gz")

    for configuration in c.configurations_ios:
        tar.add(
            name=os.path.join(lib_dir, configuration),
            arcname=os.path.basename(os.path.join(lib_dir, configuration)),
        )

    tar.close()

    l.ok()
