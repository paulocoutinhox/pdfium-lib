import os
import subprocess
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
    p.get_pdfium_by_target("emscripten")


# -----------------------------------------------------------------------------
def run_task_patch():
    l.colored("Patching files...", l.YELLOW)

    source_dir = os.path.join("build", "emscripten", "pdfium")

    # shared lib
    if c.shared_lib_wasm:
        patch.apply_shared_library("emscripten")

    # public headers
    if c.shared_lib_wasm:
        patch.apply_public_headers("emscripten")

    # build target
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "BUILDCONFIG.gn",
    )

    line_content = '_default_toolchain = "//build/toolchain/wasm:$target_cpu"'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        source = """} else if (target_os == "emscripten") {
  # Because it's too hard to remove all targets from //BUILD.gn that do not work
  # with it.
  assert(
      false,
      "emscripten is not a supported target_os. It is available only as secondary toolchain.")
} else {"""

        target = """} else if (target_os == "emscripten") {
  _default_toolchain = "//build/toolchain/wasm:$target_cpu"
} else {"""

        f.replace_in_file(source_file, source, target)
        l.bullet("Applied: build target", l.GREEN)
    else:
        l.bullet("Skipped: build target", l.PURPLE)

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
  } else if (current_os == "emscripten") {
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

    line_content = 'if (current_os != "aix" && current_os != "emscripten") {'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        f.replace_in_file(
            source_file,
            'if (current_os != "aix") {',
            'if (current_os != "aix" && current_os != "emscripten") {',
        )
        l.bullet("Applied: stack protector", l.GREEN)
    else:
        l.bullet("Skipped: stack protector", l.PURPLE)

    # fxcrt
    source_file = os.path.join(
        source_dir,
        "core",
        "fxcrt",
        "BUILD.gn",
    )

    line_content = "if (is_posix || is_wasm) {"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        source = "if (is_posix) {"
        target = "if (is_posix || is_wasm) {"

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

    line_content = "if (is_linux || is_chromeos || is_wasm) {"
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        source = "if (is_linux || is_chromeos) {"
        target = "if (is_linux || is_chromeos || is_wasm) {"

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

    # toolchain warn
    source_file = os.path.join(
        source_dir,
        "build",
        "toolchain",
        "wasm",
        "BUILD.gn",
    )

    line_content = 'extra_cflags = "-Wno-unknown-warning-option"'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if not line_number:
        source = "toolchain_args = {"
        target = 'extra_cflags = "-Wno-unknown-warning-option"\n  extra_cxxflags = "-Wno-unknown-warning-option"\n\n  toolchain_args = {'

        f.replace_in_file(source_file, source, target)
        l.bullet("Applied: toolchain warn", l.GREEN)
    else:
        l.bullet("Skipped: toolchain warn", l.PURPLE)

    # toolchain wasm
    source_file = os.path.join(
        source_dir,
        "build",
        "toolchain",
        "wasm",
        "BUILD.gn",
    )

    line_content = 'emscripten_path = "//third_party/emsdk/upstream/emscripten/"'
    line_number = f.get_file_line_number_with_content(
        source_file, line_content, strip=True
    )

    if line_number:
        emsdk_path = os.getenv("EMSDK")
        source = 'emscripten_path = "//third_party/emsdk/upstream/emscripten/"'
        target = f'emscripten_path = "{emsdk_path}/upstream/emscripten"'

        f.replace_in_file(source_file, source, target)
        l.bullet("Applied: toolchain wasm", l.GREEN)
    else:
        l.bullet("Skipped: toolchain wasm", l.PURPLE)

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

            args = cm.get_build_args(
                config,
                c.shared_lib_wasm,
                target["pdfium_os"],
                target["target_cpu"],
            )

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

            include_dir = os.path.join("build", "emscripten", "pdfium", "public")
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
def run_task_test_wasmtime():
    from pathlib import Path

    from wasmtime import Engine, FuncType, Linker, Module, Store, WasiConfig

    l.colored("Testing with wasmtime...", l.YELLOW)

    current_dir = f.current_dir()

    for config in c.configurations_wasm:
        for target in c.targets_wasm:
            l.colored(
                'Testing arch "{0}" and configuration "{1}"...'.format(
                    target["target_cpu"], config
                ),
                l.YELLOW,
            )

            # paths
            relative_dir = os.path.join(
                "build",
                target["target_os"],
                target["target_cpu"],
                config,
            )

            root_dir = os.path.join(current_dir, relative_dir)
            node_dir = os.path.join(root_dir, "node")
            wasm_file = os.path.join(node_dir, "pdfium.std.wasm")

            # check if wasm file exists
            if not f.file_exists(wasm_file):
                l.e(f"WASM file not found: {wasm_file}")
                continue

            l.bullet(f"WASM file: {wasm_file}", l.YELLOW)

            # create engine and load the pdfium.wasm module
            engine = Engine()
            module = Module.from_file(engine, wasm_file)

            # create WASI context and store
            wasi_config = WasiConfig()
            wasi_config.inherit_stdin()
            wasi_config.inherit_stdout()
            wasi_config.inherit_stderr()

            store = Store(engine)
            store.set_wasi(wasi_config)

            # create a linker and add WASI support
            linker = Linker(engine)
            linker.define_wasi()

            # define stub functions for unknown imports
            for imp in module.imports:
                module_name = imp.module
                field_name = imp.name

                # check if this is a function import
                if isinstance(imp.type, FuncType):
                    func_type = imp.type

                    # create a stub function that returns default values
                    def make_stub(ft):
                        def stub_func(*_args):
                            # return default values (0 or None) based on results
                            if ft.results:
                                if len(ft.results) == 1:
                                    return 0
                                return tuple(0 for _ in ft.results)
                            return None

                        return stub_func

                    try:
                        linker.define_func(
                            module_name, field_name, func_type, make_stub(func_type)
                        )
                    except Exception:
                        # already defined (e.g., by WASI)
                        pass

            # instantiate the module
            instance = linker.instantiate(store, module)
            exports = instance.exports(store)

            # get and call FPDF_InitLibrary function
            try:
                init_library = exports["FPDF_InitLibrary"]
                init_library(store)
                l.bullet("FPDF_InitLibrary successfully called", l.GREEN)
            except KeyError:
                l.e("Function 'FPDF_InitLibrary' not found")
                continue

            # test with a sample PDF file
            sample_pdf = os.path.join(
                current_dir, "sample-wasm", "assets", "web-assembly.pdf"
            )

            if not f.file_exists(sample_pdf):
                l.bullet("Sample PDF not found, skipping document test", l.PURPLE)
                continue

            l.bullet(f"Testing with PDF: {sample_pdf}", l.YELLOW)

            # read PDF data
            pdf_path = Path(sample_pdf)
            pdf_data = pdf_path.read_bytes()

            # allocate memory for the PDF data
            malloc = exports["malloc"]
            memory = exports["memory"]

            # allocate buffer in WASM memory
            buf_ptr = malloc(store, len(pdf_data))
            mem_data = memory.data_ptr(store)

            # copy PDF data to WASM memory
            for i, byte in enumerate(pdf_data):
                mem_data[buf_ptr + i] = byte

            # load the PDF document from memory
            fpdf_load_mem_document = exports["FPDF_LoadMemDocument"]
            doc = fpdf_load_mem_document(store, buf_ptr, len(pdf_data), 0)

            if doc == 0:
                get_last_error = exports["FPDF_GetLastError"]
                error = get_last_error(store)
                l.e(f"Failed to load PDF. Error code: {error}")

                # free the allocated memory
                free = exports["free"]
                free(store, buf_ptr)
                continue

            # get page count
            fpdf_get_page_count = exports["FPDF_GetPageCount"]
            page_count = fpdf_get_page_count(store, doc)

            l.bullet(f"PDF: {pdf_path.name}", l.GREEN)
            l.bullet(f"Number of pages: {page_count}", l.GREEN)

            # close the document
            fpdf_close_document = exports["FPDF_CloseDocument"]
            fpdf_close_document(store, doc)

            # free the allocated memory
            free = exports["free"]
            free(store, buf_ptr)

            l.bullet("Test completed successfully", l.GREEN)

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

            try:
                result = subprocess.run(
                    ["node", "function-names", "../xml/index.xml"],
                    cwd=gen_utils_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True,
                )

                exported_functions = result.stdout.strip()
            except subprocess.CalledProcessError as e:
                l.e(f"Error when execute node: {e.stderr}")
                exported_functions = ""

            if exported_functions:
                function_list = (
                    exported_functions.strip("[]").replace(" ", "").split(",")
                )
                function_list.extend(["_malloc", "_free"])
                complete_functions_list = '["' + '","'.join(function_list) + '"]'
            else:
                complete_functions_list = '["_malloc", "_free"]'

            base_command = [
                "em++",
                "{0}".format("-g" if config == "debug" else "-O2"),
                "-s",
                f"EXPORTED_FUNCTIONS={complete_functions_list}",
                "-s",
                "ALLOW_TABLE_GROWTH",
                "-s",
                'EXPORTED_RUNTIME_METHODS=\'["ccall", "cwrap", "wasmExports", "HEAP8", "HEAP16", "HEAP32", "HEAPU8", "HEAPU16", "HEAPU32", "HEAPF32", "HEAPF64", "addFunction", "removeFunction", "setValue", "FS"]\'',
                "-s",
                "FORCE_FILESYSTEM=1",
                "custom.cpp",
                lib_file_out,
                "-I{0}".format(include_dir),
                "-s",
                "USE_ZLIB=1",
                "-s",
                "USE_LIBJPEG=1",
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

            # Generate UMD (CommonJS + AMD) module and .wasm file
            umd_command = [
                *base_command,
                "-o",
                os.path.join(gen_out_dir, "pdfium.js"),
            ]
            r.run(" ".join(umd_command), cwd=gen_utils_dir, shell=True)

            # Generate ES6 module, only .js will be generated (no .wasm)
            l.colored("Compiling ES6 module with emscripten...", l.YELLOW)
            es6_command = [
                *base_command,
                "-s",
                "EXPORT_ES6=1",
                "-o",
                os.path.join(gen_out_dir, "pdfium.esm.js"),
            ]
            r.run(" ".join(es6_command), cwd=gen_utils_dir, shell=True)

            # Generate STANDALONE module, only .js will be generated (no .wasm)
            l.colored("Compiling STANDALONE module with emscripten...", l.YELLOW)
            std_command = [
                *base_command,
                "-s" "STANDALONE_WASM=1",
                "-sSTANDALONE_WASM=1",
                "-sWASM_ASYNC_COMPILATION=0",
                "-sWARN_ON_UNDEFINED_SYMBOLS=1",
                "-sERROR_ON_UNDEFINED_SYMBOLS=0",
                "-o",
                os.path.join(gen_out_dir, "pdfium.std.js"),
            ]
            r.run(" ".join(std_command), cwd=gen_utils_dir, shell=True)

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

            f.copy_file(
                os.path.join(template_dir, "logo.png"),
                os.path.join(node_dir, "logo.png"),
            )

            f.copy_file(
                os.path.join(template_dir, "package.json"),
                os.path.join(main_dir, "package.json"),
            )

            # change template tags
            l.colored("Replacing template tags...", l.YELLOW)

            f.replace_in_file(
                os.path.join(node_dir, "index.html"),
                "{pdfium-branch}",
                c.pdfium_git_branch,
            )

            f.replace_in_file(
                os.path.join(main_dir, "package.json"),
                "{pdfium-branch-version}",
                c.pdfium_git_branch.strip("chromium/"),
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
    publish_dir = os.path.join(current_dir, "build", "emscripten", "publish")
    node_dir = os.path.join(
        current_dir, "build", "emscripten", "wasm", "release", "node"
    )
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
    publish_dir = os.path.join(current_dir, "build", "emscripten", "publish")
    node_dir = os.path.join(
        current_dir, "build", "emscripten", "wasm", "release", "node"
    )
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

            filter_files = lambda x: (
                None if "_" in x.name and not x.name.endswith(".h") else x
            )

            tar.add(
                name=lib_dir,
                arcname=os.path.basename(lib_dir),
                filter=filter_files,
            )

            # Create per config "npm install"-compatible tarball
            per_config_tar = tarfile.open(
                os.path.join(current_dir, f"wasm-{config}.tgz"), "w:gz"
            )
            per_config_tar.add(
                name=lib_dir,
                # Use "package" as the root directory to be compatible with "npm install"
                arcname="package",
                filter=filter_files,
            )
            per_config_tar.close()

    tar.close()

    l.ok()
