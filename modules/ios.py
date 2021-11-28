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
    p.get_pdfium_by_target("ios")


# -----------------------------------------------------------------------------
def run_task_patch():
    l.colored("Patching files...", l.YELLOW)

    source_dir = os.path.join("build", "ios", "pdfium")

    # build gn - tests 1
    source_file = os.path.join(
        source_dir,
        "BUILD.gn",
    )

    line_content = 'test("pdfium_unittests") {'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        line_numbers = f.get_file_line_numbers_with_enclosing_tags(
            source_file, "{", "}", start_from=line_number
        )

        if line_numbers:
            f.file_line_prepend_range(
                source_file, line_numbers[0], line_numbers[1], "#"
            )

            l.bullet("Applied: build gn - tests 1", l.GREEN)
        else:
            l.bullet("Error: build gn - tests 1", l.RED)
    else:
        l.bullet("Skipped: build gn - tests 1", l.PURPLE)

    # build gn - tests 2
    source_file = os.path.join(
        source_dir,
        "BUILD.gn",
    )

    line_content = 'test("pdfium_embeddertests") {'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        line_numbers = f.get_file_line_numbers_with_enclosing_tags(
            source_file, "{", "}", start_from=line_number
        )

        if line_numbers:
            f.file_line_prepend_range(
                source_file, line_numbers[0], line_numbers[1], "#"
            )

            l.bullet("Applied: build gn - tests 2", l.GREEN)
        else:
            l.bullet("Error: build gn - tests 2", l.RED)
    else:
        l.bullet("Skipped: build gn - tests 2", l.PURPLE)

    # pdfium - embeddertests
    source_file = os.path.join(
        source_dir,
        "BUILD.gn",
    )

    line_content = '":pdfium_embeddertests",'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.file_line_prepend(source_file, line_number, "#")
        l.bullet("Applied: pdfium - embeddertests", l.GREEN)
    else:
        l.bullet("Skipped: pdfium - embeddertests", l.PURPLE)

    # pdfium - unittests
    source_file = os.path.join(
        source_dir,
        "BUILD.gn",
    )

    line_content = '":pdfium_unittests",'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.file_line_prepend(source_file, line_number, "#")
        l.bullet("Applied: pdfium - unittests", l.GREEN)
    else:
        l.bullet("Skipped: pdfium - unittests", l.PURPLE)

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
        f.replace_line_in_file(source_file, line_number, content, new_line=True)
        l.bullet("Applied: compiler warning as error", l.GREEN)
    else:
        l.bullet("Skipped: compiler warning as error", l.PURPLE)

    # libjpeg
    source_file = os.path.join(
        source_dir,
        "third_party",
        "libjpeg_turbo",
        "BUILD.gn",
    )

    line_content = (
        'assert(!is_ios, "This is not used on iOS, don\'t drag it in unintentionally")'
    )
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.file_line_prepend(source_file, line_number, "#")
        l.bullet("Applied: libjpeg", l.GREEN)
    else:
        l.bullet("Skipped: libjpeg", l.PURPLE)

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

    # carbon
    source_file = os.path.join(
        source_dir,
        "core",
        "fxge",
        "apple",
        "fx_quartz_device.h",
    )

    line_content = "#include <Carbon/Carbon.h>"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = "#include <CoreGraphics/CoreGraphics.h>\n#include <CoreFoundation/CFString.h>"
        f.replace_line_in_file(source_file, line_number, content, new_line=True)
        l.bullet("Applied: carbon", l.GREEN)
    else:
        l.bullet("Skipped: carbon", l.PURPLE)

    # carbon - font
    source_file = os.path.join(
        source_dir,
        "core",
        "fpdfapi",
        "font",
        "cpdf_type1font.cpp",
    )

    line_content = "#include <Carbon/Carbon.h>"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = "#include <CoreGraphics/CoreGraphics.h>"
        f.replace_line_in_file(source_file, line_number, content, new_line=True)
        l.bullet("Applied: carbon - font", l.GREEN)
    else:
        l.bullet("Skipped: carbon - font", l.PURPLE)

    # ios simulator
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "ios",
        "rules.gni",
    )

    line_content = 'data_deps += [ "//testing/iossim" ]'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.file_line_prepend(source_file, line_number, "#")
        l.bullet("Applied: ios simulator", l.GREEN)
    else:
        l.bullet("Skipped: ios simulator", l.PURPLE)

    # 32bits constexpr - 1
    source_file = os.path.join(
        source_dir,
        "third_party",
        "base",
        "allocator",
        "partition_allocator",
        "address_space_randomization.h",
    )

    line_content = "constexpr ALWAYS_INLINE uintptr_t ASLRMask() {"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = "PAGE_ALLOCATOR_CONSTANTS_DECLARE_CONSTEXPR ALWAYS_INLINE uintptr_t ASLRMask() {"
        f.replace_in_file(source_file, line_content, content)
        l.bullet("Applied: 32bits constexpr - 1", l.GREEN)
    else:
        l.bullet("Skipped: 32bits constexpr - 1", l.PURPLE)

    # 32bits constexpr - 2
    source_file = os.path.join(
        source_dir,
        "third_party",
        "base",
        "allocator",
        "partition_allocator",
        "address_space_randomization.h",
    )

    line_content = "constexpr ALWAYS_INLINE uintptr_t ASLROffset() {"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = "PAGE_ALLOCATOR_CONSTANTS_DECLARE_CONSTEXPR ALWAYS_INLINE uintptr_t ASLROffset() {"
        f.replace_in_file(source_file, line_content, content)
        l.bullet("Applied: 32bits constexpr - 2", l.GREEN)
    else:
        l.bullet("Skipped: 32bits constexpr - 2", l.PURPLE)

    # arm neon
    source_file = os.path.join(
        source_dir,
        "build_overrides",
        "build.gni",
    )

    line_content = 'if (current_cpu == "arm") {'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = 'if (current_cpu == "arm64") {'
        f.replace_line_in_file(source_file, line_number, content, new_line=True)
        l.bullet("Applied: arm neon", l.GREEN)
    else:
        l.bullet("Skipped: arm neon", l.PURPLE)

    # core fxge
    source_file = os.path.join(source_dir, "core", "fxge", "BUILD.gn")

    line_content = "if (is_mac) {"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = "  if (is_mac || is_ios) {"
        f.replace_line_in_file(source_file, line_number, content, new_line=True)
        l.bullet("Applied: core fxge", l.GREEN)
    else:
        l.bullet("Skipped: core fxge", l.PURPLE)

    # clang 12
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )

    line_content = 'cflags += [ "-ffile-compilation-dir=." ]'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = '      cflags += ["-Xclang","-fdebug-compilation-dir","-Xclang","."]'
        f.replace_line_in_file(source_file, line_number, content, new_line=True)
        l.bullet("Applied: clang 12", l.GREEN)
    else:
        l.bullet("Skipped: clang 12", l.PURPLE)

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
            args.append("is_component_build=false")
            args.append("clang_use_chrome_plugins=false")
            args.append("pdf_is_standalone=false")
            args.append('ios_deployment_target="9.0"')
            args.append("ios_enable_code_signing=false")
            args.append("use_xcode_clang=true")
            args.append("pdf_is_complete_lib=true")

            if target["target_cpu"] == "arm":
                args.append("enable_ios_bitcode=true")
                args.append("arm_use_neon=false")
            elif target["target_cpu"] == "arm64":
                args.append("enable_ios_bitcode=true")

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
            r.run_as_shell(" ".join(command))

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

        # universal
        folder = os.path.join("build", "ios", config, "lib", "*.a")
        files = glob.glob(folder)
        files_str = " ".join(files)
        lib_file_out = os.path.join("build", "ios", config, "lib", "libpdfium.a")

        l.colored("Merging libraries (lipo)...", l.YELLOW)
        command = ["lipo", "-create", files_str, "-o", lib_file_out]
        r.run_as_shell(" ".join(command))

        l.colored("File data...", l.YELLOW)
        command = ["file", lib_file_out]
        r.run_as_shell(" ".join(command))

        l.colored("File size...", l.YELLOW)
        command = ["ls", "-lh ", lib_file_out]
        r.run_as_shell(" ".join(command))

        # include
        include_dir = os.path.join("build", "ios", "pdfium", "public")
        target_include_dir = os.path.join("build", "ios", config, "include")

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

    for config in c.configurations_ios:
        lib_dir = os.path.join("build", "ios", config, "lib")

        command = ["file", os.path.join(lib_dir, "libpdfium.a")]
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
            filter=lambda x: (
                None if "_" in x.name and not x.name.endswith(".h") else x
            ),
        )

    tar.close()

    l.ok()
