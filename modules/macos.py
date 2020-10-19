import glob
import os
import shutil
import tarfile
from shutil import copyfile
from subprocess import check_call

import modules.config as c
import modules.functions as f


def run_task_build_pdfium():
    f.debug("Building PDFium...")

    target = "macos"
    build_dir = os.path.join("build", target)
    f.create_dir(build_dir)

    target_dir = os.path.join(build_dir, "pdfium")
    f.remove_dir(target_dir)

    cwd = build_dir
    command = " ".join(
        [
            "gclient",
            "config",
            "--unmanaged",
            "https://pdfium.googlesource.com/pdfium.git",
        ]
    )
    check_call(command, cwd=cwd, shell=True)

    cwd = build_dir
    command = " ".join(["gclient", "sync"])
    check_call(command, cwd=cwd, shell=True)

    cwd = target_dir
    command = " ".join(["git", "checkout", c.pdfium_git_commit])
    check_call(command, cwd=cwd, shell=True)


def run_task_patch():
    f.debug("Patching...")

    # source_dir = os.path.join("build", "macos", "pdfium")

    pass


def run_task_build():
    f.debug("Building libraries...")

    current_dir = os.getcwd()

    # configs
    for config in c.configurations_macos:
        # targets
        for target in c.targets_macos:
            main_dir = os.path.join(
                "build",
                target["target_os"],
                "pdfium",
                "out",
                "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            )

            f.remove_dir(main_dir)
            f.create_dir(main_dir)

            os.chdir(
                os.path.join(
                    "build",
                    target["target_os"],
                    "pdfium",
                )
            )

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
            args.append("pdf_is_standalone=true")
            args.append("use_xcode_clang=false")

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
    for config in c.configurations_macos:
        f.remove_dir(os.path.join("build", "macos", config))
        f.create_dir(os.path.join("build", "macos", config))

        # targets
        for target in c.targets_macos:
            files = get_compiled_files(config, target)

            files_str = " ".join(files)

            lib_file_out = os.path.join(
                "build", "macos", config, "libpdfium_{0}.a".format(target["target_cpu"])
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
        folder = os.path.join("build", "macos", config, "*.a")
        files = glob.glob(folder)
        files_str = " ".join(files)
        lib_file_out = os.path.join("build", "macos", config, "libpdfium.a")

        f.debug("Merging libraries (lipo)...")
        command = " ".join(["lipo", "-create", files_str, "-o", lib_file_out])
        check_call(command, shell=True)

        f.debug("File data...")
        command = " ".join(["file", lib_file_out])
        check_call(command, shell=True)

        f.debug("File size...")
        command = " ".join(["ls", "-lh ", lib_file_out])
        check_call(command, shell=True)

        # include
        include_dir = os.path.join("build", "macos", "pdfium", "public")
        target_include_dir = os.path.join("build", "macos", config, "include")
        f.remove_dir(target_include_dir)
        f.create_dir(target_include_dir)

        for basename in os.listdir(include_dir):
            if basename.endswith(".h"):
                pathname = os.path.join(include_dir, basename)

                if os.path.isfile(pathname):
                    shutil.copy2(pathname, target_include_dir)


def run_task_test():
    f.debug("Testing...")

    current_dir = os.getcwd()
    sample_dir = os.path.join(current_dir, "sample")
    build_dir = os.path.join(sample_dir, "build")

    f.remove_dir(build_dir)
    f.create_dir(build_dir)

    os.chdir(build_dir)

    # generate project
    command = " ".join(["cmake", "../"])

    check_call(command, shell=True)

    # build
    command = " ".join(["cmake", "--build", "."])
    check_call(command, shell=True)

    # copy assets
    copyfile(
        os.path.join(sample_dir, "assets", "f1.pdf"), os.path.join(build_dir, "f1.pdf")
    )

    # run
    command = " ".join(["./sample"])
    check_call(command, shell=True)

    # finish
    os.chdir(current_dir)


def run_task_archive():
    f.debug("Archiving...")

    current_dir = os.getcwd()
    lib_dir = os.path.join(current_dir, "build", "macos")
    output_filename = os.path.join(current_dir, "macos.tgz")

    tar = tarfile.open(output_filename, "w:gz")

    for configuration in c.configurations_macos:
        tar.add(
            name=os.path.join(lib_dir, configuration),
            arcname=os.path.basename(os.path.join(lib_dir, configuration)),
            filter=lambda x: (
                None if "_" in x.name and not x.name.endswith(".h") else x
            ),
        )

    tar.close()


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

    files.append(
        os.path.join(
            "build",
            target["target_os"],
            "pdfium",
            "out",
            "{0}-{1}-{2}".format(config, target["target_os"], target["target_cpu"]),
            "obj",
            "buildtools",
            "third_party",
            "libc++",
            "libc++",
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
            "buildtools",
            "third_party",
            "libc++abi",
            "libc++abi",
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
            "zlib_crc32_simd",
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
            "zlib_x86_simd",
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
            "zlib_adler32_simd",
            "*.o",
        )
    )

    return files
