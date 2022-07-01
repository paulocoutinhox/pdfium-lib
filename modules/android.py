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

    # build gn
    source_file = os.path.join(
        source_dir,
        "BUILD.gn",
    )

    line_content = "defines = ["
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        line_content = '"FPDFSDK_EXPORTS",'
        line_number_to_add = f.get_file_line_number_with_content(
            source_file, line_content, strip=True
        )

        if line_number_to_add:
            l.bullet("Skipped: build gn", l.PURPLE)
        else:
            content = '  defines = [\n    "FPDFSDK_EXPORTS",'
            f.set_file_line_content(source_file, line_number, content, new_line=True)
            l.bullet("Applied: build gn", l.GREEN)
    else:
        l.bullet("Error: build gn", l.RED)

    # build gn flags
    source_file = os.path.join(
        source_dir,
        "BUILD.gn",
    )

    line_content = "cflags = []"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = '  cflags = [ "-fvisibility=default" ]'

        f.set_file_line_content(source_file, line_number, content, new_line=True)

        # more one
        line_number = f.get_file_line_number_with_content(
            source_file, line_content, strip=True
        )

        f.set_file_line_content(source_file, line_number, content, new_line=True)

        # more one
        line_number = f.get_file_line_number_with_content(
            source_file, line_content, strip=True
        )

        f.set_file_line_content(source_file, line_number, content, new_line=True)

        l.bullet("Applied: build gn flags", l.GREEN)
    else:
        l.bullet("Skipped: build gn flags", l.PURPLE)

    # compiler warning as error
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "compiler.gni",
    )

    line_content = "treat_warnings_as_errors = true"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = "  treat_warnings_as_errors = false"
        f.set_file_line_content(source_file, line_number, content, new_line=True)
        l.bullet("Applied: compiler warning as error", l.GREEN)
    else:
        l.bullet("Skipped: compiler warning as error", l.PURPLE)

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
            args.append("pdf_use_skia=false")
            args.append("pdf_use_skia_paths=false")
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

        # include
        include_dir = os.path.join("build", "android", "pdfium", "public")
        target_include_dir = os.path.join("build", "android", config, "include")

        f.recreate_dir(target_include_dir)

        for basename in os.listdir(include_dir):
            if basename.endswith(".h"):
                pathname = os.path.join(include_dir, basename)

                if os.path.isfile(pathname):
                    f.copy_file(pathname, os.path.join(target_include_dir, basename))

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
