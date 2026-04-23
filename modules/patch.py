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


# -----------------------------------------------------------------------------
def _apply_fpdf_annot_set_color_without_ca(target):
    """Lumin: FPDFAnnot_SetColorWithoutCA in public/fpdf_annot.h and fpdfsdk/fpdf_annot.cpp."""
    build_pdfium = os.path.join("build", target, "pdfium")
    cpp = os.path.join(build_pdfium, "fpdfsdk", "fpdf_annot.cpp")
    header = os.path.join(build_pdfium, "public", "fpdf_annot.h")
    if not os.path.isfile(cpp) or not os.path.isfile(header):
        l.bullet(
            "Skipped: FPDFAnnot_SetColorWithoutCA (no PDFium tree for "
            + target
            + ")",
            l.PURPLE,
        )
        return

    h_old = """FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetColor(FPDF_ANNOTATION annot,
                                                       FPDFANNOT_COLORTYPE type,
                                                       unsigned int R,
                                                       unsigned int G,
                                                       unsigned int B,
                                                       unsigned int A);

// Experimental API.
// Get the color of an annotation. If no color is specified, default to yellow"""

    h_new = """FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetColor(FPDF_ANNOTATION annot,
                                                       FPDFANNOT_COLORTYPE type,
                                                       unsigned int R,
                                                       unsigned int G,
                                                       unsigned int B,
                                                       unsigned int A);

// Experimental API (Lumin).
// Like FPDFAnnot_SetColor, but does not set annotation /CA. If A is 0, removes
// the stroke color (/C) or interior color (/IC) (including when Normal /AP exists).
// If A is greater than 0, sets the /C or /IC array to (R,G,B) like FPDFAnnot_SetColor
// (including when Normal /AP is present) so the dictionary stays in sync; does
// not set /CA.
FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetColorWithoutCA(
    FPDF_ANNOTATION annot,
    FPDFANNOT_COLORTYPE type,
    unsigned int R,
    unsigned int G,
    unsigned int B,
    unsigned int A);

// Experimental API.
// Get the color of an annotation. If no color is specified, default to yellow"""

    h_new_legacy = """FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetColor(FPDF_ANNOTATION annot,
                                                       FPDFANNOT_COLORTYPE type,
                                                       unsigned int R,
                                                       unsigned int G,
                                                       unsigned int B,
                                                       unsigned int A);

// Experimental API (Lumin).
// Like FPDFAnnot_SetColor, but does not set annotation /CA. If A is 0, removes
// the stroke color (/C) or interior color (/IC) for |type|. If A is greater
// than 0, does not modify the annotation dictionary.
// Fails on annotations with their appearance streams already defined; for
// those, use FPDFPageObj_Set{Stroke|Fill}Color() on the form objects instead.
FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetColorWithoutCA(
    FPDF_ANNOTATION annot,
    FPDFANNOT_COLORTYPE type,
    unsigned int R,
    unsigned int G,
    unsigned int B,
    unsigned int A);

// Experimental API.
// Get the color of an annotation. If no color is specified, default to yellow"""

    cpp_old = """  pColor->AppendNew<CPDF_Number>(R / 255.f);
  pColor->AppendNew<CPDF_Number>(G / 255.f);
  pColor->AppendNew<CPDF_Number>(B / 255.f);

  return true;
}

FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_GetColor(FPDF_ANNOTATION annot,"""

    cpp_set_color_without_ca = """
// Like FPDFAnnot_SetColor, but does not set /CA. If A is 0, removes /C or /IC
// and leaves /CA unchanged (removal works even when Normal /AP is present). If
// A is greater than 0, always sets /C or /IC to (R,G,B) in the dict (unlike
// FPDFAnnot_SetColor, this succeeds when Normal /AP is present) so the dict
// matches the Lumin style layer; does not set /CA.
FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_SetColorWithoutCA(FPDF_ANNOTATION annot,
                            FPDFANNOT_COLORTYPE type,
                            unsigned int R,
                            unsigned int G,
                            unsigned int B,
                            unsigned int A) {
  RetainPtr<CPDF_Dictionary> pAnnotDict =
      GetMutableAnnotDictFromFPDFAnnotation(annot);

  if (!pAnnotDict || R > 255 || G > 255 || B > 255 || A > 255) {
    return false;
  }

  ByteStringView key = type == FPDFANNOT_COLORTYPE_InteriorColor ? "IC" : "C";
  if (A == 0) {
    pAnnotDict->RemoveFor(key);
    return true;
  }

  // A > 0: set /C or /IC the same as FPDFAnnot_SetColor, but do not set /CA.
  RetainPtr<CPDF_Array> pColor = pAnnotDict->GetMutableArrayFor(key);
  if (pColor) {
    pColor->Clear();
  } else {
    pColor = pAnnotDict->SetNewFor<CPDF_Array>(ByteString(key));
  }

  pColor->AppendNew<CPDF_Number>(R / 255.f);
  pColor->AppendNew<CPDF_Number>(G / 255.f);
  pColor->AppendNew<CPDF_Number>(B / 255.f);

  return true;
}"""

    cpp_new = (
        """  pColor->AppendNew<CPDF_Number>(R / 255.f);
  pColor->AppendNew<CPDF_Number>(G / 255.f);
  pColor->AppendNew<CPDF_Number>(B / 255.f);

  return true;
}"""
        + cpp_set_color_without_ca
        + """

FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_GetColor(FPDF_ANNOTATION annot,"""
    )

    # Legacy stub: A>0 was a no-op; HasAPStream could block A==0 removal.
    upgrade_stub = """// Like FPDFAnnot_SetColor, but does not set /CA. If A is 0, removes /C or /IC
// and leaves /CA unchanged. If A is greater than 0, does not change the
// dictionary (no /C, /IC, or /CA updates).
FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_SetColorWithoutCA(FPDF_ANNOTATION annot,
                            FPDFANNOT_COLORTYPE type,
                            unsigned int R,
                            unsigned int G,
                            unsigned int B,
                            unsigned int A) {
  RetainPtr<CPDF_Dictionary> pAnnotDict =
      GetMutableAnnotDictFromFPDFAnnotation(annot);

  if (!pAnnotDict || R > 255 || G > 255 || B > 255 || A > 255) {
    return false;
  }

  if (HasAPStream(pAnnotDict.Get())) {
    return false;
  }

  ByteStringView key = type == FPDFANNOT_COLORTYPE_InteriorColor ? "IC" : "C";
  if (A == 0) {
    pAnnotDict->RemoveFor(key);
    return true;
  }

  // A > 0: do not set /C, /IC, or /CA.
  return true;
}"""

    has_fn = f.file_has_content(cpp, "FPDFAnnot_SetColorWithoutCA")

    # Transitional: was "fail with HasAPStream for A>0" (like stock SetColor) — Lumin
    # now always updates /C|/IC when A>0 so the dict matches style/export even with /AP.
    ap_block_remove = (
        "  if (HasAPStream(pAnnotDict.Get())) {\n    return false;\n  }\n\n"
        "  // A > 0: set /C or /IC the same as FPDFAnnot_SetColor, but do not set /CA."
    )
    if f.file_has_content(cpp, ap_block_remove):
        f.replace_in_file(
            cpp,
            ap_block_remove,
            "  // A > 0: set /C or /IC the same as FPDFAnnot_SetColor, but do not set /CA.",
        )
        c_old = (
            "// Like FPDFAnnot_SetColor, but does not set /CA. If A is 0, removes /C or /IC\n"
            "// and leaves /CA unchanged (removal works even when Normal /AP is present). If\n"
            "// A is greater than 0, sets /C or /IC to (R,G,B) like SetColor, but does not\n"
            "// set /CA; for A > 0, fails with HasAPStream, same as FPDFAnnot_SetColor."
        )
        c_new = (
            "// Like FPDFAnnot_SetColor, but does not set /CA. If A is 0, removes /C or /IC\n"
            "// and leaves /CA unchanged (removal works even when Normal /AP is present). If\n"
            "// A is greater than 0, always sets /C or /IC to (R,G,B) like the SetColor dict\n"
            "// path (unlike FPDFAnnot_SetColor, this succeeds when Normal /AP is present, so\n"
            "// the dictionary stays in sync with the Lumin style layer and export)."
        )
        if f.file_has_content(cpp, c_old):
            f.replace_in_file(cpp, c_old, c_new)
        l.bullet("Upgraded: FPDFAnnot_SetColorWithoutCA (A>0 dict set with /AP present)", l.GREEN)
        return

    has_new = f.file_has_content(
        cpp, "A > 0: set /C or /IC the same as FPDFAnnot_SetColor"
    )
    if has_new and not f.file_has_content(cpp, ap_block_remove):
        l.bullet("Skipped: FPDFAnnot_SetColorWithoutCA (up to date)", l.PURPLE)
        return
    if f.file_has_content(cpp, "  // A > 0: do not set /C, /IC, or /CA."):
        f.replace_in_file(cpp, upgrade_stub, cpp_set_color_without_ca)
        f.replace_in_file(header, h_new_legacy, h_new)
        l.bullet("Upgraded: FPDFAnnot_SetColorWithoutCA (A>0 sets /C|/IC, A==0+AP)", l.GREEN)
        return
    if not has_fn:
        f.replace_in_file(header, h_old, h_new)
        f.replace_in_file(cpp, cpp_old, cpp_new)
        l.bullet("Applied: FPDFAnnot_SetColorWithoutCA (Lumin)", l.GREEN)
        return
    l.bullet("Skipped: FPDFAnnot_SetColorWithoutCA (non-legacy present; merge manually)", l.PURPLE)


# -----------------------------------------------------------------------------
def _apply_fpdf_annot_object_support_closeshapes(target):
    """
    Lumin: FPDFAnnot_AppendObject/UpdateObject on Square/Circle, not just Ink/Stamp.

    Stock PDFium only allows FPDFAnnot_IsObjectSupportedSubtype for INK and STAMP; the same
    GenerateEmptyAP + form path used for those works for closed shapes so we can rebuild custom
    /AP (dashed, cloudy) in place without removing the annotation. Patches fpdfsdk/fpdf_annot.cpp and
    the related comments in public/fpdf_annot.h.
    """
    build_pdfium = os.path.join("build", target, "pdfium")
    cpp = os.path.join(build_pdfium, "fpdfsdk", "fpdf_annot.cpp")
    header = os.path.join(build_pdfium, "public", "fpdf_annot.h")
    if not os.path.isfile(cpp) or not os.path.isfile(header):
        l.bullet(
            "Skipped: FPDFAnnot closed-shape object support (no PDFium tree for " + target + ")",
            l.PURPLE,
        )
        return
    if f.file_has_content(cpp, "FPDF_ANNOT_SQUARE || subtype == FPDF_ANNOT_CIRCLE"):
        l.bullet("Skipped: FPDFAnnot closed-shape object support (present)", l.PURPLE)
        return

    cpp_old = """FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_IsObjectSupportedSubtype(FPDF_ANNOTATION_SUBTYPE subtype) {
  // The supported subtypes must also be communicated in the user doc.
  return subtype == FPDF_ANNOT_INK || subtype == FPDF_ANNOT_STAMP;
}"""

    cpp_new = """FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_IsObjectSupportedSubtype(FPDF_ANNOTATION_SUBTYPE subtype) {
  // Lumin: Square/Circle can host form-object appearance streams (dashed, cloudy) like Ink.
  // The supported subtypes must also be communicated in the user doc.
  return subtype == FPDF_ANNOT_INK || subtype == FPDF_ANNOT_STAMP ||
         subtype == FPDF_ANNOT_SQUARE || subtype == FPDF_ANNOT_CIRCLE;
}"""

    h_old1 = """// Check if an annotation subtype is currently supported for object extraction,
// update, and removal.
// Currently supported subtypes: ink and stamp.
//
//   subtype   - the subtype to be checked.
//
// Returns true if this subtype supported.
FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_IsObjectSupportedSubtype(FPDF_ANNOTATION_SUBTYPE subtype);"""

    h_new1 = """// Check if an annotation subtype is currently supported for object extraction,
// update, and removal.
// Lumin: also square and circle (custom /AP from path objects). Stock: ink and stamp.
//
//   subtype   - the subtype to be checked.
//
// Returns true if this subtype supported.
FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_IsObjectSupportedSubtype(FPDF_ANNOTATION_SUBTYPE subtype);"""

    f.replace_in_file(cpp, cpp_old, cpp_new)
    f.replace_in_file(header, h_old1, h_new1)
    h_append_old = (
        "//   will be owned by |annot|. Note that an |obj| cannot belong to more than one\n"
        "//   |annot|. Currently, only ink and stamp annotations are supported by this API.\n"
    )
    h_append_new = (
        "//   will be owned by |annot|. Note that an |obj| cannot belong to more than one\n"
        "//   |annot|. (Lumin: square and circle; stock: ink and stamp.) "
    )
    if f.file_has_content(header, h_append_old):
        f.replace_in_file(header, h_append_old, h_append_new)
    h_update_old = (
        "//   been retrieved by FPDFAnnot_GetObject(). Currently, only ink and stamp\n"
        "// annotations are supported by this API. Also note that only path, image, and\n"
    )
    h_update_new = (
        "//   been retrieved by FPDFAnnot_GetObject(). Lumin: also square and circle. "
        "Stock: ink and stamp. Also\n// note that only path, image, and\n"
    )
    if f.file_has_content(header, h_update_old):
        f.replace_in_file(header, h_update_old, h_update_new)
    l.bullet("Applied: FPDFAnnot closed-shape object support (Lumin)", l.GREEN)


# -----------------------------------------------------------------------------
def _apply_fpdf_annot_line_native_create_and_setline(target):
    """
    Lumin: (1) allow FPDFPage_CreateAnnot(FPDF_ANNOT_LINE) by extending
    FPDFAnnot_IsSupportedSubtype; (2) add FPDFAnnot_SetLine to write /L (GetLine
    is read-only in stock PDFium); (3) allow form-object /AP for Line like Square,
    by extending FPDFAnnot_IsObjectSupportedSubtype.

    Stock PDFium can *read* Line (FPDFAnnot_GetLine) but not create; LineAnnotation_import
    uses native /Line, not an Ink carrier. Rebuild the xcframework / jni after applying.
    """
    build_pdfium = os.path.join("build", target, "pdfium")
    cpp = os.path.join(build_pdfium, "fpdfsdk", "fpdf_annot.cpp")
    header = os.path.join(build_pdfium, "public", "fpdf_annot.h")
    if not os.path.isfile(cpp) or not os.path.isfile(header):
        l.bullet(
            "Skipped: FPDF line create + SetLine (no PDFium tree for " + target + ")",
            l.PURPLE,
        )
        return

    # Idempotent: each sub-step is skipped if already present (no single early
    # return on SetLine, so a partial apply can be completed on a later run).
    h_supported_old = (
        "//    - ink\n"
        "//    - link\n"
    )
    h_supported_new = (
        "//    - ink\n"
        "//    - line (Lumin: FPDFPage_CreateAnnot; requires patch.py)\n"
        "//    - link\n"
    )
    if f.file_has_content(header, h_supported_old) and not f.file_has_content(
        header, "line (Lumin: FPDFPage_CreateAnnot"
    ):
        f.replace_in_file(header, h_supported_old, h_supported_new)
        l.bullet("Applied: fpdf_annot.h IsSupported list (line)", l.GREEN)

    # Match stock PDFium switch order: INK, LINK (see fpdfsdk/fpdf_annot.cpp).
    cpp_isup_old = (
        "    case FPDF_ANNOT_INK:\n"
        "    case FPDF_ANNOT_LINK:\n"
    )
    cpp_isup_new = (
        "    case FPDF_ANNOT_INK:\n"
        "    case FPDF_ANNOT_LINE:\n"
        "    case FPDF_ANNOT_LINK:\n"
    )
    if f.file_has_content(cpp, cpp_isup_new):
        pass  # already patched
    elif f.file_has_content(cpp, cpp_isup_old):
        f.replace_in_file(cpp, cpp_isup_old, cpp_isup_new)
        l.bullet("Applied: FPDFAnnot_IsSupportedSubtype(FPDF_ANNOT_LINE)", l.GREEN)

    cpp_iobj_old = (
        "  return subtype == FPDF_ANNOT_INK || subtype == FPDF_ANNOT_STAMP ||\n"
        "         subtype == FPDF_ANNOT_SQUARE || subtype == FPDF_ANNOT_CIRCLE;\n"
    )
    cpp_iobj_new = (
        "  return subtype == FPDF_ANNOT_INK || subtype == FPDF_ANNOT_STAMP ||\n"
        "         subtype == FPDF_ANNOT_SQUARE || subtype == FPDF_ANNOT_CIRCLE ||\n"
        "         subtype == FPDF_ANNOT_LINE;\n"
    )
    if f.file_has_content(cpp, "subtype == FPDF_ANNOT_LINE"):
        pass
    elif f.file_has_content(cpp, cpp_iobj_old):
        f.replace_in_file(cpp, cpp_iobj_old, cpp_iobj_new)
        h_iobj = (
            "// Lumin: also square and circle (custom /AP from path objects). Stock: ink and stamp."
        )
        h_iobj2 = (
            "// Lumin: also square, circle, and line (custom /AP from path objects). "
            "Stock: ink and stamp."
        )
        if f.file_has_content(header, h_iobj):
            f.replace_in_file(header, h_iobj, h_iobj2)
        l.bullet("Applied: FPDFAnnot_IsObjectSupportedSubtype(FPDF_ANNOT_LINE)", l.GREEN)
    else:
        l.bullet("Skipped: IsObjectSupported LINE (pattern not found; manual merge?)", l.PURPLE)

    getline_block_old = (
        "  end->x = line->GetFloatAt(2);\n"
        "  end->y = line->GetFloatAt(3);\n"
        "  return true;\n"
        "}\n"
        "\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetBorder(FPDF_ANNOTATION annot,\n"
    )
    setline_impl = (
        "  end->x = line->GetFloatAt(2);\n"
        "  end->y = line->GetFloatAt(3);\n"
        "  return true;\n"
        "}\n"
        "\n"
        "// Experimental API (Lumin). Sets the /L array (two points) for a Line\n"
        "// annotation. Clears the Normal /AP so viewers regenerate from the dict. Must\n"
        "// be FPDF_ANNOT_LINE.\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetLine(FPDF_ANNOTATION annot,\n"
        "                                                        const FS_POINTF* start,\n"
        "                                                        const FS_POINTF* end) {\n"
        "  if (!start || !end) {\n"
        "    return false;\n"
        "  }\n"
        "  if (FPDFAnnot_GetSubtype(annot) != FPDF_ANNOT_LINE) {\n"
        "    return false;\n"
        "  }\n"
        "  RetainPtr<CPDF_Dictionary> annot_dict =\n"
        "      GetMutableAnnotDictFromFPDFAnnotation(annot);\n"
        "  if (!annot_dict) {\n"
        "    return false;\n"
        "  }\n"
        "  RetainPtr<CPDF_Array> line = annot_dict->SetNewFor<CPDF_Array>(\n"
        "      pdfium::annotation::kL);\n"
        "  if (!line) {\n"
        "    return false;\n"
        "  }\n"
        "  line->Clear();\n"
        "  line->AppendNew<CPDF_Number>(start->x);\n"
        "  line->AppendNew<CPDF_Number>(start->y);\n"
        "  line->AppendNew<CPDF_Number>(end->x);\n"
        "  line->AppendNew<CPDF_Number>(end->y);\n"
        "  annot_dict->RemoveFor(pdfium::annotation::kAP);\n"
        "  return true;\n"
        "}\n"
        "\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetBorder(FPDF_ANNOTATION annot,\n"
    )
    if f.file_has_content(cpp, "FPDFAnnot_SetLine("):
        if not f.file_has_content(header, "FPDFAnnot_SetLine("):
            h_get_old = (
                "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_GetLine(FPDF_ANNOTATION annot,\n"
                "                                                      FS_POINTF* start,\n"
                "                                                      FS_POINTF* end);\n"
            )
            h_get_new = (
                "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_GetLine(FPDF_ANNOTATION annot,\n"
                "                                                      FS_POINTF* start,\n"
                "                                                      FS_POINTF* end);\n"
                "\n"
                "// Experimental API (Lumin). Set /L for a Line annotation (see patch.py).\n"
                "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetLine(FPDF_ANNOTATION annot,\n"
                "                                                    const FS_POINTF* start,\n"
                "                                                    const FS_POINTF* end);\n"
            )
            if f.file_has_content(header, h_get_old):
                f.replace_in_file(header, h_get_old, h_get_new)
                l.bullet("Applied: FPDFAnnot_SetLine declaration in public header (catch-up)", l.GREEN)
    elif f.file_has_content(cpp, getline_block_old):
        f.replace_in_file(cpp, getline_block_old, setline_impl)
        h_get_old = (
            "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_GetLine(FPDF_ANNOTATION annot,\n"
            "                                                      FS_POINTF* start,\n"
            "                                                      FS_POINTF* end);\n"
        )
        h_get_new = (
            "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_GetLine(FPDF_ANNOTATION annot,\n"
            "                                                      FS_POINTF* start,\n"
            "                                                      FS_POINTF* end);\n"
            "\n"
            "// Experimental API (Lumin). Set /L for a Line annotation (see patch.py).\n"
            "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetLine(FPDF_ANNOTATION annot,\n"
            "                                                    const FS_POINTF* start,\n"
            "                                                    const FS_POINTF* end);\n"
        )
        if f.file_has_content(header, h_get_old) and not f.file_has_content(
            header, "FPDFAnnot_SetLine("
        ):
            f.replace_in_file(header, h_get_old, h_get_new)
        l.bullet("Applied: FPDFAnnot_SetLine in fpdfsdk", l.GREEN)
    else:
        l.bullet("Skipped: FPDFAnnot_SetLine insert (GetLine/SetBorder boundary not found)", l.PURPLE)


# -----------------------------------------------------------------------------
def _apply_fpdf_annot_set_number_value(target):
    """
    Lumin: FPDFAnnot_SetNumberValue in public/fpdf_annot.h and
    fpdfsdk/fpdf_annot.cpp (e.g. /CA opacity, PDF Object Number).
    """
    build_pdfium = os.path.join("build", target, "pdfium")
    cpp = os.path.join(build_pdfium, "fpdfsdk", "fpdf_annot.cpp")
    header = os.path.join(build_pdfium, "public", "fpdf_annot.h")
    if not os.path.isfile(cpp) or not os.path.isfile(header):
        l.bullet(
            "Skipped: FPDFAnnot_SetNumberValue (no PDFium tree for " + target + ")",
            l.PURPLE,
        )
        return
    if f.file_has_content(cpp, "FPDFAnnot_SetNumberValue("):
        l.bullet("Skipped: FPDFAnnot_SetNumberValue (already present)", l.PURPLE)
        return

    h_old = """FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_GetNumberValue(FPDF_ANNOTATION annot,
                         FPDF_BYTESTRING key,
                         float* value);

// Experimental API.
// Set the AP (appearance string) in |annot|'s dictionary for a given
// |appearanceMode|."""
    h_new = """FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_GetNumberValue(FPDF_ANNOTATION annot,
                         FPDF_BYTESTRING key,
                         float* value);

// Experimental API.
// Set the number value for |key| in |annot|'s dictionary (replaces an existing
// value if present). The value is stored as FPDF_OBJECT_NUMBER.
// Common keys: "CA" (constant alpha / opacity, 0.0–1.0).
// Returns true on success.
FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_SetNumberValue(FPDF_ANNOTATION annot,
                         FPDF_BYTESTRING key,
                         float value);

// Experimental API.
// Set the AP (appearance string) in |annot|'s dictionary for a given
// |appearanceMode|."""

    cpp_old = """  *value = p->GetNumber();
  return true;
}

FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_SetAP(FPDF_ANNOTATION annot,
                FPDF_ANNOT_APPEARANCEMODE appearanceMode,
                FPDF_WIDESTRING value) {"""
    cpp_new = """  *value = p->GetNumber();
  return true;
}

FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_SetNumberValue(FPDF_ANNOTATION annot,
                         FPDF_BYTESTRING key,
                         float value) {
  RetainPtr<CPDF_Dictionary> pAnnotDict =
      GetMutableAnnotDictFromFPDFAnnotation(annot);
  if (!pAnnotDict) {
    return false;
  }

  pAnnotDict->SetNewFor<CPDF_Number>(key, value);
  return true;
}

FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_SetAP(FPDF_ANNOTATION annot,
                FPDF_ANNOT_APPEARANCEMODE appearanceMode,
                FPDF_WIDESTRING value) {"""

    if f.file_has_content(header, h_old) and f.file_has_content(cpp, cpp_old):
        f.replace_in_file(header, h_old, h_new)
        f.replace_in_file(cpp, cpp_old, cpp_new)
        l.bullet("Applied: FPDFAnnot_SetNumberValue in fpdfsdk", l.GREEN)
    else:
        l.bullet(
            "Skipped: FPDFAnnot_SetNumberValue (pattern not found; manual merge?)",
            l.PURPLE,
        )


# -----------------------------------------------------------------------------
def _apply_fpdf_annot_line_endings(target):
    """
    Lumin: FPDFAnnot_GetLineEndings / FPDFAnnot_SetLineEndings for ISO /LE (two
    name entries) on Line / Polyline annotations. See LineAnnotation.cpp.
    """
    build_pdfium = os.path.join("build", target, "pdfium")
    cpp = os.path.join(build_pdfium, "fpdfsdk", "fpdf_annot.cpp")
    header = os.path.join(build_pdfium, "public", "fpdf_annot.h")
    if not os.path.isfile(cpp) or not os.path.isfile(header):
        l.bullet(
            "Skipped: FPDF line /LE (no PDFium tree for " + target + ")",
            l.PURPLE,
        )
        return
    if f.file_has_content(cpp, "FPDFAnnot_GetLineEndings("):
        l.bullet("Skipped: FPDF line /LE (already present)", l.PURPLE)
        return
    if not f.file_has_content(cpp, "FPDFAnnot_SetLine("):
        l.bullet(
            "Skipped: FPDF line /LE (FPDFAnnot_SetLine missing; apply line patch first)",
            l.PURPLE,
        )
        return

    cpp_insert_before_setborder = (
        "  annot_dict->RemoveFor(pdfium::annotation::kAP);\n"
        "  return true;\n"
        "}\n"
        "\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetBorder"
    )
    if not f.file_has_content(cpp, cpp_insert_before_setborder):
        l.bullet(
            "Skipped: FPDF line /LE (SetLine block before SetBorder not found)",
            l.PURPLE,
        )
        return

    le_impl = (
        "  annot_dict->RemoveFor(pdfium::annotation::kAP);\n"
        "  return true;\n"
        "}\n"
        "\n"
        "namespace {\n"
        "void LuminCopyByteStringToUserBuf(const ByteString& bs, char* out, int n) "
        "{\n"
        "  if (!out || n < 1) {\n"
        "    return;\n"
        "  }\n"
        "  const char* s = bs.c_str() ? bs.c_str() : \"\";\n"
        "  int cap = n - 1;\n"
        "  int i = 0;\n"
        "  for (; i < cap && s[i]; ++i) {\n"
        "    out[i] = s[i];\n"
        "  }\n"
        "  out[i] = '\\0';\n"
        "}\n"
        "ByteString LuminNameTokenOrNone(const char* s) {\n"
        "  if (!s || s[0] == '\\0') {\n"
        "    return ByteString(\"None\");\n"
        "  }\n"
        "  return ByteString(s);\n"
        "}\n"
        "}  // namespace\n"
        "\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_GetLineEndings("
        "    FPDF_ANNOTATION annot, char* outStart, int outStartLen, char* outEnd, int outEndLen) "
        "{\n"
        "  if (!outStart || outStartLen < 1 || !outEnd || outEndLen < 1) "
        "{\n"
        "    return false;\n"
        "  }\n"
        "  const FPDF_ANNOTATION_SUBTYPE st = FPDFAnnot_GetSubtype(annot);\n"
        "  if (st != FPDF_ANNOT_LINE && st != FPDF_ANNOT_POLYLINE) "
        "{\n"
        "    return false;\n"
        "  }\n"
        "  const CPDF_Dictionary* annot_dict = GetAnnotDictFromFPDFAnnotation(annot);\n"
        "  if (!annot_dict) "
        "{\n"
        "    return false;\n"
        "  }\n"
        "  RetainPtr<const CPDF_Array> le = annot_dict->GetArrayFor(\"LE\");\n"
        "  if (!le || le->size() < 2) "
        "{\n"
        "    return false;\n"
        "  }\n"
        "  RetainPtr<const CPDF_Object> o0 = le->GetObjectAt(0);\n"
        "  RetainPtr<const CPDF_Object> o1 = le->GetObjectAt(1);\n"
        "  if (!o0 || !o1) "
        "{\n"
        "    return false;\n"
        "  }\n"
        "  const CPDF_Name* n0 = ToName(o0.Get());\n"
        "  const CPDF_Name* n1 = ToName(o1.Get());\n"
        "  if (!n0 || !n1) "
        "{\n"
        "    return false;\n"
        "  }\n"
        "  LuminCopyByteStringToUserBuf(n0->GetString(), outStart, outStartLen);\n"
        "  LuminCopyByteStringToUserBuf(n1->GetString(), outEnd, outEndLen);\n"
        "  return true;\n"
        "}\n"
        "\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetLineEndings("
        "    FPDF_ANNOTATION annot, const char* startName, const char* endName) "
        "{\n"
        "  const FPDF_ANNOTATION_SUBTYPE st = FPDFAnnot_GetSubtype(annot);\n"
        "  if (st != FPDF_ANNOT_LINE && st != FPDF_ANNOT_POLYLINE) "
        "{\n"
        "    return false;\n"
        "  }\n"
        "  RetainPtr<CPDF_Dictionary> annot_dict =\n"
        "      GetMutableAnnotDictFromFPDFAnnotation(annot);\n"
        "  if (!annot_dict) "
        "{\n"
        "    return false;\n"
        "  }\n"
        "  RetainPtr<CPDF_Array> le = annot_dict->SetNewFor<CPDF_Array>(\"LE\");\n"
        "  if (!le) "
        "{\n"
        "    return false;\n"
        "  }\n"
        "  le->Clear();\n"
        "  le->AppendNew<CPDF_Name>(LuminNameTokenOrNone(startName));\n"
        "  le->AppendNew<CPDF_Name>(LuminNameTokenOrNone(endName));\n"
        "  annot_dict->RemoveFor(pdfium::annotation::kAP);\n"
        "  return true;\n"
        "}\n"
        "\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetBorder"
    )
    f.replace_in_file(cpp, cpp_insert_before_setborder, le_impl)

    h_setline = (
        "// Experimental API (Lumin). Set /L for a Line annotation (see patch.py).\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetLine(FPDF_ANNOTATION annot,\n"
        "                                                    const FS_POINTF* start,\n"
        "                                                    const FS_POINTF* end);"
    )
    h_setline_le = (
        h_setline
        + "\n"
        + "\n"
        + "// Experimental API (Lumin). Read or set /LE (line endings) for"
        " Line; see patch.py.\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_GetLineEndings("
        "    FPDF_ANNOTATION annot, char* outStart, int outStartLen, char* outEnd,\n"
        "    int outEndLen);\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_SetLineEndings("
        "    FPDF_ANNOTATION annot, const char* startName, const char* endName);"
    )
    if f.file_has_content(header, h_setline) and not f.file_has_content(
        header, "FPDFAnnot_GetLineEndings("
    ):
        f.replace_in_file(header, h_setline, h_setline_le)
    l.bullet("Applied: FPDFAnnot Get/SetLineEndings in fpdfsdk", l.GREEN)
    _apply_fpdf_annot_line_endings_polyline_upgrade(target)


# -----------------------------------------------------------------------------
def _apply_fpdf_annot_line_endings_polyline_upgrade(target):
    """
    Idempotent: extend existing Get/SetLineEndings (LINE-only) to LINE+POLYLINE
    on set. For PDFium trees patched before polyline support was added to
    le_impl.
    """
    build_pdfium = os.path.join("build", target, "pdfium")
    cpp = os.path.join(build_pdfium, "fpdfsdk", "fpdf_annot.cpp")
    if not os.path.isfile(cpp) or not f.file_has_content(cpp, "FPDFAnnot_GetLineEndings("):
        return
    if f.file_has_content(cpp, "st != FPDF_ANNOT_LINE && st != FPDF_ANNOT_POLYLINE"):
        l.bullet("Skipped: line /LE polyline upgrade (already present)", l.PURPLE)
        return

    g_old = (
        "  if (FPDFAnnot_GetSubtype(annot) != FPDF_ANNOT_LINE) \n"
        "  {\n"
        "    return false;\n"
        "  }\n"
        "  const CPDF_Dictionary* annot_dict = GetAnnotDictFromFPDFAnnotation(annot);\n"
    )
    g_new = (
        "  const FPDF_ANNOTATION_SUBTYPE st = FPDFAnnot_GetSubtype(annot);\n"
        "  if (st != FPDF_ANNOT_LINE && st != FPDF_ANNOT_POLYLINE) \n"
        "  {\n"
        "    return false;\n"
        "  }\n"
        "  const CPDF_Dictionary* annot_dict = GetAnnotDictFromFPDFAnnotation(annot);\n"
    )
    s_old = (
        "  if (FPDFAnnot_GetSubtype(annot) != FPDF_ANNOT_LINE) \n"
        "  {\n"
        "    return false;\n"
        "  }\n"
        "  RetainPtr<CPDF_Dictionary> annot_dict =\n"
        "      GetMutableAnnotDictFromFPDFAnnotation(annot);\n"
    )
    s_new = (
        "  const FPDF_ANNOTATION_SUBTYPE st = FPDFAnnot_GetSubtype(annot);\n"
        "  if (st != FPDF_ANNOT_LINE && st != FPDF_ANNOT_POLYLINE) \n"
        "  {\n"
        "    return false;\n"
        "  }\n"
        "  RetainPtr<CPDF_Dictionary> annot_dict =\n"
        "      GetMutableAnnotDictFromFPDFAnnotation(annot);\n"
    )
    plle_old = (
        "  annot_dict->RemoveFor(\"LMLE1\");\n"
        "  annot_dict->RemoveFor(pdfium::annotation::kAP);\n"
    )
    plle_new = "  annot_dict->RemoveFor(pdfium::annotation::kAP);\n"
    if f.file_has_content(cpp, g_old):
        f.replace_in_file(cpp, g_old, g_new)
        l.bullet("Upgraded: GetLineEndings allows polyline", l.GREEN)
    if f.file_has_content(cpp, s_old):
        f.replace_in_file(cpp, s_old, s_new)
        l.bullet("Upgraded: SetLineEndings allows polyline", l.GREEN)
    if f.file_has_content(cpp, plle_old):
        f.replace_in_file(cpp, plle_old, plle_new)
        l.bullet("Upgraded: SetLineEndings drops legacy LMLE1 removal", l.GREEN)


# -----------------------------------------------------------------------------
def _apply_fpdf_annot_interior_color_key_exists(target):
    """Lumin: /C and /IC key-exists helpers in public/fpdf_annot.h and fpdfsdk/fpdf_annot.cpp."""
    build_pdfium = os.path.join("build", target, "pdfium")
    cpp = os.path.join(build_pdfium, "fpdfsdk", "fpdf_annot.cpp")
    header = os.path.join(build_pdfium, "public", "fpdf_annot.h")
    if not os.path.isfile(cpp):
        l.bullet(
            "Skipped: FPDFAnnot_AnnotationColorDictionaryKeyExists (no fpdfsdk for "
            + target
            + ")",
            l.PURPLE,
        )
        return

    insert_cpp = (
        "\n// Lumin: true if the annotation dict has a color array for |type| (/C or /IC).\n"
        "// FPDFAnnot_GetColor returns a default (black, or highlight yellow) when the key\n"
        "// is absent, which must not be treated as an authored color for XFDF export.\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_AnnotationColorDictionaryKeyExists(\n"
        "    FPDF_ANNOTATION annot,\n"
        "    FPDFANNOT_COLORTYPE type) {\n"
        "  RetainPtr<CPDF_Dictionary> pAnnotDict =\n"
        "      GetMutableAnnotDictFromFPDFAnnotation(annot);\n"
        "  if (!pAnnotDict) {\n"
        "    return false;\n"
        "  }\n"
        "  return pAnnotDict->KeyExist(\n"
        "      type == FPDFANNOT_COLORTYPE_InteriorColor ? \"IC\" : \"C\");\n"
        "}\n\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_StrokeColorDictionaryKeyExists(FPDF_ANNOTATION annot) {\n"
        "  return FPDFAnnot_AnnotationColorDictionaryKeyExists(\n"
        "      annot, FPDFANNOT_COLORTYPE_Color);\n"
        "}\n\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_InteriorColorDictionaryKeyExists(FPDF_ANNOTATION annot) {\n"
        "  return FPDFAnnot_AnnotationColorDictionaryKeyExists(\n"
        "      annot, FPDFANNOT_COLORTYPE_InteriorColor);\n"
        "}\n"
    )
    if not f.file_has_content(cpp, "FPDFAnnot_AnnotationColorDictionaryKeyExists"):
        ic_only_old = (
            "// Lumin: true if the annotation dictionary has an /IC (interior color) entry.\n"
            "// FPDFAnnot_GetColor(Interior) returns a default black when /IC is absent, which\n"
            "// must not be treated as an authored fill for XFDF export.\n"
            "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
            "FPDFAnnot_InteriorColorDictionaryKeyExists(FPDF_ANNOTATION annot) {\n"
            "  RetainPtr<CPDF_Dictionary> pAnnotDict =\n"
            "      GetMutableAnnotDictFromFPDFAnnotation(annot);\n"
            "  if (!pAnnotDict) {\n"
            "    return false;\n"
            "  }\n"
            "  return pAnnotDict->KeyExist(\"IC\");\n"
            "}\n"
        )
        if f.file_has_content(cpp, ic_only_old):
            f.replace_in_file(cpp, ic_only_old, insert_cpp.lstrip())
            l.bullet("Upgraded: IC-only key check → /C and /IC (Lumin C++)", l.GREEN)
        else:
            anchor_old = (
                "  return true;\n"
                "}\n\n"
                "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
                "FPDFAnnot_HasAttachmentPoints(FPDF_ANNOTATION annot) {"
            )
            if f.file_has_content(cpp, anchor_old):
                f.replace_in_file(
                    cpp,
                    anchor_old,
                    "  return true;\n}\n" + insert_cpp + "\n"
                    "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
                    "FPDFAnnot_HasAttachmentPoints(FPDF_ANNOTATION annot) {",
                )
                l.bullet("Applied: FPDFAnnot /C and /IC key exists (Lumin C++)", l.GREEN)
            else:
                l.bullet(
                    "Skipped: FPDFAnnot color dict in cpp (no anchor; merge manually)",
                    l.PURPLE,
                )
    else:
        l.bullet(
            "Skipped: FPDFAnnot color dict key exists in fpdfsdk (cpp up to date)",
            l.PURPLE,
        )

    h_old_min = (
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_GetColor(FPDF_ANNOTATION annot,\n"
        "                                                       FPDFANNOT_COLORTYPE type,\n"
        "                                                       unsigned int* R,\n"
        "                                                       unsigned int* G,\n"
        "                                                       unsigned int* B,\n"
        "                                                       unsigned int* A);\n\n"
        "// Experimental API.\n"
        "// Check if the annotation is of a type that has attachment points"
    )
    h_new_block = (
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_GetColor(FPDF_ANNOTATION annot,\n"
        "                                                       FPDFANNOT_COLORTYPE type,\n"
        "                                                       unsigned int* R,\n"
        "                                                       unsigned int* G,\n"
        "                                                       unsigned int* B,\n"
        "                                                       unsigned int* A);\n\n"
        "// Experimental API (Lumin).\n"
        "// True if the annotation dict has /C or /IC for |type|.\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_AnnotationColorDictionaryKeyExists(\n"
        "    FPDF_ANNOTATION annot,\n"
        "    FPDFANNOT_COLORTYPE type);\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_StrokeColorDictionaryKeyExists(FPDF_ANNOTATION annot);\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_InteriorColorDictionaryKeyExists(FPDF_ANNOTATION annot);\n\n"
        "// Experimental API.\n"
        "// Check if the annotation is of a type that has attachment points"
    )
    h_old_ic = (
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV FPDFAnnot_GetColor(FPDF_ANNOTATION annot,\n"
        "                                                       FPDFANNOT_COLORTYPE type,\n"
        "                                                       unsigned int* R,\n"
        "                                                       unsigned int* G,\n"
        "                                                       unsigned int* B,\n"
        "                                                       unsigned int* A);\n\n"
        "// Experimental API (Lumin).\n"
        "// Returns true if the annotation dictionary has an /IC (interior color) entry.\n"
        "// FPDFAnnot_GetColor(Interior) synthesizes a default when /IC is missing; this\n"
        "// predicate distinguishes absent /IC from a real color array for export.\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_InteriorColorDictionaryKeyExists(FPDF_ANNOTATION annot);\n\n"
        "// Experimental API.\n"
        "// Check if the annotation is of a type that has attachment points"
    )
    if os.path.isfile(header) and not f.file_has_content(
        header, "FPDFAnnot_AnnotationColorDictionaryKeyExists"
    ):
        if f.file_has_content(header, h_old_ic):
            f.replace_in_file(header, h_old_ic, h_new_block)
            l.bullet("Upgraded: FPDFAnnot color key headers (Lumin public header)", l.GREEN)
        elif f.file_has_content(header, h_old_min):
            f.replace_in_file(header, h_old_min, h_new_block)
            l.bullet("Applied: FPDFAnnot color key headers (Lumin public header)", l.GREEN)
        else:
            l.bullet(
                "Skipped: FPDFAnnot color key exists (header anchor mismatch; merge manually)",
                l.PURPLE,
            )


# -----------------------------------------------------------------------------
def _apply_fpdf_annot_markup_bs_rd_be(target):
    """
    Lumin: FPDFAnnot_Get/Set for ISO /BS, /RD, /BE on Square and Circle annotations
    (see SquareAnnotation.cpp / patch lumin_markup_bs_rd_be.cpp.inc).
    Requires FPDFAnnot_SetNumberValue (Lumin) already applied so we can anchor
    after its closing brace and before FPDFAnnot_SetAP.
    """
    build_pdfium = os.path.join("build", target, "pdfium")
    cpp = os.path.join(build_pdfium, "fpdfsdk", "fpdf_annot.cpp")
    header = os.path.join(build_pdfium, "public", "fpdf_annot.h")
    if not os.path.isfile(cpp) or not os.path.isfile(header):
        l.bullet(
            "Skipped: FPDF BS/RD/BE (no PDFium tree for " + target + ")",
            l.PURPLE,
        )
        return
    if f.file_has_content(cpp, "FPDFAnnot_GetRectDiff("):
        l.bullet("Skipped: FPDF BS/RD/BE (already present)", l.PURPLE)
        return
    if not f.file_has_content(cpp, "FPDFAnnot_SetNumberValue("):
        l.bullet(
            "Skipped: FPDF BS/RD/BE (SetNumberValue missing; run set-number patch first)",
            l.PURPLE,
        )
        return

    this_dir = os.path.dirname(os.path.abspath(__file__))
    inc_path = os.path.join(this_dir, "lumin_markup_bs_rd_be.cpp.inc")
    if not os.path.isfile(inc_path):
        l.bullet("Skipped: FPDF BS/RD/BE (lumin_markup_bs_rd_be.cpp.inc not found)", l.PURPLE)
        return
    with open(inc_path, "r", encoding="utf-8") as inc_file:
        markup_impl = inc_file.read()

    cpp_old = (
        "  pAnnotDict->SetNewFor<CPDF_Number>(key, value);\n"
        "  return true;\n"
        "}\n\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_SetAP(FPDF_ANNOTATION annot,"
    )
    cpp_new = (
        "  pAnnotDict->SetNewFor<CPDF_Number>(key, value);\n"
        "  return true;\n"
        "}\n\n"
        + markup_impl
        + "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_SetAP(FPDF_ANNOTATION annot,"
    )
    if f.file_has_content(cpp, cpp_old):
        f.replace_in_file(cpp, cpp_old, cpp_new)
        l.bullet("Applied: FPDF BS/RD/BE markup (fpdfsdk/fpdf_annot.cpp)", l.GREEN)
    else:
        l.bullet("Skipped: FPDF BS/RD/BE (cpp anchor mismatch)", l.PURPLE)
        return

    h_old = (
        "float value);\n\n"
        "// Experimental API.\n"
        "// Set the AP (appearance string) in |annot|'s dictionary for a given\n"
        "// |appearanceMode|.\n"
        "//\n"
        "//   annot          - handle to an annotation.\n"
    )
    h_new = (
        "float value);\n\n"
        "// Experimental API (Lumin). Square / Circle: /BS, /RD, /BE; see patch.py.\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_GetRectDiff(FPDF_ANNOTATION annot, float* outLeft, float* outTop,\n"
        "                      float* outRight, float* outBottom);\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_SetRectDiff(FPDF_ANNOTATION annot, float left, float top, float right,\n"
        "                      float bottom);\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_GetBorderStyleDict(FPDF_ANNOTATION annot, char* outS, int sLen,\n"
        "                            char* outDashComma, int dashCommaLen, float* wOut);\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_SetBorderStyleDict(FPDF_ANNOTATION annot, const char* sName,\n"
        "                            const char* dashComma, float w);\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_GetBorderEffectDict(FPDF_ANNOTATION annot, char* outS, int sLen,\n"
        "                            float* iOut);\n"
        "FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV\n"
        "FPDFAnnot_SetBorderEffectDict(FPDF_ANNOTATION annot, const char* sName,\n"
        "                            float intensity);\n"
        "\n"
        "// Experimental API.\n"
        "// Set the AP (appearance string) in |annot|'s dictionary for a given\n"
        "// |appearanceMode|.\n"
        "//\n"
        "//   annot          - handle to an annotation.\n"
    )
    if f.file_has_content(header, h_old):
        f.replace_in_file(header, h_old, h_new)
        l.bullet("Applied: FPDF BS/RD/BE (public/fpdf_annot.h)", l.GREEN)
    else:
        l.bullet(
            "Warning: FPDF BS/RD/BE cpp done but public header anchor mismatch — add decls by hand",
            l.PURPLE,
        )


# -----------------------------------------------------------------------------
def apply_lumin_custom_patches(target):
    """
    Idempotent hook for Lumin-specific PDFium source changes.

    Add new patch steps here so they survive `gclient sync` (unlike one-off
    hand-edits under build/<target>/pdfium/). Call sites: ios.run_task_patch,
    android.run_task_patch.

    Args:
        target: "ios" or "android" — use to build paths under build/<target>/pdfium/.
    """
    _apply_fpdf_annot_set_color_without_ca(target)
    _apply_fpdf_annot_interior_color_key_exists(target)
    _apply_fpdf_annot_object_support_closeshapes(target)
    _apply_fpdf_annot_line_native_create_and_setline(target)
    _apply_fpdf_annot_set_number_value(target)
    _apply_fpdf_annot_line_endings(target)
    _apply_fpdf_annot_markup_bs_rd_be(target)
