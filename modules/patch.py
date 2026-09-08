import os
import re

from pygemstones.io import file as f
from pygemstones.util import log as l


# -----------------------------------------------------------------------------
def apply_shared_library(target):
    source_dir = os.path.join("build", target, "pdfium")
    source_file = os.path.join(source_dir, "BUILD.gn")

    original_content = 'component("pdfium") {'
    has_content = f.file_has_content(source_file, original_content)

    if has_content:
        new_content = 'shared_library("pdfium") {'
        f.replace_in_file(source_file, original_content, new_content)
        l.bullet("Applied: shared library", l.GREEN)
    else:
        l.bullet("Skipped: shared library", l.PURPLE)


# -----------------------------------------------------------------------------
def apply_public_headers(target):
    source_dir = os.path.join("build", target, "pdfium")
    public_dir = os.path.join(source_dir, "public")

    # Removes the first component build guard from public/fpdfview.h.
    source_file = os.path.join(public_dir, "fpdfview.h")

    original_content = "#if defined(COMPONENT_BUILD)\n// FPDF_EXPORT should be consistent with |export| in the pdfium_fuzzer\n// template in testing/fuzzers/BUILD.gn."
    has_content = f.file_has_content(source_file, original_content)

    if has_content:
        f.replace_in_file(source_file, original_content, "")
        l.bullet("Applied: public headers (p1)", l.GREEN)
    else:
        l.bullet("Skipped: public headers (p1)", l.PURPLE)

    # Removes the second component build guard from public/fpdfview.h.
    source_file = os.path.join(public_dir, "fpdfview.h")

    original_content = "#else\n#define FPDF_EXPORT\n#endif  // defined(COMPONENT_BUILD)"
    has_content = f.file_has_content(source_file, original_content)

    if has_content:
        f.replace_in_file(source_file, original_content, "")
        l.bullet("Applied: public headers (p2)", l.GREEN)
    else:
        l.bullet("Skipped: public headers (p2)", l.PURPLE)


# Returns the directory where the windows sdk is installed.
def get_windows_sdk_dir():
    return os.environ.get(
        "WindowsSdkDir",
        os.path.join("C:\\", "Program Files (x86)", "Windows Kits", "10"),
    )


# Returns the newest usable windows sdk version installed, or None when there is none.
def find_installed_windows_sdk_version(sdk_dir=None):
    if not sdk_dir:
        sdk_dir = get_windows_sdk_dir()

    include_dir = os.path.join(sdk_dir, "Include")

    if not os.path.isdir(include_dir):
        return None

    versions = []

    for name in os.listdir(include_dir):
        parts = name.split(".")

        # A version only counts when it carries the headers the build looks for.
        if not os.path.isdir(os.path.join(include_dir, name, "um")):
            continue

        if all(part.isdigit() for part in parts):
            versions.append((tuple(int(part) for part in parts), name))

    if not versions:
        return None

    return max(versions)[1]


# -----------------------------------------------------------------------------
# Points the pinned windows sdk version at one that is installed.
def apply_windows_sdk_version(target):
    # Chromium pins the sdk version it ships with and hands it to vcvarsall, so any other version fails before compiling.
    version = find_installed_windows_sdk_version()

    if not version:
        l.bullet("Skipped: windows sdk version", l.PURPLE)
        return

    build_dir = os.path.join("build", target, "pdfium", "build")

    source_files = [
        os.path.join(build_dir, "vs_toolchain.py"),
        os.path.join(build_dir, "toolchain", "win", "setup_toolchain.py"),
    ]

    new_content = "SDK_VERSION = '{0}'".format(version)

    for source_file in source_files:
        name = os.path.basename(source_file)
        found = re.search(r"SDK_VERSION = '[\d.]+'", f.get_file_contents(source_file))

        if not found or found.group(0) == new_content:
            l.bullet("Skipped: windows sdk version ({0})".format(name), l.PURPLE)
            continue

        f.replace_in_file(source_file, found.group(0), new_content)
        l.bullet(
            "Applied: windows sdk version {0} ({1})".format(version, name), l.GREEN
        )


# Returns every windows api level the installed sdk defines, mapped to its numeric value.
def find_installed_windows_ntddi_versions(sdk_dir=None):
    if not sdk_dir:
        sdk_dir = get_windows_sdk_dir()

    version = find_installed_windows_sdk_version(sdk_dir)

    if not version:
        return {}

    header = os.path.join(sdk_dir, "Include", version, "shared", "sdkddkver.h")

    if not os.path.isfile(header):
        return {}

    found = re.findall(
        r"#define\s+(NTDDI_WIN\w+)\s+(0x[0-9A-Fa-f]+)", f.get_file_contents(header)
    )

    return {name: int(value, 16) for name, value in found}


# -----------------------------------------------------------------------------
# Points the pinned windows api level at one the installed sdk defines.
def apply_windows_ntddi_version(target):
    # An sdk that does not define the pinned level expands it to zero, and the version guards then hide the declarations the build needs.
    versions = find_installed_windows_ntddi_versions()

    if not versions:
        l.bullet("Skipped: windows ntddi version", l.PURPLE)
        return

    source_file = os.path.join(
        "build", target, "pdfium", "build", "config", "win", "BUILD.gn"
    )

    found = re.search(r'"NTDDI_VERSION=(NTDDI_\w+)"', f.get_file_contents(source_file))

    if not found:
        l.bullet("Skipped: windows ntddi version", l.PURPLE)
        return

    if found.group(1) in versions:
        l.bullet("Skipped: windows ntddi version", l.PURPLE)
        return

    newest = max(versions, key=versions.get)

    f.replace_in_file(source_file, found.group(0), '"NTDDI_VERSION={0}"'.format(newest))

    l.bullet("Applied: windows ntddi version {0}".format(newest), l.GREEN)
