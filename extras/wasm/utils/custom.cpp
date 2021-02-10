#include <climits>
#include <string>
#include <vector>

#include "fpdfview.h"
#include "fpdf_dataavail.h"

#include <emscripten.h>

#ifdef __cplusplus
extern "C"
{
#endif

    EMSCRIPTEN_KEEPALIVE void PDFium_Init();
    EMSCRIPTEN_KEEPALIVE FPDF_DOCUMENT PDFium_CreateDocFromBuffer(void *buffer, int length);
    EMSCRIPTEN_KEEPALIVE double *PDFium_GetPageSizeByIndex(FPDF_DOCUMENT doc, int pageIndex);
    EMSCRIPTEN_KEEPALIVE unsigned char *PDFium_GetRenderPageBitmap(FPDF_DOCUMENT doc, int pageIndex, bool reverseByteOrder);
    EMSCRIPTEN_KEEPALIVE int PDFium_GetRenderPageDataSize(FPDF_DOCUMENT doc, int pageIndex);
    EMSCRIPTEN_KEEPALIVE const char *PDFium_GetLastError();

#ifdef __cplusplus
}
#endif

const double PDF_SCALE = 2.0;

void PDFium_Init()
{
    // https://source.chromium.org/chromium/chromium/src/+/master:third_party/pdfium/samples/pdfium_test.cc;l=1172

    FPDF_LIBRARY_CONFIG config;
    config.version = 3;
    config.m_pUserFontPaths = nullptr;
    config.m_pIsolate = nullptr;
    config.m_v8EmbedderSlot = 0;
    config.m_pPlatform = nullptr;

    FPDF_InitLibraryWithConfig(&config);
}

bool PDFium_CheckDimensions(int stride, int width, int height)
{
    if (stride < 0 || width < 0 || height < 0)
    {
        return false;
    }

    if (height > 0 && stride > INT_MAX / height)
    {
        return false;
    }

    return true;
}

FPDF_DOCUMENT PDFium_CreateDocFromBuffer(void *buffer, int length)
{
    return FPDF_LoadMemDocument(buffer, length, "");
}

double *PDFium_GetPageSizeByIndex(FPDF_DOCUMENT doc, int pageIndex)
{
    double *result = static_cast<double *>(malloc(2 * sizeof(double)));

    double pageWidth;
    double pageHeight;

    FPDF_GetPageSizeByIndex(doc, pageIndex, &pageWidth, &pageHeight);

    pageWidth = pageWidth * PDF_SCALE;
    pageHeight = pageHeight * PDF_SCALE;

    result[0] = pageWidth;
    result[1] = pageHeight;

    return result;
}

unsigned char *PDFium_GetRenderPageBitmap(FPDF_DOCUMENT doc, int pageIndex, bool reverseByteOrder)
{
    // page size
    double pageWidth;
    double pageHeight;

    FPDF_GetPageSizeByIndex(doc, pageIndex, &pageWidth, &pageHeight);

    pageWidth = pageWidth * PDF_SCALE;
    pageHeight = pageHeight * PDF_SCALE;

    // render page
    FPDF_PAGE page = FPDF_LoadPage(doc, pageIndex);

    unsigned char *result = static_cast<unsigned char *>(malloc((int)pageWidth * (int)pageHeight * 4));

    FPDF_BITMAP pageBitmap = FPDFBitmap_CreateEx((int)pageWidth, (int)pageHeight, FPDFBitmap_BGRA, result, (int)pageWidth * 4);
    int background = 0xFFFFFFFF;

    FPDFBitmap_FillRect(pageBitmap, 0, 0, (int)pageWidth, (int)pageHeight, background);

    int flags = 0;

    if (reverseByteOrder)
    {
        flags = FPDF_ANNOT | FPDF_PRINTING | FPDF_REVERSE_BYTE_ORDER;
    }
    else
    {
        flags = FPDF_ANNOT | FPDF_PRINTING;
    }

    FPDF_RenderPageBitmap(pageBitmap, page, 0, 0, (int)pageWidth, (int)pageHeight, 0, flags);
    FPDFBitmap_Destroy(pageBitmap);
    FPDF_ClosePage(page);

    return result;
}

int PDFium_GetRenderPageDataSize(FPDF_DOCUMENT doc, int pageIndex)
{
    // page size
    double pageWidth;
    double pageHeight;

    FPDF_GetPageSizeByIndex(doc, pageIndex, &pageWidth, &pageHeight);

    pageWidth = pageWidth * PDF_SCALE;
    pageHeight = pageHeight * PDF_SCALE;

    return (int)((int)pageWidth * (int)pageHeight * 4);
}

const char *PDFium_GetLastError()
{
    unsigned long err = FPDF_GetLastError();

    switch (err)
    {
    case FPDF_ERR_SUCCESS:
        return "success";
        break;
    case FPDF_ERR_UNKNOWN:
        return "unknown error";
        break;
    case FPDF_ERR_FILE:
        return "file not found or could not be opened";
        break;
    case FPDF_ERR_FORMAT:
        return "file not in PDF format or corrupted";
        break;
    case FPDF_ERR_PASSWORD:
        return "password required or incorrect password";
        break;
    case FPDF_ERR_SECURITY:
        return "unsupported security scheme";
        break;
    case FPDF_ERR_PAGE:
        return "page not found or content error";
        break;
    default:
        return "unknown error";
    }

    return "";
}