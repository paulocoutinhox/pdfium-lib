// Copyright 2016 PDFium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Original code copyright 2014 Foxit Software Inc. http://www.foxitsoftware.com

#include "core/fxge/cfx_fontmapper.h"

#include <algorithm>
#include <memory>
#include <sstream>
#include <tuple>
#include <utility>
#include <vector>

#include "build/build_config.h"
#include "core/fxcrt/fx_codepage.h"
#include "core/fxcrt/fx_memory_wrappers.h"
#include "core/fxge/cfx_fontmgr.h"
#include "core/fxge/cfx_substfont.h"
#include "core/fxge/fx_font.h"
#include "core/fxge/systemfontinfo_iface.h"
#include "third_party/base/stl_util.h"

namespace {

const int kNumStandardFonts = 14;
static_assert(CFX_FontMapper::kDingbats + 1 == kNumStandardFonts,
              "StandardFont enum count mismatch");

const char* const g_Base14FontNames[kNumStandardFonts] = {
    "Courier",
    "Courier-Bold",
    "Courier-BoldOblique",
    "Courier-Oblique",
    "Helvetica",
    "Helvetica-Bold",
    "Helvetica-BoldOblique",
    "Helvetica-Oblique",
    "Times-Roman",
    "Times-Bold",
    "Times-BoldItalic",
    "Times-Italic",
    "Symbol",
    "ZapfDingbats",
};

struct AltFontName {
  const char* m_pName;  // Raw, POD struct.
  CFX_FontMapper::StandardFont m_Index;
};

const AltFontName g_AltFontNames[] = {
    {"Arial", CFX_FontMapper::kHelvetica},
    {"Arial,Bold", CFX_FontMapper::kHelveticaBold},
    {"Arial,BoldItalic", CFX_FontMapper::kHelveticaBoldOblique},
    {"Arial,Italic", CFX_FontMapper::kHelveticaOblique},
    {"Arial-Bold", CFX_FontMapper::kHelveticaBold},
    {"Arial-BoldItalic", CFX_FontMapper::kHelveticaBoldOblique},
    {"Arial-BoldItalicMT", CFX_FontMapper::kHelveticaBoldOblique},
    {"Arial-BoldMT", CFX_FontMapper::kHelveticaBold},
    {"Arial-Italic", CFX_FontMapper::kHelveticaOblique},
    {"Arial-ItalicMT", CFX_FontMapper::kHelveticaOblique},
    {"ArialBold", CFX_FontMapper::kHelveticaBold},
    {"ArialBoldItalic", CFX_FontMapper::kHelveticaBoldOblique},
    {"ArialItalic", CFX_FontMapper::kHelveticaOblique},
    {"ArialMT", CFX_FontMapper::kHelvetica},
    {"ArialMT,Bold", CFX_FontMapper::kHelveticaBold},
    {"ArialMT,BoldItalic", CFX_FontMapper::kHelveticaBoldOblique},
    {"ArialMT,Italic", CFX_FontMapper::kHelveticaOblique},
    {"ArialRoundedMTBold", CFX_FontMapper::kHelveticaBold},
    {"Courier", CFX_FontMapper::kCourier},
    {"Courier,Bold", CFX_FontMapper::kCourierBold},
    {"Courier,BoldItalic", CFX_FontMapper::kCourierBoldOblique},
    {"Courier,Italic", CFX_FontMapper::kCourierOblique},
    {"Courier-Bold", CFX_FontMapper::kCourierBold},
    {"Courier-BoldOblique", CFX_FontMapper::kCourierBoldOblique},
    {"Courier-Oblique", CFX_FontMapper::kCourierOblique},
    {"CourierBold", CFX_FontMapper::kCourierBold},
    {"CourierBoldItalic", CFX_FontMapper::kCourierBoldOblique},
    {"CourierItalic", CFX_FontMapper::kCourierOblique},
    {"CourierNew", CFX_FontMapper::kCourier},
    {"CourierNew,Bold", CFX_FontMapper::kCourierBold},
    {"CourierNew,BoldItalic", CFX_FontMapper::kCourierBoldOblique},
    {"CourierNew,Italic", CFX_FontMapper::kCourierOblique},
    {"CourierNew-Bold", CFX_FontMapper::kCourierBold},
    {"CourierNew-BoldItalic", CFX_FontMapper::kCourierBoldOblique},
    {"CourierNew-Italic", CFX_FontMapper::kCourierOblique},
    {"CourierNewBold", CFX_FontMapper::kCourierBold},
    {"CourierNewBoldItalic", CFX_FontMapper::kCourierBoldOblique},
    {"CourierNewItalic", CFX_FontMapper::kCourierOblique},
    {"CourierNewPS-BoldItalicMT", CFX_FontMapper::kCourierBoldOblique},
    {"CourierNewPS-BoldMT", CFX_FontMapper::kCourierBold},
    {"CourierNewPS-ItalicMT", CFX_FontMapper::kCourierOblique},
    {"CourierNewPSMT", CFX_FontMapper::kCourier},
    {"CourierStd", CFX_FontMapper::kCourier},
    {"CourierStd-Bold", CFX_FontMapper::kCourierBold},
    {"CourierStd-BoldOblique", CFX_FontMapper::kCourierBoldOblique},
    {"CourierStd-Oblique", CFX_FontMapper::kCourierOblique},
    {"Helvetica", CFX_FontMapper::kHelvetica},
    {"Helvetica,Bold", CFX_FontMapper::kHelveticaBold},
    {"Helvetica,BoldItalic", CFX_FontMapper::kHelveticaBoldOblique},
    {"Helvetica,Italic", CFX_FontMapper::kHelveticaOblique},
    {"Helvetica-Bold", CFX_FontMapper::kHelveticaBold},
    {"Helvetica-BoldItalic", CFX_FontMapper::kHelveticaBoldOblique},
    {"Helvetica-BoldOblique", CFX_FontMapper::kHelveticaBoldOblique},
    {"Helvetica-Italic", CFX_FontMapper::kHelveticaOblique},
    {"Helvetica-Oblique", CFX_FontMapper::kHelveticaOblique},
    {"HelveticaBold", CFX_FontMapper::kHelveticaBold},
    {"HelveticaBoldItalic", CFX_FontMapper::kHelveticaBoldOblique},
    {"HelveticaItalic", CFX_FontMapper::kHelveticaOblique},
    {"Symbol", CFX_FontMapper::kSymbol},
    {"SymbolMT", CFX_FontMapper::kSymbol},
    {"Times-Bold", CFX_FontMapper::kTimesBold},
    {"Times-BoldItalic", CFX_FontMapper::kTimesBoldOblique},
    {"Times-Italic", CFX_FontMapper::kTimesOblique},
    {"Times-Roman", CFX_FontMapper::kTimes},
    {"TimesBold", CFX_FontMapper::kTimesBold},
    {"TimesBoldItalic", CFX_FontMapper::kTimesBoldOblique},
    {"TimesItalic", CFX_FontMapper::kTimesOblique},
    {"TimesNewRoman", CFX_FontMapper::kTimes},
    {"TimesNewRoman,Bold", CFX_FontMapper::kTimesBold},
    {"TimesNewRoman,BoldItalic", CFX_FontMapper::kTimesBoldOblique},
    {"TimesNewRoman,Italic", CFX_FontMapper::kTimesOblique},
    {"TimesNewRoman-Bold", CFX_FontMapper::kTimesBold},
    {"TimesNewRoman-BoldItalic", CFX_FontMapper::kTimesBoldOblique},
    {"TimesNewRoman-Italic", CFX_FontMapper::kTimesOblique},
    {"TimesNewRomanBold", CFX_FontMapper::kTimesBold},
    {"TimesNewRomanBoldItalic", CFX_FontMapper::kTimesBoldOblique},
    {"TimesNewRomanItalic", CFX_FontMapper::kTimesOblique},
    {"TimesNewRomanPS", CFX_FontMapper::kTimes},
    {"TimesNewRomanPS-Bold", CFX_FontMapper::kTimesBold},
    {"TimesNewRomanPS-BoldItalic", CFX_FontMapper::kTimesBoldOblique},
    {"TimesNewRomanPS-BoldItalicMT", CFX_FontMapper::kTimesBoldOblique},
    {"TimesNewRomanPS-BoldMT", CFX_FontMapper::kTimesBold},
    {"TimesNewRomanPS-Italic", CFX_FontMapper::kTimesOblique},
    {"TimesNewRomanPS-ItalicMT", CFX_FontMapper::kTimesOblique},
    {"TimesNewRomanPSMT", CFX_FontMapper::kTimes},
    {"TimesNewRomanPSMT,Bold", CFX_FontMapper::kTimesBold},
    {"TimesNewRomanPSMT,BoldItalic", CFX_FontMapper::kTimesBoldOblique},
    {"TimesNewRomanPSMT,Italic", CFX_FontMapper::kTimesOblique},
    {"ZapfDingbats", CFX_FontMapper::kDingbats},
};

struct AltFontFamily {
  const char* m_pFontName;    // Raw, POD struct.
  const char* m_pFontFamily;  // Raw, POD struct.
};

const AltFontFamily g_AltFontFamilies[] = {
    {"AGaramondPro", "Adobe Garamond Pro"},
    {"BankGothicBT-Medium", "BankGothic Md BT"},
    {"ForteMT", "Forte"},
};

#if _FX_PLATFORM_ == _FX_PLATFORM_LINUX_
const char kNarrowFamily[] = "LiberationSansNarrow";
#elif defined(OS_ANDROID)
const char kNarrowFamily[] = "RobotoCondensed";
#else
const char kNarrowFamily[] = "ArialNarrow";
#endif  // _FX_PLATFORM_ == _FX_PLATFORM_LINUX_

ByteString TT_NormalizeName(const char* family) {
  ByteString norm(family);
  norm.Remove(' ');
  norm.Remove('-');
  norm.Remove(',');
  auto pos = norm.Find('+');
  if (pos.has_value() && pos.value() != 0)
    norm = norm.Left(pos.value());
  norm.MakeLower();
  return norm;
}

void GetFontFamily(uint32_t nStyle, ByteString* fontName) {
  if (fontName->Contains("Script")) {
    if (FontStyleIsForceBold(nStyle))
      *fontName = "ScriptMTBold";
    else if (fontName->Contains("Palace"))
      *fontName = "PalaceScriptMT";
    else if (fontName->Contains("French"))
      *fontName = "FrenchScriptMT";
    else if (fontName->Contains("FreeStyle"))
      *fontName = "FreeStyleScript";
    return;
  }
  for (const auto& alternate : g_AltFontFamilies) {
    if (fontName->Contains(alternate.m_pFontName)) {
      *fontName = alternate.m_pFontFamily;
      return;
    }
  }
}

ByteString ParseStyle(const char* pStyle, int iLen, int iIndex) {
  std::vector<char> buf;
  if (!iLen || iLen <= iIndex)
    return ByteString(buf.data());
  while (iIndex < iLen) {
    if (pStyle[iIndex] == ',')
      break;
    buf.push_back(pStyle[iIndex]);
    ++iIndex;
  }
  return ByteString(buf.data());
}

const struct FX_FontStyle {
  const char* name;
  size_t len;
  uint32_t style;
} g_FontStyles[] = {
    {"Bold", 4, FXFONT_FORCE_BOLD},
    {"Italic", 6, FXFONT_ITALIC},
    {"BoldItalic", 10, FXFONT_FORCE_BOLD | FXFONT_ITALIC},
    {"Reg", 3, FXFONT_NORMAL},
    {"Regular", 7, FXFONT_NORMAL},
};

// <exists, index, length>
std::tuple<bool, uint32_t, size_t> GetStyleType(const ByteString& bsStyle,
                                                bool bReverse) {
  if (bsStyle.IsEmpty())
    return std::make_tuple(false, FXFONT_NORMAL, 0);

  for (int i = FX_ArraySize(g_FontStyles) - 1; i >= 0; --i) {
    const FX_FontStyle* pStyle = g_FontStyles + i;
    if (!pStyle || pStyle->len > bsStyle.GetLength())
      continue;

    if (bReverse) {
      if (bsStyle.Right(pStyle->len).Compare(pStyle->name) == 0)
        return std::make_tuple(true, pStyle->style, pStyle->len);
    } else {
      if (bsStyle.Left(pStyle->len).Compare(pStyle->name) == 0)
        return std::make_tuple(true, pStyle->style, pStyle->len);
    }
  }
  return std::make_tuple(false, FXFONT_NORMAL, 0);
}

bool CheckSupportThirdPartFont(const ByteString& name, int* PitchFamily) {
  if (name != "MyriadPro")
    return false;
  *PitchFamily &= ~FXFONT_FF_ROMAN;
  return true;
}

void UpdatePitchFamily(uint32_t flags, int* PitchFamily) {
  if (FontStyleIsSerif(flags))
    *PitchFamily |= FXFONT_FF_ROMAN;
  if (FontStyleIsScript(flags))
    *PitchFamily |= FXFONT_FF_SCRIPT;
  if (FontStyleIsFixedPitch(flags))
    *PitchFamily |= FXFONT_FF_FIXEDPITCH;
}

}  // namespace

CFX_FontMapper::CFX_FontMapper(CFX_FontMgr* mgr) : m_pFontMgr(mgr) {}

CFX_FontMapper::~CFX_FontMapper() = default;

void CFX_FontMapper::SetSystemFontInfo(
    std::unique_ptr<SystemFontInfoIface> pFontInfo) {
  if (!pFontInfo)
    return;

  m_pFontInfo = std::move(pFontInfo);
}

uint32_t CFX_FontMapper::GetChecksumFromTT(void* hFont) {
  uint32_t buffer[256];
  m_pFontInfo->GetFontData(
      hFont, kTableTTCF, pdfium::as_writable_bytes(pdfium::make_span(buffer)));

  uint32_t checksum = 0;
  for (auto x : buffer)
    checksum += x;

  return checksum;
}

ByteString CFX_FontMapper::GetPSNameFromTT(void* hFont) {
  uint32_t size = m_pFontInfo->GetFontData(hFont, kTableNAME, {});
  if (!size)
    return ByteString();

  std::vector<uint8_t> buffer(size);
  uint32_t bytes_read = m_pFontInfo->GetFontData(hFont, kTableNAME, buffer);
  return bytes_read == size ? GetNameFromTT(buffer, 6) : ByteString();
}

void CFX_FontMapper::AddInstalledFont(const ByteString& name, int charset) {
  if (!m_pFontInfo)
    return;

  m_FaceArray.push_back({name, static_cast<uint32_t>(charset)});
  if (name == m_LastFamily)
    return;

  bool bLocalized = std::any_of(name.begin(), name.end(), [](const char& c) {
    return static_cast<uint8_t>(c) > 0x80;
  });

  if (bLocalized) {
    void* hFont = m_pFontInfo->GetFont(name.c_str());
    if (!hFont) {
      hFont = m_pFontInfo->MapFont(0, 0, FX_CHARSET_Default, 0, name.c_str());
      if (!hFont)
        return;
    }

    ByteString new_name = GetPSNameFromTT(hFont);
    if (!new_name.IsEmpty())
      m_LocalizedTTFonts.push_back(std::make_pair(new_name, name));
    m_pFontInfo->DeleteFont(hFont);
  }
  m_InstalledTTFonts.push_back(name);
  m_LastFamily = name;
}

void CFX_FontMapper::LoadInstalledFonts() {
  if (!m_pFontInfo || m_bListLoaded)
    return;

  m_pFontInfo->EnumFontList(this);
  m_bListLoaded = true;
}

ByteString CFX_FontMapper::MatchInstalledFonts(const ByteString& norm_name) {
  LoadInstalledFonts();
  int i;
  for (i = pdfium::CollectionSize<int>(m_InstalledTTFonts) - 1; i >= 0; i--) {
    ByteString norm1 = TT_NormalizeName(m_InstalledTTFonts[i].c_str());
    if (norm1 == norm_name)
      return m_InstalledTTFonts[i];
  }
  for (i = pdfium::CollectionSize<int>(m_LocalizedTTFonts) - 1; i >= 0; i--) {
    ByteString norm1 = TT_NormalizeName(m_LocalizedTTFonts[i].first.c_str());
    if (norm1 == norm_name)
      return m_LocalizedTTFonts[i].second;
  }
  return ByteString();
}

RetainPtr<CFX_Face> CFX_FontMapper::UseInternalSubst(CFX_SubstFont* pSubstFont,
                                                     int iBaseFont,
                                                     int italic_angle,
                                                     int weight,
                                                     int pitch_family) {
  if (iBaseFont < kNumStandardFonts) {
    if (m_FoxitFaces[iBaseFont])
      return m_FoxitFaces[iBaseFont];
    Optional<pdfium::span<const uint8_t>> font_data =
        m_pFontMgr->GetBuiltinFont(iBaseFont);
    if (font_data.has_value()) {
      m_FoxitFaces[iBaseFont] =
          m_pFontMgr->NewFixedFace(nullptr, font_data.value(), 0);
      return m_FoxitFaces[iBaseFont];
    }
  }
  pSubstFont->m_bFlagMM = true;
  pSubstFont->m_ItalicAngle = italic_angle;
  if (weight)
    pSubstFont->m_Weight = weight;
  if (FontFamilyIsRoman(pitch_family)) {
    pSubstFont->m_Weight = pSubstFont->m_Weight * 4 / 5;
    pSubstFont->m_Family = "Chrome Serif";
    if (!m_MMFaces[1]) {
      m_MMFaces[1] = m_pFontMgr->NewFixedFace(
          nullptr, m_pFontMgr->GetBuiltinFont(14).value(), 0);
    }
    return m_MMFaces[1];
  }
  pSubstFont->m_Family = "Chrome Sans";
  if (!m_MMFaces[0]) {
    m_MMFaces[0] = m_pFontMgr->NewFixedFace(
        nullptr, m_pFontMgr->GetBuiltinFont(15).value(), 0);
  }
  return m_MMFaces[0];
}

RetainPtr<CFX_Face> CFX_FontMapper::FindSubstFont(const ByteString& name,
                                                  bool bTrueType,
                                                  uint32_t flags,
                                                  int weight,
                                                  int italic_angle,
                                                  int CharsetCP,
                                                  CFX_SubstFont* pSubstFont) {
  if (weight == 0)
    weight = FXFONT_FW_NORMAL;

  if (!(flags & FXFONT_USEEXTERNATTR)) {
    weight = FXFONT_FW_NORMAL;
    italic_angle = 0;
  }
  ByteString SubstName = name;
  SubstName.Remove(' ');
  if (bTrueType && name.GetLength() > 0 && name[0] == '@')
    SubstName = name.Right(name.GetLength() - 1);
  GetStandardFontName(&SubstName);
  if (SubstName == "Symbol" && !bTrueType) {
    pSubstFont->m_Family = "Chrome Symbol";
    pSubstFont->m_Charset = FX_CHARSET_Symbol;
    return UseInternalSubst(pSubstFont, 12, italic_angle, weight, 0);
  }
  if (SubstName == "ZapfDingbats") {
    pSubstFont->m_Family = "Chrome Dingbats";
    pSubstFont->m_Charset = FX_CHARSET_Symbol;
    return UseInternalSubst(pSubstFont, 13, italic_angle, weight, 0);
  }
  int iBaseFont = 0;
  ByteString family;
  ByteString style;
  bool bHasComma = false;
  bool bHasHyphen = false;
  {
    Optional<size_t> pos = SubstName.Find(",", 0);
    if (pos.has_value()) {
      family = SubstName.Left(pos.value());
      GetStandardFontName(&family);
      style = SubstName.Right(SubstName.GetLength() - (pos.value() + 1));
      bHasComma = true;
    } else {
      family = SubstName;
    }
  }
  for (; iBaseFont < 12; iBaseFont++) {
    if (family == ByteStringView(g_Base14FontNames[iBaseFont]))
      break;
  }
  int PitchFamily = 0;
  uint32_t nStyle = FXFONT_NORMAL;
  bool bStyleAvail = false;
  if (iBaseFont < 12) {
    if ((iBaseFont % 4) == 1 || (iBaseFont % 4) == 2)
      nStyle |= FXFONT_FORCE_BOLD;
    if ((iBaseFont % 4) / 2)
      nStyle |= FXFONT_ITALIC;
    if (iBaseFont < 4)
      PitchFamily |= FXFONT_FF_FIXEDPITCH;
    if (iBaseFont >= 8)
      PitchFamily |= FXFONT_FF_ROMAN;
  } else {
    iBaseFont = kNumStandardFonts;
    if (!bHasComma) {
      Optional<size_t> pos = family.ReverseFind('-');
      if (pos.has_value()) {
        style = family.Right(family.GetLength() - (pos.value() + 1));
        family = family.Left(pos.value());
        bHasHyphen = true;
      }
    }
    if (!bHasHyphen) {
      int nLen = family.GetLength();
      bool hasStyleType;
      uint32_t styleType;
      size_t len;
      std::tie(hasStyleType, styleType, len) = GetStyleType(family, true);
      if (hasStyleType) {
        family = family.Left(nLen - len);
        nStyle |= styleType;
      }
    }
    UpdatePitchFamily(flags, &PitchFamily);
  }

  const int old_weight = weight;
  if (FontStyleIsForceBold(nStyle))
    weight = FXFONT_FW_BOLD;

  if (!style.IsEmpty()) {
    int nLen = style.GetLength();
    const char* pStyle = style.c_str();
    int i = 0;
    bool bFirstItem = true;
    ByteString buf;
    while (i < nLen) {
      buf = ParseStyle(pStyle, nLen, i);

      bool hasStyleType;
      uint32_t styleType;
      size_t len;
      std::tie(hasStyleType, styleType, len) = GetStyleType(buf, false);
      if ((i && !bStyleAvail) || (!i && !hasStyleType)) {
        family = SubstName;
        iBaseFont = kNumStandardFonts;
        break;
      }
      if (hasStyleType)
        bStyleAvail = true;

      if (FontStyleIsForceBold(styleType)) {
        // If we're already bold, then we're double bold, use special weight.
        if (FontStyleIsForceBold(nStyle)) {
          weight = FXFONT_FW_BOLD_BOLD;
        } else {
          weight = FXFONT_FW_BOLD;
          nStyle |= FXFONT_FORCE_BOLD;
        }

        bFirstItem = false;
      }
      if (FontStyleIsItalic(styleType) && FontStyleIsForceBold(styleType)) {
        nStyle |= FXFONT_ITALIC;
      } else if (FontStyleIsItalic(styleType)) {
        if (bFirstItem) {
          nStyle |= FXFONT_ITALIC;
        } else {
          family = SubstName;
          iBaseFont = kNumStandardFonts;
        }
        break;
      }
      i += buf.GetLength() + 1;
    }
  }

  if (!m_pFontInfo) {
    return UseInternalSubst(pSubstFont, iBaseFont, italic_angle, old_weight,
                            PitchFamily);
  }

  int Charset = FX_CHARSET_ANSI;
  if (CharsetCP)
    Charset = FX_GetCharsetFromCodePage(CharsetCP);
  else if (iBaseFont == kNumStandardFonts && FontStyleIsSymbolic(flags))
    Charset = FX_CHARSET_Symbol;
  const bool bCJK = FX_CharSetIsCJK(Charset);
  bool bItalic = FontStyleIsItalic(nStyle);

  GetFontFamily(nStyle, &family);
  ByteString match = MatchInstalledFonts(TT_NormalizeName(family.c_str()));
  if (match.IsEmpty() && family != SubstName &&
      (!bHasComma && (!bHasHyphen || (bHasHyphen && !bStyleAvail)))) {
    match = MatchInstalledFonts(TT_NormalizeName(SubstName.c_str()));
  }
  if (match.IsEmpty() && iBaseFont >= kNumStandardFonts) {
    if (!bCJK) {
      if (!CheckSupportThirdPartFont(family, &PitchFamily)) {
        bItalic = italic_angle != 0;
        weight = old_weight;
      }
      Optional<size_t> pos = SubstName.Find("Narrow");
      if (pos.has_value() && pos.value() != 0)
        family = kNarrowFamily;
      pos = SubstName.Find("Condensed");
      if (pos.has_value() && pos.value() != 0)
        family = kNarrowFamily;
    } else {
      pSubstFont->m_bSubstCJK = true;
      if (nStyle)
        pSubstFont->m_WeightCJK = nStyle ? weight : FXFONT_FW_NORMAL;
      if (FontStyleIsItalic(nStyle))
        pSubstFont->m_bItalicCJK = true;
    }
  } else {
    italic_angle = 0;
    if (nStyle == FXFONT_NORMAL)
      weight = FXFONT_FW_NORMAL;
  }

  if (!match.IsEmpty() || iBaseFont < kNumStandardFonts) {
    if (!match.IsEmpty())
      family = match;
    if (iBaseFont < kNumStandardFonts) {
      if (nStyle && !(iBaseFont % 4)) {
        if (FontStyleIsForceBold(nStyle) && FontStyleIsItalic(nStyle))
          iBaseFont += 2;
        else if (FontStyleIsForceBold(nStyle))
          iBaseFont += 1;
        else if (FontStyleIsItalic(nStyle))
          iBaseFont += 3;
      }
      family = g_Base14FontNames[iBaseFont];
    }
  } else if (FontStyleIsItalic(flags)) {
    bItalic = true;
  }
  void* hFont = m_pFontInfo->MapFont(weight, bItalic, Charset, PitchFamily,
                                     family.c_str());
  if (!hFont) {
    if (bCJK) {
      bItalic = italic_angle != 0;
      weight = old_weight;
    }
    if (!match.IsEmpty()) {
      hFont = m_pFontInfo->GetFont(match.c_str());
      if (!hFont) {
        return UseInternalSubst(pSubstFont, iBaseFont, italic_angle, old_weight,
                                PitchFamily);
      }
    } else {
      if (Charset == FX_CHARSET_Symbol) {
#if defined(OS_MACOSX) || defined(OS_ANDROID)
        if (SubstName == "Symbol") {
          pSubstFont->m_Family = "Chrome Symbol";
          pSubstFont->m_Charset = FX_CHARSET_Symbol;
          return UseInternalSubst(pSubstFont, 12, italic_angle, old_weight,
                                  PitchFamily);
        }
#endif
        return FindSubstFont(family, bTrueType, flags & ~FXFONT_SYMBOLIC,
                             weight, italic_angle, 0, pSubstFont);
      }
      if (Charset == FX_CHARSET_ANSI) {
        return UseInternalSubst(pSubstFont, iBaseFont, italic_angle, old_weight,
                                PitchFamily);
      }

      auto it =
          std::find_if(m_FaceArray.begin(), m_FaceArray.end(),
                       [Charset](const FaceData& face) {
                         return face.charset == static_cast<uint32_t>(Charset);
                       });
      if (it == m_FaceArray.end()) {
        return UseInternalSubst(pSubstFont, iBaseFont, italic_angle, old_weight,
                                PitchFamily);
      }
      hFont = m_pFontInfo->GetFont(it->name.c_str());
    }
  }
  if (!hFont)
    return nullptr;

  m_pFontInfo->GetFaceName(hFont, &SubstName);
  if (Charset == FX_CHARSET_Default)
    m_pFontInfo->GetFontCharset(hFont, &Charset);
  uint32_t ttc_size = m_pFontInfo->GetFontData(hFont, kTableTTCF, {});
  uint32_t font_size = m_pFontInfo->GetFontData(hFont, 0, {});
  if (font_size == 0 && ttc_size == 0) {
    m_pFontInfo->DeleteFont(hFont);
    return nullptr;
  }
  RetainPtr<CFX_Face> face;
  if (ttc_size)
    face = GetCachedTTCFace(hFont, ttc_size, font_size);
  else
    face = GetCachedFace(hFont, SubstName, weight, bItalic, font_size);
  if (!face) {
    m_pFontInfo->DeleteFont(hFont);
    return nullptr;
  }
  pSubstFont->m_Family = SubstName;
  pSubstFont->m_Charset = Charset;
  bool bNeedUpdateWeight = false;
  if (FXFT_Is_Face_Bold(face->GetRec()))
    bNeedUpdateWeight = weight != FXFONT_FW_BOLD;
  else
    bNeedUpdateWeight = weight != FXFONT_FW_NORMAL;
  if (bNeedUpdateWeight)
    pSubstFont->m_Weight = weight;
  if (bItalic && !FXFT_Is_Face_Italic(face->GetRec())) {
    if (italic_angle == 0)
      italic_angle = -12;
    else if (abs(italic_angle) < 5)
      italic_angle = 0;
    pSubstFont->m_ItalicAngle = italic_angle;
  }
  m_pFontInfo->DeleteFont(hFont);
  return face;
}

int CFX_FontMapper::GetFaceSize() const {
  return pdfium::CollectionSize<int>(m_FaceArray);
}

bool CFX_FontMapper::IsBuiltinFace(const RetainPtr<CFX_Face>& face) const {
  for (size_t i = 0; i < MM_FACE_COUNT; ++i) {
    if (m_MMFaces[i] == face)
      return true;
  }
  for (size_t i = 0; i < FOXIT_FACE_COUNT; ++i) {
    if (m_FoxitFaces[i] == face)
      return true;
  }
  return false;
}

RetainPtr<CFX_Face> CFX_FontMapper::GetCachedTTCFace(void* hFont,
                                                     uint32_t ttc_size,
                                                     uint32_t font_size) {
  uint32_t checksum = GetChecksumFromTT(hFont);
  RetainPtr<CFX_FontMgr::FontDesc> pFontDesc =
      m_pFontMgr->GetCachedTTCFontDesc(ttc_size, checksum);
  if (!pFontDesc) {
    std::unique_ptr<uint8_t, FxFreeDeleter> pFontData(
        FX_Alloc(uint8_t, ttc_size));
    m_pFontInfo->GetFontData(hFont, kTableTTCF, {pFontData.get(), ttc_size});
    pFontDesc = m_pFontMgr->AddCachedTTCFontDesc(
        ttc_size, checksum, std::move(pFontData), ttc_size);
  }
  ASSERT(ttc_size >= font_size);
  uint32_t font_offset = ttc_size - font_size;
  int face_index =
      GetTTCIndex(pFontDesc->FontData().first(ttc_size), font_offset);
  RetainPtr<CFX_Face> pFace(pFontDesc->GetFace(face_index));
  if (pFace)
    return pFace;

  pFace = m_pFontMgr->NewFixedFace(
      pFontDesc, pFontDesc->FontData().first(ttc_size), face_index);
  if (!pFace)
    return nullptr;

  pFontDesc->SetFace(face_index, pFace.Get());
  return pFace;
}

RetainPtr<CFX_Face> CFX_FontMapper::GetCachedFace(void* hFont,
                                                  ByteString SubstName,
                                                  int weight,
                                                  bool bItalic,
                                                  uint32_t font_size) {
  RetainPtr<CFX_FontMgr::FontDesc> pFontDesc =
      m_pFontMgr->GetCachedFontDesc(SubstName, weight, bItalic);
  if (!pFontDesc) {
    std::unique_ptr<uint8_t, FxFreeDeleter> pFontData(
        FX_Alloc(uint8_t, font_size));
    m_pFontInfo->GetFontData(hFont, 0, {pFontData.get(), font_size});
    pFontDesc = m_pFontMgr->AddCachedFontDesc(SubstName, weight, bItalic,
                                              std::move(pFontData), font_size);
  }
  RetainPtr<CFX_Face> pFace(pFontDesc->GetFace(0));
  if (pFace)
    return pFace;

  pFace = m_pFontMgr->NewFixedFace(pFontDesc,
                                   pFontDesc->FontData().first(font_size),
                                   m_pFontInfo->GetFaceIndex(hFont));
  if (!pFace)
    return nullptr;

  pFontDesc->SetFace(0, pFace.Get());
  return pFace;
}

// static
Optional<CFX_FontMapper::StandardFont> CFX_FontMapper::GetStandardFontName(
    ByteString* name) {
  const auto* end = std::end(g_AltFontNames);
  const auto* found =
      std::lower_bound(std::begin(g_AltFontNames), end, name->c_str(),
                       [](const AltFontName& element, const char* name) {
                         return FXSYS_stricmp(element.m_pName, name) < 0;
                       });
  if (found == end || FXSYS_stricmp(found->m_pName, name->c_str()))
    return {};

  *name = g_Base14FontNames[static_cast<size_t>(found->m_Index)];
  return found->m_Index;
}

// static
bool CFX_FontMapper::IsSymbolicFont(StandardFont font) {
  return font == StandardFont::kSymbol || font == StandardFont::kDingbats;
}

// static
bool CFX_FontMapper::IsFixedFont(StandardFont font) {
  return font == StandardFont::kCourier || font == StandardFont::kCourierBold ||
         font == StandardFont::kCourierBoldOblique ||
         font == StandardFont::kCourierOblique;
}
