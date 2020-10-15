import glob
import os
from subprocess import check_call

import modules.config as c
import modules.functions as f


def run_task_apply_patch():
    f.debug("Applying patchs...")

    source_dir = os.path.join("build", "ios", "pdfium")

    # build gn
    source_file = os.path.join(source_dir, "BUILD.gn",)
    if not f.file_line_has_content(source_file, 235, '#test("pdfium_unittests") {\n'):
        f.file_line_comment_range(source_file, 235, 282)
        f.file_line_comment_range(source_file, 375, 376)

        f.debug("Applied: Build GN")
    else:
        f.debug("Skipped: Build GN")

    # libjpeg
    source_file = os.path.join(source_dir, "third_party", "libjpeg_turbo", "BUILD.gn",)
    if not f.file_line_has_content(
        source_file,
        13,
        '#assert(!is_ios, "This is not used on iOS, don\'t drag it in unintentionally")\n',
    ):
        f.file_line_comment(source_file, 13)

        f.debug("Applied: Lib JPEG")
    else:
        f.debug("Skipped: Lib JPEG")

    # ios automatically manage certs
    source_file = os.path.join(
        source_dir, "build", "config", "ios", "ios_sdk_overrides.gni",
    )
    if not f.file_has_content(source_file, "ios_automatically_manage_certs"):
        f.append_to_file(
            source_file, "if (is_ios) { ios_automatically_manage_certs = true }"
        )

        f.debug("Applied: iOS Automatically Manage Certs")
    else:
        f.debug("Skipped: iOS Automatically Manage Certs")

    # compiler
    source_file = os.path.join(source_dir, "build", "config", "compiler", "BUILD.gn",)
    if not f.file_line_has_content(
        source_file, 1636, '#      "-Wimplicit-fallthrough",\n'
    ):
        f.file_line_comment(source_file, 1636)

        f.debug("Applied: Compiler")
    else:
        f.debug("Skipped: Compiler")

    # carbon
    source_file = os.path.join(
        source_dir, "core", "fxge", "apple", "fx_quartz_device.h",
    )
    if not f.file_line_has_content(
        source_file, 10, "#include <CoreGraphics/CoreGraphics.h>\n"
    ):
        f.replace_line_in_file(
            source_file,
            10,
            "#include <CoreGraphics/CoreGraphics.h>\n#include <CoreFoundation/CFString.h>\n",
        )

        f.debug("Applied: Carbon")
    else:
        f.debug("Skipped: Carbon")

    # ios simulator
    source_file = os.path.join(source_dir, "build", "config", "ios", "rules.gni",)
    if not f.file_line_has_content(
        source_file, 910, '#          data_deps += [ "//testing/iossim" ]\n'
    ):
        f.file_line_comment(source_file, 910)

        f.debug("Applied: iOS Simulator")
    else:
        f.debug("Skipped: iOS Simulator")

    # 32bits constexpr
    source_file = os.path.join(
        source_dir,
        "third_party",
        "base",
        "allocator",
        "partition_allocator",
        "address_space_randomization.h",
    )
    if f.file_line_has_content(
        source_file, 248, "  constexpr ALWAYS_INLINE uintptr_t ASLRMask() {\n"
    ):
        f.replace_line_in_file(
            source_file,
            248,
            "  PAGE_ALLOCATOR_CONSTANTS_DECLARE_CONSTEXPR ALWAYS_INLINE uintptr_t ASLRMask() {\n",
        )
        f.replace_line_in_file(
            source_file,
            251,
            "  PAGE_ALLOCATOR_CONSTANTS_DECLARE_CONSTEXPR ALWAYS_INLINE uintptr_t ASLROffset() {\n",
        )

        f.debug("Applied: 32bits constexpr")
    else:
        f.debug("Skipped: 32bits constexpr")

    # ARM Neon
    source_file = os.path.join(source_dir, "build_overrides", "build.gni",)
    if f.file_line_has_content(source_file, 18, 'if (current_cpu == "arm") {\n'):
        f.replace_line_in_file(source_file, 18, 'if (current_cpu == "arm64") {\n')

        f.debug("Applied: ARM Neon")
    else:
        f.debug("Skipped: ARM Neon")

    # core fxge
    source_file = os.path.join(source_dir, "core", "fxge", "BUILD.gn")
    if f.file_line_has_content(source_file, 167, "  if (is_mac) {\n"):
        f.replace_line_in_file(source_file, 167, "  if (is_mac || is_ios) {\n")

        f.debug("Applied: Core FXGE")
    else:
        f.debug("Skipped: Core FXGE")


def run_task_build():
    f.debug("Building libraries...")

    current_dir = os.getcwd()

    # configs
    for config in c.configurations_ios:
        # targets
        for target in c.targets_ios:
            main_dir = os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            )

            f.remove_dir(main_dir)
            f.create_dir(main_dir)

            os.chdir(os.path.join("build", target["target_os"], "pdfium",))

            # generating files...
            f.debug(
                'Generating files to arch "{0}" and configuration "{1}"...'.format(
                    target["target_cpu"], config
                )
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

            if target["target_cpu"] == "arm":
                args.append("enable_ios_bitcode=true")
                args.append("arm_use_neon=false")
            elif target["target_cpu"] == "arm64":
                args.append("enable_ios_bitcode=true")

            if config == "release":
                args.append("symbol_level=0")

            args_str = " ".join(args)

            command = " ".join(
                [
                    "gn",
                    "gen",
                    "out/{0}-{1}-{2}".format(
                        config, target["target_os"], target["target_cpu"]
                    ),
                    "--args='{0}'".format(args_str),
                ]
            )
            check_call(command, shell=True)

            # compiling...
            f.debug(
                'Compiling to arch "{0}" and configuration "{1}"...'.format(
                    target["target_cpu"], config
                )
            )

            command = " ".join(
                [
                    "ninja",
                    "-C",
                    "out/{0}-{1}-{2}".format(
                        config, target["target_os"], target["target_cpu"]
                    ),
                    "pdfium",
                    "-v",
                ]
            )
            check_call(command, shell=True)

            os.chdir(current_dir)


def run_task_install():
    f.debug("Installing libraries...")

    # configs
    for config in c.configurations_ios:
        f.remove_dir(os.path.join("build", "ios", config))
        f.create_dir(os.path.join("build", "ios", config))

        # targets
        for target in c.targets_ios:
            files = get_compiled_files(config, target)

            files_str = " ".join(files)

            lib_file_out = os.path.join(
                "build", "ios", config, "libpdfium_{0}.a".format(target["target_cpu"])
            )

            # we have removed symbols to squeeze final results. -no_warning_for_no_symbols will save us from useless warnings.
            command = " ".join(
                [
                    "libtool",
                    "-static -no_warning_for_no_symbols",
                    files_str,
                    "-o",
                    lib_file_out,
                ]
            )
            check_call(command, shell=True)

        # universal
        folder = os.path.join("build", "ios", config, "*.a")
        files = glob.glob(folder)
        files_str = " ".join(files)
        lib_file_out = os.path.join("build", "ios", config, "libpdfium.a")

        f.debug("Merging libraries (lipo)...")
        command = " ".join(["lipo", "-create", files_str, "-o", lib_file_out])
        check_call(command, shell=True)

        f.debug("File data...")
        command = " ".join(["file", lib_file_out])
        check_call(command, shell=True)

        f.debug("File size...")
        command = " ".join(["ls", "-lh ", lib_file_out])
        check_call(command, shell=True)


def run_task_test():
    f.debug("Testing...")

    current_dir = os.getcwd()

    for configuration in c.configurations_ios:
        lib_dir = os.path.join(current_dir, "build", "ios", configuration)

        command = " ".join(["file", os.path.join(lib_dir, "libpdfium.a")])
        check_call(command, shell=True)

    os.chdir(current_dir)


def get_compiled_files(config, target):
    folder = os.path.join(
        "build",
        target["target_os"],
        "pdfium",
        "out",
        "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
        "obj",
        "**",
        "*.a",
    )

    files = glob.glob(folder, recursive=True)

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdftext",
            "fpdftext",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fxcrt",
            "fxcrt",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfapi",
            "page",
            "page",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfapi",
            "render",
            "render",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfapi",
            "parser",
            "parser",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfapi",
            "edit",
            "edit",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfapi",
            "cmaps",
            "cmaps",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfapi",
            "font",
            "font",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fpdfdoc",
            "fpdfdoc",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fxcodec",
            "fxcodec",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fxge",
            "fxge",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "core",
            "fdrm",
            "fdrm",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "fxjs",
            "fxjs",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "fpdfsdk",
            "pwl",
            "pwl",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "fpdfsdk",
            "formfiller",
            "formfiller",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "fpdfsdk",
            "fpdfsdk",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "fx_freetype",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "fx_agg",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "skia_shared",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "pdfium_base",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "fx_lcms2",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "fx_libopenjpeg",
            "*.o",
        )
    )

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "third_party",
            "zlib",
            "zlib",
            "*.o",
        )
    )

    if target["target_cpu"] == "arm64":
        files.append(
            os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
                "obj",
                "third_party",
                "zlib",
                "zlib_adler32_simd",
                "*.o",
            )
        )

        files.append(
            os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
                "obj",
                "third_party",
                "zlib",
                "zlib_inflate_chunk_simd",
                "*.o",
            )
        )

    return files
