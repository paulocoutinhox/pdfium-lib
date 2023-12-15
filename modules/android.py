import os
import tarfile

from pygemstones.io import file as f
from pygemstones.system import runner as r
from pygemstones.util import log as l

import modules.config as c
import modules.pdfium as p


# -----------------------------------------------------------------------------
def run_task_build_pdfium():
    p.get_pdfium_by_target("android", "android")


# -----------------------------------------------------------------------------
def run_task_patch():
    l.colored("Patching files...", l.YELLOW)

    source_dir = os.path.join("build", "android", "pdfium")

    # build config
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "BUILDCONFIG.gn",
    )

    original_content = 'set_defaults("shared_library") {\n  configs = default_shared_library_configs\n}'
    has_content = f.file_has_content(source_file, original_content)

    if has_content:
        new_content = 'set_defaults("shared_library") {\n  configs = default_shared_library_configs\n\n  if (is_android) {\n    configs -= [ "//build/config/android:hide_all_but_jni_onload" ]\n  }\n}'
        f.replace_in_file(source_file, original_content, new_content)
        l.bullet("Applied: build config", l.GREEN)
    else:
        l.bullet("Skipped: build config", l.PURPLE)

    l.ok()


# -----------------------------------------------------------------------------
def run_task_build():
    l.colored("Building libraries...", l.YELLOW)

    current_dir = f.current_dir()

    # configs
    for config in c.configurations_android:
        # targets
        for target in c.targets_android:
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
            args.append('target_os="{0}"'.format(target["pdfium_os"]))
            args.append('target_cpu="{0}"'.format(target["target_cpu"]))
            args.append("use_goma=false")
            args.append("is_debug={0}".format(arg_is_debug))
            args.append("treat_warnings_as_errors=false")
            args.append("pdf_use_skia=false")
            args.append("pdf_enable_xfa=false")
            args.append("pdf_enable_v8=false")
            args.append("is_component_build=true")
            args.append("pdf_is_standalone=true")
            args.append("pdf_bundle_freetype=true")

            if config == "release":
                args.append("symbol_level=0")

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
    for config in c.configurations_android:
        f.recreate_dir(os.path.join("build", "android", config))

        # targets
        for target in c.targets_android:
            out_dir = "{0}-{1}-{2}".format(
                target["target_os"], target["target_cpu"], config
            )

            source_lib_dir = os.path.join("build", "android", "pdfium", "out", out_dir)

            lib_dir = os.path.join("build", "android", config, "lib")
            target_dir = os.path.join(lib_dir, target["android_cpu"])

            f.recreate_dir(target_dir)

            for basename in os.listdir(source_lib_dir):
                if basename.endswith(".so"):
                    pathname = os.path.join(source_lib_dir, basename)

                    if os.path.isfile(pathname):
                        f.copy_file(pathname, os.path.join(target_dir, basename))

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

        include_dir = os.path.join("build", "android", "pdfium", "public")
        include_cpp_dir = os.path.join(include_dir, "cpp")
        target_include_dir = os.path.join("build", "android", config, "include")
        target_include_cpp_dir = os.path.join(target_include_dir, "cpp")

        f.recreate_dir(target_include_dir)
        f.copy_files(include_dir, target_include_dir, "*.h")
        f.copy_files(include_cpp_dir, target_include_cpp_dir, "*.h")

    l.ok()


# -----------------------------------------------------------------------------
def run_task_test():
    l.colored("Testing...", l.YELLOW)

    for config in c.configurations_android:
        for target in c.targets_android:
            lib_dir = os.path.join(
                "build", "android", config, "lib", target["android_cpu"]
            )

            command = ["file", os.path.join(lib_dir, "libpdfium.cr.so")]
            r.run(command)

    l.ok()


# -----------------------------------------------------------------------------
def run_task_archive():
    l.colored("Archiving...", l.YELLOW)

    current_dir = os.getcwd()
    lib_dir = os.path.join(current_dir, "build", "android")
    output_filename = os.path.join(current_dir, "android.tgz")

    tar = tarfile.open(output_filename, "w:gz")

    for configuration in c.configurations_android:
        tar.add(
            name=os.path.join(lib_dir, configuration),
            arcname=os.path.basename(os.path.join(lib_dir, configuration)),
            filter=lambda x: (
                None
                if "_" in x.name
                and not x.name.endswith(".h")
                and not x.name.endswith(".so")
                and os.path.isfile(x.name)
                else x
            ),
        )

    tar.close()

    l.ok()
