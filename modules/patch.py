import os

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

    # file: public/fpdfview.h (p1)
    source_file = os.path.join(public_dir, "fpdfview.h")

    original_content = "#if defined(COMPONENT_BUILD)\n// FPDF_EXPORT should be consistent with |export| in the pdfium_fuzzer\n// template in testing/fuzzers/BUILD.gn."
    has_content = f.file_has_content(source_file, original_content)

    if has_content:
        f.replace_in_file(source_file, original_content, "")
        l.bullet("Applied: public headers (p1)", l.GREEN)
    else:
        l.bullet("Skipped: public headers (p1)", l.PURPLE)

    # file: public/fpdfview.h (p2)
    source_file = os.path.join(public_dir, "fpdfview.h")

    original_content = "#else\n#define FPDF_EXPORT\n#endif  // defined(COMPONENT_BUILD)"
    has_content = f.file_has_content(source_file, original_content)

    if has_content:
        f.replace_in_file(source_file, original_content, "")
        l.bullet("Applied: public headers (p2)", l.GREEN)
    else:
        l.bullet("Skipped: public headers (p2)", l.PURPLE)
