import glob
import os
import tarfile
from subprocess import check_call

import modules.config as c
import modules.functions as f


def run_task_build_pdfium():
    f.debug("Building PDFium...")

    target = "ios"
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

    source_dir = os.path.join("build", "ios", "pdfium")

    # build gn
    source_file = os.path.join(
        source_dir,
        "BUILD.gn",
    )
    if not f.file_line_has_content(source_file, 245, '#test("pdfium_unittests") {\n'):
        f.file_line_comment_range(
            source_file, 245, 292
        )  # comment all lines of "pdfium_unittests"
        f.file_line_comment_range(
            source_file, 383, 384
        )  # group "pdfium_all", comment all tests

        f.debug("Applied: Build GN")
    else:
        f.debug("Skipped: Build GN")

    # deprecated warning
    source_file = os.path.join(
        source_dir,
        "BUILD.gn",
    )
    if f.file_line_has_content(
        source_file, 53, '    cflags += [ "-Wdeprecated-copy" ]\n'
    ):
        f.file_line_comment(source_file, 53)

        f.debug("Applied: Deprecated Warning")
    else:
        f.debug("Skipped: Deprecated Warning")

    # libjpeg
    source_file = os.path.join(
        source_dir,
        "third_party",
        "libjpeg_turbo",
        "BUILD.gn",
    )
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
        source_dir,
        "build",
        "config",
        "ios",
        "ios_sdk_overrides.gni",
    )
    if not f.file_has_content(source_file, "ios_automatically_manage_certs"):
        f.append_to_file(
            source_file, "if (is_ios) { ios_automatically_manage_certs = true }"
        )

        f.debug("Applied: iOS Automatically Manage Certs")
    else:
        f.debug("Skipped: iOS Automatically Manage Certs")

    # compiler
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "compiler",
        "BUILD.gn",
    )
    if f.file_line_has_content(source_file, 1703, '      "-Wimplicit-fallthrough",\n'):
        f.file_line_comment(source_file, 1703)

        f.debug("Applied: Compiler")
    else:
        f.debug("Skipped: Compiler")

    # carbon
    source_file = os.path.join(
        source_dir,
        "core",
        "fxge",
        "apple",
        "fx_quartz_device.h",
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

    # carbon - font
    source_file = os.path.join(
        source_dir,
        "core",
        "fpdfapi",
        "font",
        "cpdf_type1font.cpp",
    )
    if not f.file_line_has_content(
        source_file, 21, "#include <CoreGraphics/CoreGraphics.h>\n"
    ):
        f.replace_line_in_file(
            source_file,
            21,
            "#include <CoreGraphics/CoreGraphics.h>\n",
        )

        f.debug("Applied: Carbon - Font")
    else:
        f.debug("Skipped: Carbon - Font")

    # ios simulator
    source_file = os.path.join(
        source_dir,
        "build",
        "config",
        "ios",
        "rules.gni",
    )
    if not f.file_line_has_content(
        source_file, 951, '#          data_deps += [ "//testing/iossim" ]\n'
    ):
        f.file_line_comment(source_file, 951)

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
    source_file = os.path.join(
        source_dir,
        "build_overrides",
        "build.gni",
    )
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

    # gdal support patch - occontext cpp
    source_file = os.path.join(
        source_dir, "core", "fpdfapi", "page", "cpdf_occontext.cpp"
    )
    if f.file_line_has_content(
        source_file,
        185,
        "bool CPDF_OCContext::CheckObjectVisible(const CPDF_PageObject* pObj) const {\n",
    ):
        f.replace_line_in_file(
            source_file,
            185,
            "bool CPDF_OCContextInterface::CheckObjectVisible(const CPDF_PageObject* pObj) const {\n",
        )

        f.debug("Applied: GDAL - OCContext CPP")
    else:
        f.debug("Skipped: GDAL - OCContext CPP")

    # gdal support patch - occontext h
    source_file = os.path.join(
        source_dir, "core", "fpdfapi", "page", "cpdf_occontext.h"
    )
    if f.file_line_has_content(
        source_file, 21, "class CPDF_OCContext final : public Retainable {\n"
    ):
        f.replace_line_in_file(
            source_file,
            21,
            "class CPDF_OCContextInterface : public Retainable {\npublic:\n  ~CPDF_OCContextInterface() override = default;\n  virtual bool CheckOCGVisible(const CPDF_Dictionary* pOCGDict) const = 0;\n  virtual bool CheckObjectVisible(const CPDF_PageObject* pObj) const;\n};\n\nclass CPDF_OCContext : public CPDF_OCContextInterface {\n",
        )

        f.debug("Applied: GDAL - OCContext H")
    else:
        f.debug("Skipped: GDAL - OCContext H")

    # gdal support patch - occontext visible
    source_file = os.path.join(
        source_dir, "core", "fpdfapi", "page", "cpdf_occontext.h"
    )
    if f.file_line_has_content(
        source_file,
        34,
        "  bool CheckOCGVisible(const CPDF_Dictionary* pOCGDict) const;\n",
    ):
        f.replace_line_in_file(
            source_file,
            34,
            "  bool CheckOCGVisible(const CPDF_Dictionary* pOCGDict) const override;\n",
        )
        f.replace_line_in_file(source_file, 35, "\n")

        f.debug("Applied: GDAL - OCContext Visible")
    else:
        f.debug("Skipped: GDAL - OCContext Visible")

    # gdal support patch - render options - set occontext
    source_file = os.path.join(
        source_dir, "core", "fpdfapi", "render", "cpdf_renderoptions.h"
    )
    if f.file_line_has_content(
        source_file, 70, "  void SetOCContext(RetainPtr<CPDF_OCContext> context) {\n"
    ):
        f.replace_line_in_file(
            source_file,
            70,
            "  void SetOCContext(RetainPtr<CPDF_OCContextInterface> context) {\n",
        )

        f.debug("Applied: GDAL - Render Options Set OCContext")
    else:
        f.debug("Skipped: GDAL - Render Options Set OCContext")

    # gdal support patch - render options - get occontext
    source_file = os.path.join(
        source_dir, "core", "fpdfapi", "render", "cpdf_renderoptions.h"
    )
    if f.file_line_has_content(
        source_file,
        73,
        "  const CPDF_OCContext* GetOCContext() const { return m_pOCContext.Get(); }\n",
    ):
        f.replace_line_in_file(
            source_file,
            73,
            "  const CPDF_OCContextInterface* GetOCContext() const { return m_pOCContext.Get(); }\n",
        )

        f.debug("Applied: GDAL - Render Options Get OCContext")
    else:
        f.debug("Skipped: GDAL - Render Options Get OCContext")

    # gdal support patch - render options - attribute
    source_file = os.path.join(
        source_dir, "core", "fpdfapi", "render", "cpdf_renderoptions.h"
    )
    if f.file_line_has_content(
        source_file, 80, "  RetainPtr<CPDF_OCContext> m_pOCContext;\n"
    ):
        f.replace_line_in_file(
            source_file, 80, "  RetainPtr<CPDF_OCContextInterface> m_pOCContext;\n"
        )

        f.debug("Applied: GDAL - Render Options Attribute")
    else:
        f.debug("Skipped: GDAL - Render Options Attribute")

    # gdal support patch - annotation list
    source_file = os.path.join(source_dir, "core", "fpdfdoc", "cpdf_annotlist.cpp")
    if f.file_line_has_content(
        source_file,
        249,
        "      const CPDF_OCContext* pOCContext = pOptions->GetOCContext();\n",
    ):
        f.replace_line_in_file(
            source_file,
            249,
            "      const auto* pOCContext = pOptions->GetOCContext();\n",
        )

        f.debug("Applied: GDAL - Annotation List")
    else:
        f.debug("Skipped: GDAL - Annotation List")


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

            # gdal args
            args.append("use_rtti=true")

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
    for config in c.configurations_ios:
        target_dir = os.path.join("build", "ios", config)
        pdfium_dir = os.path.join("build", "ios", "pdfium")

        f.remove_dir(target_dir)
        f.create_dir(target_dir)

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
                target["target_cpu"],
                "lib",
                "libpdfium.a",
            )

            f.copy_file(source_lib_path, target_lib_path)

            # include
            include_dirs = [
                os.path.join("build"),
                os.path.join("constants"),
                os.path.join("fpdfsdk"),
                os.path.join("core", "fxge"),
                os.path.join("core", "fxge", "agg"),
                os.path.join("core", "fxge", "dib"),
                os.path.join("core", "fpdfdoc"),
                os.path.join("core", "fpdfapi", "parser"),
                os.path.join("core", "fpdfapi", "page"),
                os.path.join("core", "fpdfapi", "render"),
                os.path.join("core", "fxcrt"),
                os.path.join("third_party", "agg23"),
                os.path.join("third_party", "base"),
                os.path.join("third_party", "base", "allocator", "partition_allocator"),
                os.path.join("third_party", "base", "numerics"),
                os.path.join("public"),
                os.path.join("public", "cpp"),
            ]

            for include_dir in include_dirs:
                source_include_dir = os.path.join(pdfium_dir, include_dir)
                target_include_dir = os.path.join(
                    target_dir, target["target_cpu"], "include", "pdfium", include_dir
                )

                f.remove_dir(target_include_dir)
                f.create_dir(target_include_dir)

                for basename in os.listdir(source_include_dir):
                    if basename.endswith(".h"):
                        pathname = os.path.join(source_include_dir, basename)

                        if os.path.isfile(pathname):
                            f.copy_file2(pathname, target_include_dir)


def run_task_test():
    f.debug("Testing...")

    for config in c.configurations_ios:
        lib_dir = os.path.join("build", "ios", config, "lib")

        command = " ".join(["file", os.path.join(lib_dir, "libpdfium.a")])
        check_call(command, shell=True)


def run_task_archive():
    f.debug("Archiving...")

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
