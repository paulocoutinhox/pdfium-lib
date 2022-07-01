import os
import tarfile

from pygemstones.io import file as f
from pygemstones.system import runner as r
from pygemstones.util import log as l

import modules.config as c
import modules.pdfium as p


# -----------------------------------------------------------------------------
def run_task_build_pdfium():
    p.get_pdfium_by_target("wasm")


# -----------------------------------------------------------------------------
def run_task_patch():
    l.colored("Patching files...", l.YELLOW)

    source_dir = os.path.join("build", "wasm", "pdfium")

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

    # build config
    source_file = os.path.join(
        source_dir,
        "build",
        "build_config.h",
    )

    line_content = (
        "#error Please add support for your architecture in build/build_config.h"
    )
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = "#define ARCH_CPU_X86_FAMILY 1\n#define ARCH_CPU_32_BITS 1\n#define ARCH_CPU_LITTLE_ENDIAN 1"
        f.set_file_line_content(source_file, line_number, content, new_line=True)
        l.bullet("Applied: build config", l.GREEN)
    else:
        l.bullet("Skipped: build config", l.PURPLE)

    # compiler thin archive
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "BUILDCONFIG.gn",
    )

    line_content = '"//build/config/compiler:thin_archive",'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.prepend_to_file_line(source_file, line_number, "#")
        l.bullet("Applied: compiler thin archive", l.GREEN)
    else:
        l.bullet("Skipped: compiler thin archive", l.PURPLE)

    # build thin archive
    source_file = os.path.join(
        source_dir,
        "BUILD.gn",
    )

    line_content = 'configs -= [ "//build/config/compiler:thin_archive" ]'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.prepend_to_file_line(source_file, line_number, "#")
        l.bullet("Applied: build thin archive", l.GREEN)
    else:
        l.bullet("Skipped: build thin archive", l.PURPLE)

    # cflags - m64
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )

    line_content = '"-m64",'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.prepend_to_file_line(source_file, line_number, "#")
        l.bullet("Applied: cflags - m64", l.GREEN)
    else:
        l.bullet("Skipped: cflags - m64", l.PURPLE)

    # cflags - msse3
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )

    line_content = '"-msse3",'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = '#"-msse3",'
        f.replace_in_file(source_file, line_content, content)
        l.bullet("Applied: cflags - msse3", l.GREEN)
    else:
        l.bullet("Skipped: cflags - msse3", l.PURPLE)

    # pragma optimize
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )

    line_content = '"-Wno-ignored-pragma-optimize",'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = '          "-Wno-deprecated-register",'
        f.set_file_line_content(source_file, line_number, content, new_line=True)
        l.bullet("Applied: pragma optimize", l.GREEN)
    else:
        l.bullet("Skipped: pragma optimize", l.PURPLE)

    # pubnames
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )

    line_content = 'cflags += [ "-ggnu-pubnames" ]'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.prepend_to_file_line(source_file, line_number, "#")
        l.bullet("Applied: pubnames", l.GREEN)
    else:
        l.bullet("Skipped: pubnames", l.PURPLE)

    # gcc toolchain - 1
    source_file = os.path.join(
        source_dir,
        "build",
        "toolchain",
        "gcc_toolchain.gni",
    )

    line_content = 'cc = "${prefix}/clang"'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = '    cc = "emcc"'
        f.set_file_line_content(source_file, line_number, content, new_line=True)
        l.bullet("Applied: gcc toolchain - 1", l.GREEN)
    else:
        l.bullet("Skipped: gcc toolchain - 1", l.PURPLE)

    # gcc toolchain - 2
    source_file = os.path.join(
        source_dir,
        "build",
        "toolchain",
        "gcc_toolchain.gni",
    )

    line_content = 'cxx = "${prefix}/clang++"'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = '    cxx = "em++"'
        f.set_file_line_content(source_file, line_number, content, new_line=True)
        l.bullet("Applied: gcc toolchain - 2", l.GREEN)
    else:
        l.bullet("Skipped: gcc toolchain - 2", l.PURPLE)

    # partition allocator
    source_file = os.path.join(
        source_dir,
        "third_party",
        "base",
        "allocator",
        "partition_allocator",
        "spin_lock.cc",
    )

    line_content = '#warning "Processor yield not supported on this architecture."'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.prepend_to_file_line(source_file, line_number, "//")
        l.bullet("Applied: partition allocator", l.GREEN)
    else:
        l.bullet("Skipped: partition allocator", l.PURPLE)

    # compiler stack protector
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )

    line_content = 'cflags += [ "-fstack-protector" ]'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        content = 'cflags += [ "-fno-stack-protector" ]'
        f.replace_in_file(source_file, line_content, content)
        l.bullet("Applied: compiler stack protector", l.GREEN)
    else:
        l.bullet("Skipped: compiler stack protector", l.PURPLE)

    # build pthread
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "BUILD.gn",
    )

    line_content = '"pthread",'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.prepend_to_file_line(source_file, line_number, "#")
        l.bullet("Applied: build pthread", l.GREEN)
    else:
        l.bullet("Skipped: build pthread", l.PURPLE)

    # compiler pthread
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )

    line_content = 'cflags += [ "-pthread" ]'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.prepend_to_file_line(source_file, line_number, "#")
        l.bullet("Applied: compiler pthread", l.GREEN)
    else:
        l.bullet("Skipped: compiler pthread", l.PURPLE)

    # skia pthread
    source_file = os.path.join(
        source_dir,
        "third_party",
        "skia",
        "gn",
        "skia",
        "BUILD.gn",
    )

    line_content = 'libs += [ "pthread" ]'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        f.prepend_to_file_line(source_file, line_number, "#")
        l.bullet("Applied: skia pthread", l.GREEN)
    else:
        l.bullet("Skipped: skia pthread", l.PURPLE)

    # copy files required
    l.colored("Copying required files...", l.YELLOW)

    pdfium_linux_dir = os.path.join(source_dir, "linux")
    f.create_dir(pdfium_linux_dir)

    f.copy_file("/usr/include/jpeglib.h", os.path.join(source_dir, "jpeglib.h"))
    f.copy_file("/usr/include/jmorecfg.h", os.path.join(source_dir, "jmorecfg.h"))
    f.copy_file("/usr/include/zlib.h", os.path.join(source_dir, "zlib.h"))
    f.copy_file("/usr/include/zconf.h", os.path.join(source_dir, "zconf.h"))
    f.copy_file("/usr/include/jerror.h", os.path.join(source_dir, "jerror.h"))
    f.copy_file("/usr/include/jconfig.h", os.path.join(source_dir, "jconfig.h"))
    f.copy_file(
        "/usr/include/linux/limits.h", os.path.join(pdfium_linux_dir, "limits.h")
    )

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

            # check file
            l.colored("File data...", l.YELLOW)
            command = ["file", target_lib_path]
            r.run(" ".join(command), shell=True)

            l.colored("File size...", l.YELLOW)
            command = ["ls", "-lh ", target_lib_path]
            r.run(" ".join(command), shell=True)

            # include
            include_dir = os.path.join("build", "wasm", "pdfium", "public")
            target_include_dir = os.path.join(
                "build", target["target_os"], target["target_cpu"], config, "include"
            )

            f.recreate_dir(target_include_dir)

            for basename in os.listdir(include_dir):
                if basename.endswith(".h"):
                    pathname = os.path.join(include_dir, basename)

                    if os.path.isfile(pathname):
                        f.copy_file(
                            pathname, os.path.join(target_include_dir, basename)
                        )

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

            html_file = os.path.join(
                gen_out_dir,
                "pdfium.html",
            )

            command = [
                "em++",
                "{0}".format("-g" if config == "debug" else "-O3"),
                "-o",
                html_file,
                "-s",
                'EXPORTED_FUNCTIONS="$(node function-names ../xml/index.xml)"',
                "-s",
                'EXPORTED_RUNTIME_METHODS=\'["ccall", "cwrap"]\'',
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

            f.replace_in_file(
                os.path.join(node_dir, "index.html"),
                "{pdfium-commit}",
                c.pdfium_git_commit,
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
    publish_dir = os.path.join(current_dir, "build", "wasm", "publish")
    node_dir = os.path.join(current_dir, "build", "wasm", "x64", "release", "node")
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
    publish_dir = os.path.join(current_dir, "build", "wasm", "publish")
    node_dir = os.path.join(current_dir, "build", "wasm", "x64", "release", "node")
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

    command = 'git commit -m "new version published"'
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
