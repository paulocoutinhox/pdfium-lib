import glob
import os
import tarfile
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

    # compiler thin archive
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "BUILDCONFIG.gn",
    )
    if f.file_line_has_content(
        source_file,
        332,
        '  "//build/config/compiler:thin_archive",\n',
    ):
        f.replace_line_in_file(
            source_file,
            332,
            '  #"//build/config/compiler:thin_archive",\n',
        )

        f.debug("Applied: compiler thin archive")
    else:
        f.debug("Skipped: compiler thin archive")

    # build thin archive
    source_file = os.path.join(
        source_dir,
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file,
        203,
        '    configs -= [ "//build/config/compiler:thin_archive" ]\n',
    ):
        f.replace_line_in_file(
            source_file,
            203,
            '    #configs -= [ "//build/config/compiler:thin_archive" ]\n',
        )

        f.debug("Applied: build thin archive")
    else:
        f.debug("Skipped: build thin archive")

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
        817,
        '        "-m64",\n',
    ):
        f.replace_line_in_file(
            source_file,
            817,
            '        #"-m64",\n',
        )
        f.replace_line_in_file(
            source_file,
            818,
            '        #"-march=$x64_arch",\n',
        )
        f.replace_line_in_file(
            source_file,
            819,
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
        1590,
        '          "-Wno-ignored-pragma-optimize",\n',
    ):
        f.replace_line_in_file(
            source_file,
            1590,
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
        2407,
        '        cflags += [ "-ggnu-pubnames" ]\n',
    ):
        f.replace_line_in_file(
            source_file,
            2407,
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
        650,
        '    cc = "$prefix/clang"\n',
    ):
        f.replace_line_in_file(
            source_file,
            650,
            '    cc = "emcc"\n',
        )
        f.replace_line_in_file(
            source_file,
            651,
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

    # compiler stack protector
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file,
        312,
        '        cflags += [ "-fstack-protector" ]\n',
    ):
        f.replace_line_in_file(
            source_file,
            312,
            '        cflags += [ "-fno-stack-protector" ]\n',
        )

        f.replace_line_in_file(
            source_file,
            324,
            '        cflags += [ "-fno-stack-protector" ]\n',
        )

        f.debug("Applied: compiler stack protector")
    else:
        f.debug("Skipped: compiler stack protector")

    # build pthread
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file,
        236,
        '      "pthread",\n',
    ):
        f.replace_line_in_file(
            source_file,
            236,
            '      #"pthread",\n',
        )

        f.debug("Applied: build pthread")
    else:
        f.debug("Skipped: build pthread")

    # compiler pthread
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file,
        479,
        '    cflags += [ "-pthread" ]\n',
    ):
        f.replace_line_in_file(
            source_file,
            479,
            '    #cflags += [ "-pthread" ]\n',
        )

        f.debug("Applied: compiler pthread")
    else:
        f.debug("Skipped: compiler pthread")

    # skia pthread
    source_file = os.path.join(
        source_dir,
        "third_party",
        "skia",
        "gn",
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file,
        231,
        '    libs += [ "pthread" ]\n',
    ):
        f.replace_line_in_file(
            source_file,
            231,
            '    #libs += [ "pthread" ]\n',
        )

        f.debug("Applied: skia pthread")
    else:
        f.debug("Skipped: skia pthread")

    # copy files required
    f.debug("Copying required files...")

    linux_dir = os.path.join(source_dir, "linux")
    f.create_dir(linux_dir)

    f.copy_file("/usr/include/jpeglib.h", os.path.join(source_dir, "jpeglib.h"))
    f.copy_file("/usr/include/jmorecfg.h", os.path.join(source_dir, "jmorecfg.h"))
    f.copy_file("/usr/include/zlib.h", os.path.join(source_dir, "zlib.h"))
    f.copy_file("/usr/include/zconf.h", os.path.join(source_dir, "zconf.h"))
    f.copy_file("/usr/include/jerror.h", os.path.join(source_dir, "jerror.h"))
    f.copy_file(
        "/usr/include/x86_64-linux-gnu/jconfig.h", os.path.join(source_dir, "jconfig.h")
    )
    f.copy_file("/usr/include/linux/limits.h", os.path.join(linux_dir, "limits.h"))

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
                "{0}-{1}-{2}".format(target["target_os"], target["target_cpu"], config),
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
            args.append("use_debug_fission=false")
            args.append("use_custom_libcxx=false")
            args.append("use_sysroot=false")
            args.append("use_system_libjpeg=true")
            args.append("use_system_zlib=true")
            args.append("pdf_is_complete_lib=true")

            if config == "release":
                args.append("symbol_level=0")

            args_str = " ".join(args)

            command = " ".join(
                [
                    "gn",
                    "gen",
                    "out/{0}-{1}-{2}".format(
                        target["target_os"], target["target_cpu"], config
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
                        target["target_os"], target["target_cpu"], config
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
        for target in c.targets_wasm:
            f.remove_dir(
                os.path.join("build", target["target_os"], target["target_cpu"], config)
            )

            f.create_dir(
                os.path.join("build", target["target_os"], target["target_cpu"], config)
            )

            f.create_dir(
                os.path.join(
                    "build", target["target_os"], target["target_cpu"], config, "lib"
                )
            )

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
                target["target_cpu"],
                config,
                "lib",
                "libpdfium.a",
            )

            f.copy_file(source_lib_path, target_lib_path)

            # check file
            f.debug("File data...")
            command = " ".join(["file", target_lib_path])
            check_call(command, shell=True)

            f.debug("File size...")
            command = " ".join(["ls", "-lh ", target_lib_path])
            check_call(command, shell=True)

            # include
            include_dir = os.path.join("build", "linux", "pdfium", "public")
            target_include_dir = os.path.join(
                "build", target["target_os"], target["target_cpu"], config, "include"
            )

            f.remove_dir(target_include_dir)
            f.create_dir(target_include_dir)

            for basename in os.listdir(include_dir):
                if basename.endswith(".h"):
                    pathname = os.path.join(include_dir, basename)

                    if os.path.isfile(pathname):
                        f.copy_file2(pathname, target_include_dir)


def run_task_test():
    f.debug("Testing...")

    current_dir = os.getcwd()
    sample_dir = os.path.join(current_dir, "sample-wasm")
    build_dir = os.path.join(sample_dir, "build")
    http_dir = os.path.join("sample-wasm", "build")

    for config in c.configurations_wasm:
        for target in c.targets_wasm:
            lib_file_out = os.path.join(
                current_dir,
                "build",
                target["target_os"],
                target["target_cpu"],
                config,
                "lib",
                "libpdfium.a",
            )

            include_dir = os.path.join(
                current_dir,
                "build",
                target["target_os"],
                target["target_cpu"],
                config,
                "include",
            )

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
                    "-s",
                    "USE_ZLIB=1",
                    "-s",
                    "USE_LIBJPEG=1",
                    "-s",
                    "WASM=1",
                    "-s",
                    "ASSERTIONS=1",
                    "-s",
                    "ALLOW_MEMORY_GROWTH=1",
                    "--embed-file",
                    "assets/web-assembly.pdf",
                ]
            )
            check_call(command, cwd=sample_dir, shell=True)

            f.debug(
                "Test on browser with: python -m http.server --directory {0}".format(
                    http_dir
                )
            )


def run_task_generate():
    f.debug("Generating...")

    current_dir = os.getcwd()

    for config in c.configurations_wasm:
        for target in c.targets_wasm:
            # paths
            utils_dir = os.path.join(current_dir, "extras", "wasm", "utils")
            template_dir = os.path.join(current_dir, "extras", "wasm", "template")

            relative_dir = os.path.join(
                "build",
                target["target_os"],
                target["target_cpu"],
            )

            root_dir = os.path.join(current_dir, relative_dir)
            main_dir = os.path.join(root_dir, config)
            lib_dir = os.path.join(main_dir, "lib")
            include_dir = os.path.join(main_dir, "include")
            gen_dir = os.path.join(root_dir, "gen")
            node_dir = os.path.join(main_dir, "node")
            http_dir = os.path.join(relative_dir, config, "node")

            f.remove_dir(gen_dir)
            f.create_dir(gen_dir)

            # doxygen
            f.debug("Doxygen...")

            doxygen_file = os.path.join(
                current_dir,
                "extras",
                "wasm",
                "doxygen",
                "Doxyfile",
            )

            command = " ".join(
                [
                    "doxygen",
                    doxygen_file,
                ]
            )
            check_call(command, cwd=include_dir, shell=True)

            # copy xml files
            f.debug("Copying xml files...")

            xml_dir = os.path.join(include_dir, "xml")
            f.copy_dir(xml_dir, os.path.join(gen_dir, "xml"))
            f.remove_dir(xml_dir)

            # copy utils files
            f.debug("Copying utils files...")

            f.copy_dir(utils_dir, os.path.join(gen_dir, "utils"))

            # prepare files
            f.debug("Preparing files...")

            rsp_file = os.path.join(gen_dir, "utils", "pdfium.rsp")
            f.replace_in_file(rsp_file, "{LIB_DIR}", lib_dir)
            f.replace_in_file(rsp_file, "{INCLUDE_DIR}", include_dir)

            # node modules
            f.debug("Installing node modules...")

            gen_utils_dir = os.path.join(
                gen_dir,
                "utils",
            )

            command = " ".join(
                [
                    "npm",
                    "install",
                ]
            )
            check_call(command, cwd=gen_utils_dir, shell=True)

            # generate
            f.debug("Compiling with emscripten...")

            gen_out_dir = os.path.join(
                gen_dir,
                "out",
            )

            f.remove_dir(gen_out_dir)
            f.create_dir(gen_out_dir)

            html_file = os.path.join(
                gen_out_dir,
                "pdfium.html",
            )

            command = " ".join(
                [
                    "em++",
                    "-o",
                    html_file,
                    "-s",
                    'EXPORTED_FUNCTIONS="$(node function-names ../xml/index.xml)"',
                    "-s",
                    'EXTRA_EXPORTED_RUNTIME_METHODS=\'["ccall", "cwrap"]\'',
                    "custom.cpp",
                    "@pdfium.rsp",
                    "-O3",
                    "-std=c++11",
                    "-Wall",
                    "--no-entry",
                ]
            )
            check_call(command, cwd=gen_utils_dir, shell=True)

            # copy files
            f.debug("Copying compiled files...")

            f.remove_dir(node_dir)
            f.copy_dir(gen_out_dir, node_dir)

            # copy template files
            f.debug("Copying template files...")

            f.copy_file(
                os.path.join(template_dir, "index.html"),
                os.path.join(node_dir, "index.html"),
            )

            # test
            f.debug(
                "Test on browser with: python -m http.server --directory {0}".format(
                    http_dir
                )
            )

    f.debug("Generated")


def run_task_publish():
    f.debug("Publishing...")

    current_dir = os.getcwd()
    publish_dir = os.path.join(current_dir, "build", "linux", "publish")
    node_dir = os.path.join(current_dir, "build", "linux", "x64", "release", "node")
    template_dir = os.path.join(current_dir, "extras", "wasm", "template")

    # copy generated files
    f.remove_dir(publish_dir)
    f.copy_dir(node_dir, publish_dir)

    # copy template files
    f.copy_file(
        os.path.join(template_dir, "README.md"),
        os.path.join(publish_dir, "README.md"),
    )

    # finish
    f.debug("Test on browser with: https://paulo-coutinho.github.io/pdfium-lib/")

    f.debug("Published")


def run_task_publish_to_web():
    f.debug("Publishing...")

    current_dir = os.getcwd()
    publish_dir = os.path.join(current_dir, "build", "linux", "publish")
    node_dir = os.path.join(current_dir, "build", "linux", "x64", "release", "node")
    template_dir = os.path.join(current_dir, "extras", "wasm", "template")

    # copy generated files
    f.remove_dir(publish_dir)
    f.copy_dir(node_dir, publish_dir)

    # copy template files
    f.copy_file(
        os.path.join(template_dir, "README.md"),
        os.path.join(publish_dir, "README.md"),
    )

    # clone gh-pages branch
    command = "git init ."
    check_call(command, cwd=publish_dir, shell=True)

    command = "git add ."
    check_call(command, cwd=publish_dir, shell=True)

    command = 'git commit -m "new version published"'
    check_call(command, cwd=publish_dir, shell=True)

    command = 'git push "git@github.com:pdfviewer/pdfviewer.github.io.git" master:master --force'
    check_call(command, cwd=publish_dir, shell=True)

    # finish
    f.debug("Test on browser with: https://pdfviewer.github.io/")

    f.debug("Published")


def run_task_archive():
    f.debug("Archiving...")

    current_dir = os.getcwd()
    output_filename = os.path.join(current_dir, "wasm.tgz")

    tar = tarfile.open(output_filename, "w:gz")

    for config in c.configurations_wasm:
        for target in c.targets_wasm:
            lib_dir = os.path.join(
                current_dir, "build", target["target_os"], target["target_cpu"], config
            )

            tar.add(
                name=lib_dir,
                arcname=os.path.basename(lib_dir),
                filter=lambda x: (
                    None if "_" in x.name and not x.name.endswith(".h") else x
                ),
            )

    tar.close()
