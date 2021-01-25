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

    target = "linux"
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

    source_dir = os.path.join("build", "linux", "pdfium")

    # build config
    source_file = os.path.join(
        source_dir,
        "build",
        "build_config.h",
    )
    if f.file_line_has_content(
        source_file,
        201,
        "#error Please add support for your architecture in build/build_config.h\n",
    ):
        f.replace_line_in_file(
            source_file,
            201,
            "#define ARCH_CPU_X86_FAMILY 1\n#define ARCH_CPU_32_BITS 1\n#define ARCH_CPU_LITTLE_ENDIAN 1\n",
        )

        f.debug("Applied: build config")
    else:
        f.debug("Skipped: build config")

    # thin archive
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "BUILDCONFIG.gn",
    )
    if f.file_line_has_content(
        source_file,
        342,
        '  "//build/config/compiler:thin_archive",\n',
    ):
        f.replace_line_in_file(
            source_file,
            342,
            '  #"//build/config/compiler:thin_archive",\n',
        )

        f.debug("Applied: thin archive")
    else:
        f.debug("Skipped: thin archive")

    # compiler
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file,
        768,
        '        "-m64",\n',
    ):
        f.replace_line_in_file(
            source_file,
            768,
            '        #"-m64",\n',
        )
        f.replace_line_in_file(
            source_file,
            769,
            '        #"-march=$x64_arch",\n',
        )
        f.replace_line_in_file(
            source_file,
            770,
            '        #"-msse3",\n',
        )

        f.debug("Applied: compiler")
    else:
        f.debug("Skipped: compiler")

    # pragma optimize
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file,
        1541,
        '          "-Wno-ignored-pragma-optimize",\n',
    ):
        f.replace_line_in_file(
            source_file,
            1541,
            '          "-Wno-deprecated-register",\n',
        )

        f.debug("Applied: pragma optimize")
    else:
        f.debug("Skipped: pragma optimize")

    # pubnames
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file,
        2358,
        '        cflags += [ "-ggnu-pubnames" ]\n',
    ):
        f.replace_line_in_file(
            source_file,
            2358,
            '        #cflags += [ "-ggnu-pubnames" ]\n',
        )

        f.debug("Applied: pubnames")
    else:
        f.debug("Skipped: pubnames")

    # gcc toolchain
    source_file = os.path.join(
        source_dir,
        "build",
        "toolchain",
        "gcc_toolchain.gni",
    )
    if f.file_line_has_content(
        source_file,
        643,
        '    cc = "$prefix/clang"\n',
    ):
        f.replace_line_in_file(
            source_file,
            643,
            '    cc = "emcc"\n',
        )
        f.replace_line_in_file(
            source_file,
            644,
            '    cxx = "em++"\n',
        )

        f.debug("Applied: gcc toolchain")
    else:
        f.debug("Skipped: gcc toolchain")

    # partition allocator
    source_file = os.path.join(
        source_dir,
        "third_party",
        "base",
        "allocator",
        "partition_allocator",
        "spin_lock.cc",
    )
    if f.file_line_has_content(
        source_file,
        54,
        '#warning "Processor yield not supported on this architecture."\n',
    ):
        f.replace_line_in_file(
            source_file,
            54,
            '//#warning "Processor yield not supported on this architecture."\n',
        )

        f.debug("Applied: partition allocator")
    else:
        f.debug("Skipped: partition allocator")

    # copy files required
    f.debug("Copying required files...")

    linux_dir = os.path.join(source_dir, "linux")
    f.create_dir(linux_dir)

    f.copyfile("/usr/include/jpeglib.h", os.path.join(source_dir, "jpeglib.h"))
    f.copyfile("/usr/include/jmorecfg.h", os.path.join(source_dir, "jmorecfg.h"))
    f.copyfile("/usr/include/zlib.h", os.path.join(source_dir, "zlib.h"))
    f.copyfile("/usr/include/zconf.h", os.path.join(source_dir, "zconf.h"))
    f.copyfile("/usr/include/jerror.h", os.path.join(source_dir, "jerror.h"))
    f.copyfile(
        "/usr/include/x86_64-linux-gnu/jconfig.h", os.path.join(source_dir, "jconfig.h")
    )
    f.copyfile("/usr/include/linux/limits.h", os.path.join(linux_dir, "limits.h"))

    f.debug("Copied!")


def run_task_build():
    f.debug("Building libraries...")

    current_dir = os.getcwd()

    # configs
    for config in c.configurations_wasm:
        # targets
        for target in c.targets_wasm:
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
            args.append("use_debug_fission=false")
            args.append("use_custom_libcxx=false")
            args.append("use_sysroot=false")
            args.append("use_system_libjpeg=true")
            args.append("use_system_zlib=true")

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
    for config in c.configurations_wasm:
        f.remove_dir(os.path.join("build", "linux", config))
        f.create_dir(os.path.join("build", "linux", config))

        # targets
        for target in c.targets_wasm:
            files = get_compiled_files(config, target)

            files_str = " ".join(files)

            lib_file_out = os.path.join("build", "linux", config, "libpdfium.a")

            command = " ".join(
                [
                    "emcc",
                    "-Wall",
                    "-Os",
                    files_str,
                    "-o",
                    lib_file_out,
                ]
            )
            check_call(command, shell=True)

        # check file
        lib_file_out = os.path.join("build", "linux", config, "libpdfium.a")

        f.debug("File data...")
        command = " ".join(["file", lib_file_out])
        check_call(command, shell=True)

        f.debug("File size...")
        command = " ".join(["ls", "-lh ", lib_file_out])
        check_call(command, shell=True)

        # include
        include_dir = os.path.join("build", "linux", "pdfium", "public")
        target_include_dir = os.path.join("build", "linux", config, "include")
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
    sample_dir = os.path.join(current_dir, "sample-wasm")
    build_dir = os.path.join(sample_dir, "build")

    lib_file_out = os.path.join(current_dir, "build", "linux", "release", "libpdfium.a")
    include_dir = os.path.join(current_dir, "build", "linux", "release", "include")

    f.remove_dir(build_dir)
    f.create_dir(build_dir)

    # build
    command = " ".join(
        [
            "em++",
            "-o",
            "build/index.html",
            "src/main.cpp",
            lib_file_out,
            "-I{0}".format(include_dir),
            "-s",
            "DEMANGLE_SUPPORT=1",
            "--embed-file",
            "files/web-assembly.pdf",
        ]
    )
    check_call(command, cwd=sample_dir, shell=True)


def run_task_archive():
    f.debug("Archiving...")

    current_dir = os.getcwd()
    lib_dir = os.path.join(current_dir, "build", "linux")
    output_filename = os.path.join(current_dir, "wasm.tgz")

    tar = tarfile.open(output_filename, "w:gz")

    for configuration in c.configurations_wasm:
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

    return files
