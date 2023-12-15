import os
import tarfile

from pygemstones.io import file as f
from pygemstones.system import runner as r
from pygemstones.util import log as l

import modules.config as c
import modules.pdfium as p


# -----------------------------------------------------------------------------
def run_task_build_pdfium():
    p.get_pdfium_by_target("wasm32")


# -----------------------------------------------------------------------------
def run_task_patch():
    l.colored("Patching files...", l.YELLOW)

    source_dir = os.path.join("build", "wasm32", "pdfium")

    # build target
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "BUILDCONFIG.gn",
    )

    line_content = '_default_toolchain = "//build/toolchain/wasm:emscripten"'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        source = """} else {
  assert(false, "Unsupported target_os: $target_os")
}"""

        target = """} else if (target_os == "wasm") {
  _default_toolchain = "//build/toolchain/wasm:emscripten"
} else {
  assert(false, "Unsupported target_os: $target_os")
}"""

        f.replace_in_file(source_file, source, target)
        l.bullet("Applied: build target", l.GREEN)
    else:
        l.bullet("Skipped: build target", l.PURPLE)

    # build os
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "BUILDCONFIG.gn",
    )

    line_content = 'is_wasm = current_os == "wasm"'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        f.replace_in_file(
            source_file,
            'is_mac = current_os == "mac"',
            'is_mac = current_os == "mac"\nis_wasm = current_os == "wasm"',
        )
        l.bullet("Applied: build os", l.GREEN)
    else:
        l.bullet("Skipped: build os", l.PURPLE)

    # build overrides target
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "BUILDCONFIG.gn",
    )

    line_content = '_default_toolchain = "//build/toolchain/wasm:emscripten"'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        source = """} else {
  assert(false, "Unsupported target_os: $target_os")
}"""

        target = """} else if (target_os == "wasm") {
  _default_toolchain = "//build/toolchain/wasm:emscripten"
} else {
  assert(false, "Unsupported target_os: $target_os")
}"""

        f.replace_in_file(source_file, source, target)
        l.bullet("Applied: build overrides target", l.GREEN)
    else:
        l.bullet("Skipped: build overrides target", l.PURPLE)

    # build overrides os
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "BUILDCONFIG.gn",
    )

    line_content = 'is_wasm = current_os == "wasm"'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        f.replace_in_file(
            source_file,
            'is_mac = current_os == "mac"',
            'is_mac = current_os == "mac"\nis_wasm = current_os == "wasm"',
        )
        l.bullet("Applied: build overrides os", l.GREEN)
    else:
        l.bullet("Skipped: build overrides os", l.PURPLE)

    # compiler
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )

    line_content = 'configs += [ "//build/config/wasm:compiler" ]'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        source = """} else if (is_mac) {
    configs += [ "//build/config/mac:compiler" ]
  }"""

        target = """} else if (is_mac) {
    configs += [ "//build/config/mac:compiler" ]
  } else if (current_os == "wasm") {
    configs += [ "//build/config/wasm:compiler" ]
  }"""

        f.replace_in_file(source_file, source, target)
        l.bullet("Applied: build compiler", l.GREEN)
    else:
        l.bullet("Skipped: build compiler", l.PURPLE)

    # stack protector
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )

    line_content = '} else if (current_os != "aix" && current_os != "wasm") {'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        f.replace_in_file(
            source_file,
            '} else if (current_os != "aix") {',
            '} else if (current_os != "aix" && current_os != "wasm") {',
        )
        l.bullet("Applied: stack protector", l.GREEN)
    else:
        l.bullet("Skipped: stack protector", l.PURPLE)

    # lib extension
    source_file = os.path.join(
        source_dir,
        "build",
        "toolchain",
        "toolchain.gni",
    )

    line_content = "} else if (is_wasm) {"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        source = """} else if (is_win) {
  shlib_extension = ".dll"
}"""

        target = """} else if (is_win) {
  shlib_extension = ".dll"
} else if (is_wasm) {
  shlib_extension = ".so"
}"""

        f.replace_in_file(source_file, source, target)
        l.bullet("Applied: lib extension", l.GREEN)
    else:
        l.bullet("Skipped: lib extension", l.PURPLE)

    # # partition allocator
    # source_file = os.path.join(
    #     source_dir,
    #     "base",
    #     "allocator",
    #     "partition_allocator",
    #     "partition_alloc_base",
    #     "threading",
    #     "platform_thread_posix.cc",
    # )

    # line_content = (
    #     "#elif BUILDFLAG(IS_POSIX) && (BUILDFLAG(IS_AIX) || defined(OS_ASMJS))"
    # )
    # line_number = f.get_file_line_number_with_content(
    #     source_file, line_content, strip=True
    # )

    # if not line_number:
    #     source = "#elif BUILDFLAG(IS_POSIX) && BUILDFLAG(IS_AIX)"
    #     target = "#elif BUILDFLAG(IS_POSIX) && (BUILDFLAG(IS_AIX) || defined(OS_ASMJS))"

    #     f.replace_in_file(source_file, source, target)
    #     l.bullet("Applied: partition allocator", l.GREEN)
    # else:
    #     l.bullet("Skipped: partition allocator", l.PURPLE)

    # fxcrt
    source_file = os.path.join(
        source_dir,
        "core",
        "fxcrt",
        "BUILD.gn",
    )

    line_content = "if (is_posix || is_fuchsia || is_wasm) {"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        source = "if (is_posix || is_fuchsia) {"
        target = "if (is_posix || is_fuchsia || is_wasm) {"

        f.replace_in_file(source_file, source, target)
        l.bullet("Applied: fxcrt", l.GREEN)
    else:
        l.bullet("Skipped: fxcrt", l.PURPLE)

    # fxge
    source_file = os.path.join(
        source_dir,
        "core",
        "fxge",
        "BUILD.gn",
    )

    line_content = "if (is_linux || is_chromeos || is_fuchsia || is_wasm) {"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        source = "if (is_linux || is_chromeos || is_fuchsia) {"
        target = "if (is_linux || is_chromeos || is_fuchsia || is_wasm) {"

        f.replace_in_file(source_file, source, target)
        l.bullet("Applied: fxge", l.GREEN)
    else:
        l.bullet("Skipped: fxge", l.PURPLE)

    # build config
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "wasm",
        "BUILD.gn",
    )

    if not f.file_exists(source_file):
        content = """config("compiler") {
  defines = [
    # Enable fseeko() and ftello() (required by libopenjpeg20)
    # https://github.com/emscripten-core/emscripten/issues/4932
    "_POSIX_C_SOURCE=200112",
  ]
}"""

        f.set_file_content(source_file, content)

        l.bullet("Applied: build config", l.GREEN)
    else:
        l.bullet("Skipped: build config", l.PURPLE)

    # toolchain
    source_file = os.path.join(
        source_dir,
        "build",
        "toolchain",
        "wasm",
        "BUILD.gn",
    )

    if not f.file_exists(source_file):
        content = """import("//build/toolchain/gcc_toolchain.gni")

gcc_toolchain("emscripten") {
  cc = "emcc"
  cxx = "em++"

  readelf = "llvm-readobj"
  ar = "emar"
  ld = cxx
  nm = "emnm"

  extra_cflags = "-Wno-unknown-warning-option"
  extra_cxxflags = "-Wno-unknown-warning-option"

  toolchain_args = {
    current_cpu = "wasm"
    current_os = "wasm"
  }
}"""

        f.set_file_content(source_file, content)

        l.bullet("Applied: toolchain", l.GREEN)
    else:
        l.bullet("Skipped: toolchain", l.PURPLE)

    # skia
    source_file = os.path.join(
        source_dir,
        "BUILD.gn",
    )

    line_content = 'deps += [ "//skia" ]'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.set_file_line_content(
            source_file, line_number, '    #deps += [ "//skia" ]', new_line=True
        )
        l.bullet("Applied: skia", l.GREEN)
    else:
        l.bullet("Skipped: skia", l.PURPLE)

    l.ok()


# -----------------------------------------------------------------------------
def run_task_build():
    l.colored("Building libraries...", l.YELLOW)

    current_dir = f.current_dir()

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
            args.append("is_component_build=false")
            args.append("clang_use_chrome_plugins=false")
            args.append("pdf_is_standalone=true")
            args.append("use_debug_fission=false")
            args.append("use_custom_libcxx=false")
            args.append("use_sysroot=false")
            args.append("pdf_is_complete_lib=true")
            args.append("pdf_use_partition_alloc=false")
            args.append("is_clang=false")

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
    for config in c.configurations_wasm:
        for target in c.targets_wasm:
            f.recreate_dir(
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

            # check file
            l.colored("File data...", l.YELLOW)
            command = ["file", target_lib_path]
            r.run(" ".join(command), shell=True)

            l.colored("File size...", l.YELLOW)
            command = ["ls", "-lh ", target_lib_path]
            r.run(" ".join(command), shell=True)

            # headers
            l.colored("Copying header files...", l.YELLOW)

            include_dir = os.path.join("build", "wasm32", "pdfium", "public")
            include_cpp_dir = os.path.join(include_dir, "cpp")
            target_include_dir = os.path.join(
                "build", target["target_os"], target["target_cpu"], config, "include"
            )
            target_include_cpp_dir = os.path.join(target_include_dir, "cpp")

            f.recreate_dir(target_include_dir)
            f.copy_files(include_dir, target_include_dir, "*.h")
            f.copy_files(include_cpp_dir, target_include_cpp_dir, "*.h")

    l.ok()


# -----------------------------------------------------------------------------
def run_task_test():
    l.colored("Testing...", l.YELLOW)

    current_dir = f.current_dir()
    sample_dir = os.path.join(current_dir, "sample-wasm")
    build_dir = os.path.join(sample_dir, "build")
    http_dir = os.path.join(sample_dir, "build")

    for config in c.configurations_wasm:
        for target in c.targets_wasm:
            l.colored(
                'Generating test files to arch "{0}" and configuration "{1}"...'.format(
                    target["target_cpu"], config
                ),
                l.YELLOW,
            )

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

            f.recreate_dir(build_dir)

            # build
            command = [
                "em++",
                "{0}".format("-g" if config == "debug" else ""),
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
            r.run(" ".join(command), cwd=sample_dir, shell=True)

            l.colored(
                "Test on browser with: python3 -m http.server --directory {0}".format(
                    http_dir
                ),
                l.YELLOW,
            )

    l.ok()


# -----------------------------------------------------------------------------
def run_task_generate():
    l.colored("Generating...", l.YELLOW)

    current_dir = f.current_dir()

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
            lib_file_out = os.path.join(lib_dir, "libpdfium.a")

            f.recreate_dir(gen_dir)

            # doxygen
            l.colored("Doxygen...", l.YELLOW)

            doxygen_file = os.path.join(
                current_dir,
                "extras",
                "wasm",
                "doxygen",
                "Doxyfile",
            )

            command = [
                "doxygen",
                doxygen_file,
            ]
            r.run(" ".join(command), cwd=include_dir, shell=True)

            # copy xml files
            l.colored("Copying xml files...", l.YELLOW)

            xml_dir = os.path.join(include_dir, "xml")
            f.copy_dir(xml_dir, os.path.join(gen_dir, "xml"))
            f.remove_dir(xml_dir)

            # copy utils files
            l.colored("Copying utils files...", l.YELLOW)
            f.copy_dir(utils_dir, os.path.join(gen_dir, "utils"))

            # node modules
            l.colored("Installing node modules...", l.YELLOW)

            gen_utils_dir = os.path.join(
                gen_dir,
                "utils",
            )

            command = [
                "npm",
                "install",
            ]
            r.run(" ".join(command), cwd=gen_utils_dir, shell=True)

            # generate
            l.colored("Compiling with emscripten...", l.YELLOW)

            gen_out_dir = os.path.join(
                gen_dir,
                "out",
            )

            f.recreate_dir(gen_out_dir)

            output_file = os.path.join(
                gen_out_dir,
                "pdfium.js",
            )

            command = [
                "em++",
                "{0}".format("-g" if config == "debug" else "-O3"),
                "-o",
                output_file,
                "-s",
                'EXPORTED_FUNCTIONS="$(node function-names ../xml/index.xml)"',
                "-s",
                'EXPORTED_RUNTIME_METHODS=\'["ccall", "cwrap", "wasmExports"]\'',
                "custom.cpp",
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
                "-sMODULARIZE",
                "-sEXPORT_NAME=PDFiumModule",
                "-std=c++11",
                "-Wall",
                "--no-entry",
            ]
            r.run(" ".join(command), cwd=gen_utils_dir, shell=True)

            # copy files
            l.colored("Copying compiled files...", l.YELLOW)

            f.remove_dir(node_dir)
            f.copy_dir(gen_out_dir, node_dir)

            # copy template files
            l.colored("Copying template files...", l.YELLOW)

            f.copy_file(
                os.path.join(template_dir, "index.html"),
                os.path.join(node_dir, "index.html"),
            )

            # change template tags
            l.colored("Replacing template tags...", l.YELLOW)

            f.replace_in_file(
                os.path.join(node_dir, "index.html"),
                "{pdfium-branch}",
                c.pdfium_git_branch,
            )

            # test
            l.colored(
                "Test on browser with: python3 -m http.server --directory {0}".format(
                    http_dir
                ),
                l.YELLOW,
            )

    l.ok()


# -----------------------------------------------------------------------------
def run_task_publish():
    l.colored("Publishing...", l.YELLOW)

    current_dir = f.current_dir()
    publish_dir = os.path.join(current_dir, "build", "wasm32", "publish")
    node_dir = os.path.join(current_dir, "build", "wasm32", "wasm", "release", "node")
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
    l.ok()


# -----------------------------------------------------------------------------
def run_task_publish_to_web():
    l.colored("Publishing...", l.YELLOW)

    current_dir = os.getcwd()
    publish_dir = os.path.join(current_dir, "build", "wasm32", "publish")
    node_dir = os.path.join(current_dir, "build", "wasm32", "wasm", "release", "node")
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
    r.run(command, cwd=publish_dir, shell=True)

    command = "git add ."
    r.run(command, cwd=publish_dir, shell=True)

    command = f'git commit -m "version {c.pdfium_git_branch} published"'
    r.run(command, cwd=publish_dir, shell=True)

    command = "git branch -M master"
    r.run(command, cwd=publish_dir, shell=True)

    command = 'git push "git@github.com:pdfviewer/pdfviewer.github.io.git" master:master --force'
    r.run(command, cwd=publish_dir, shell=True)

    # finish
    l.colored("Test on browser: https://pdfviewer.github.io/", l.YELLOW)

    l.ok()


# -----------------------------------------------------------------------------
def run_task_archive():
    l.colored("Archiving...", l.YELLOW)

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

    l.ok()
