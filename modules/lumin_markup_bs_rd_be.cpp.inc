// Inserted into fpdfsdk/fpdf_annot.cpp by patch.py (Lumin: /BS, /RD, /BE for Square/Circle).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

namespace {

bool LuminAnnotIsSquareOrCircle(FPDF_ANNOTATION annot) {
  const FPDF_ANNOTATION_SUBTYPE st = FPDFAnnot_GetSubtype(annot);
  return st == FPDF_ANNOT_SQUARE || st == FPDF_ANNOT_CIRCLE;
}

void LuminCopyAsciiz(const char* src, char* dst, int cap) {
  if (!dst || cap < 1)
    return;
  if (!src) {
    dst[0] = '\0';
    return;
  }
  int i = 0;
  for (; i < cap - 1 && src[i]; ++i)
    dst[i] = src[i];
  dst[i] = '\0';
}

int LuminParseDashCommaToArray(const char* dashComma, float* out, int maxOut) {
  if (!out || maxOut < 1)
    return 0;
  if (!dashComma || !dashComma[0])
    return 0;
  int n = 0;
  const char* p = dashComma;
  while (*p && n < maxOut) {
    while (*p == ' ' || *p == ',')
      ++p;
    if (!*p)
      break;
    char* endp = nullptr;
    float v = std::strtof(p, &endp);
    if (endp == p)
      break;
    out[n++] = v;
    p = endp;
  }
  return n;
}

float LuminArrayGetFloat(const CPDF_Array* arr, size_t i) {
  if (!arr || i >= arr->size())
    return 0.0f;
  RetainPtr<const CPDF_Object> o = arr->GetObjectAt(i);
  return o && o->IsNumber() ? o->GetNumber() : 0.0f;
}

void LuminCopySNameToBuf(const CPDF_Object* sObj, char* outS, int sLen) {
  if (!outS || sLen < 1)
    return;
  outS[0] = '\0';
  if (!sObj)
    return;
  if (const CPDF_Name* nm = sObj->AsName()) {
    LuminCopyAsciiz(nm->GetString().c_str(), outS, sLen);
  }
}

}  // namespace

FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_GetRectDiff(FPDF_ANNOTATION annot,
                      float* outLeft,
                      float* outTop,
                      float* outRight,
                      float* outBottom) {
  if (!outLeft || !outTop || !outRight || !outBottom)
    return false;
  if (!LuminAnnotIsSquareOrCircle(annot))
    return false;
  const CPDF_Dictionary* annot_dict = GetAnnotDictFromFPDFAnnotation(annot);
  if (!annot_dict)
    return false;
  RetainPtr<const CPDF_Array> rd = annot_dict->GetArrayFor("RD");
  if (!rd || rd->size() < 4)
    return false;
  *outLeft = LuminArrayGetFloat(rd.Get(), 0);
  *outTop = LuminArrayGetFloat(rd.Get(), 1);
  *outRight = LuminArrayGetFloat(rd.Get(), 2);
  *outBottom = LuminArrayGetFloat(rd.Get(), 3);
  return true;
}

FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_SetRectDiff(FPDF_ANNOTATION annot,
                        float left,
                        float top,
                        float right,
                        float bottom) {
  if (!LuminAnnotIsSquareOrCircle(annot))
    return false;
  RetainPtr<CPDF_Dictionary> annot_dict =
      GetMutableAnnotDictFromFPDFAnnotation(annot);
  if (!annot_dict)
    return false;
  if (left == 0.0f && top == 0.0f && right == 0.0f && bottom == 0.0f) {
    annot_dict->RemoveFor("RD");
  } else {
    RetainPtr<CPDF_Array> rd = annot_dict->GetOrCreateArrayFor("RD");
    rd->Clear();
    rd->AppendNew<CPDF_Number>(left);
    rd->AppendNew<CPDF_Number>(top);
    rd->AppendNew<CPDF_Number>(right);
    rd->AppendNew<CPDF_Number>(bottom);
  }
  annot_dict->RemoveFor(pdfium::annotation::kAP);
  return true;
}

FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_GetBorderStyleDict(FPDF_ANNOTATION annot,
                             char* outS,
                             int sLen,
                             char* outDashComma,
                             int dashCommaLen,
                             float* wOut) {
  if (!wOut)
    return false;
  *wOut = 0.0f;
  if (outS && sLen > 0)
    outS[0] = '\0';
  if (outDashComma && dashCommaLen > 0)
    outDashComma[0] = '\0';
  if (!LuminAnnotIsSquareOrCircle(annot))
    return false;
  const CPDF_Dictionary* annot_dict = GetAnnotDictFromFPDFAnnotation(annot);
  if (!annot_dict)
    return false;
  RetainPtr<const CPDF_Dictionary> bs = annot_dict->GetDictFor("BS");
  if (!bs)
    return false;
  RetainPtr<const CPDF_Object> sObjS = bs->GetObjectFor("S");
  LuminCopySNameToBuf(sObjS ? sObjS.Get() : nullptr, outS, sLen);
  RetainPtr<const CPDF_Array> d = bs->GetArrayFor("D");
  if (d && d->size() > 0 && outDashComma && dashCommaLen > 0) {
    std::string acc;
    for (size_t i = 0; i < d->size(); ++i) {
      if (i)
        acc += ',';
      char b[32];
      std::snprintf(b, sizeof(b), "%g", static_cast<double>(LuminArrayGetFloat(d.Get(), i)));
      acc += b;
    }
    LuminCopyAsciiz(acc.c_str(), outDashComma, dashCommaLen);
  }
  RetainPtr<const CPDF_Object> wobj = bs->GetObjectFor("W");
  if (wobj && wobj->IsNumber())
    *wOut = wobj->GetNumber();
  return true;
}

FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_SetBorderStyleDict(FPDF_ANNOTATION annot,
                              const char* sName,
                              const char* dashComma,
                              float w) {
  if (!LuminAnnotIsSquareOrCircle(annot))
    return false;
  RetainPtr<CPDF_Dictionary> annot_dict =
      GetMutableAnnotDictFromFPDFAnnotation(annot);
  if (!annot_dict)
    return false;
  if (!sName || !sName[0]) {
    annot_dict->RemoveFor("BS");
    annot_dict->RemoveFor(pdfium::annotation::kAP);
    return true;
  }
  RetainPtr<CPDF_Dictionary> bs = annot_dict->GetOrCreateDictFor("BS");
  bs->SetNewFor<CPDF_Name>("S", ByteString(sName));
  float dtmp[32];
  int dcount = LuminParseDashCommaToArray(dashComma, dtmp, 32);
  if (dcount > 0 && sName[0] == 'D' && sName[1] == '\0') {
    RetainPtr<CPDF_Array> darr = bs->GetOrCreateArrayFor("D");
    darr->Clear();
    for (int i = 0; i < dcount; ++i)
      darr->AppendNew<CPDF_Number>(dtmp[i]);
  } else {
    bs->RemoveFor("D");
  }
  if (w > 0.0f)
    bs->SetNewFor<CPDF_Number>("W", w);
  else
    bs->RemoveFor("W");
  annot_dict->RemoveFor(pdfium::annotation::kAP);
  return true;
}

FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_GetBorderEffectDict(FPDF_ANNOTATION annot,
                                char* outS,
                                int sLen,
                                float* iOut) {
  if (!iOut)
    return false;
  *iOut = 0.0f;
  if (outS && sLen > 0)
    outS[0] = '\0';
  if (!LuminAnnotIsSquareOrCircle(annot))
    return false;
  const CPDF_Dictionary* annot_dict = GetAnnotDictFromFPDFAnnotation(annot);
  if (!annot_dict)
    return false;
  RetainPtr<const CPDF_Dictionary> be = annot_dict->GetDictFor("BE");
  if (!be)
    return false;
  RetainPtr<const CPDF_Object> sObjE = be->GetObjectFor("S");
  LuminCopySNameToBuf(sObjE ? sObjE.Get() : nullptr, outS, sLen);
  RetainPtr<const CPDF_Object> iobj = be->GetObjectFor("I");
  if (iobj && iobj->IsNumber())
    *iOut = iobj->GetNumber();
  return true;
}

FPDF_EXPORT FPDF_BOOL FPDF_CALLCONV
FPDFAnnot_SetBorderEffectDict(FPDF_ANNOTATION annot,
                                const char* sName,
                                float intensity) {
  if (!LuminAnnotIsSquareOrCircle(annot))
    return false;
  RetainPtr<CPDF_Dictionary> annot_dict =
      GetMutableAnnotDictFromFPDFAnnotation(annot);
  if (!annot_dict)
    return false;
  if (!sName || !sName[0]) {
    annot_dict->RemoveFor("BE");
  } else {
    RetainPtr<CPDF_Dictionary> be = annot_dict->GetOrCreateDictFor("BE");
    be->SetNewFor<CPDF_Name>("S", ByteString(sName));
    be->SetNewFor<CPDF_Number>("I", intensity);
  }
  annot_dict->RemoveFor(pdfium::annotation::kAP);
  return true;
}
