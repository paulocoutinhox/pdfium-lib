#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include "fpdfview.h"
#include "fpdf_dataavail.h"

#include <emscripten.h>

EMSCRIPTEN_KEEPALIVE void PDFium_Init()
{
    FPDF_LIBRARY_CONFIG config;
    config.version = 2;
    config.m_pUserFontPaths = NULL;
    config.m_pIsolate = NULL;
    config.m_v8EmbedderSlot = 0;

    FPDF_InitLibraryWithConfig(&config);
}

EMSCRIPTEN_KEEPALIVE FPDF_DOCUMENT PDFium_CreateDocFromBuffer(void *buffer, int length)
{
    return FPDF_LoadMemDocument(buffer, length, "");
}

EMSCRIPTEN_KEEPALIVE double *PDFium_GetPageSizeByIndex(FPDF_DOCUMENT doc, int pageIndex)
{
    double *result = malloc(2 * sizeof(double));

    double pageWidth;
    double pageHeight;

    FPDF_GetPageSizeByIndex(doc, pageIndex, &pageWidth, &pageHeight);

    result[0] = pageWidth;
    result[1] = pageHeight;

    return result;
}

EMSCRIPTEN_KEEPALIVE char *PDFium_GetRenderPageBitmap(FPDF_DOCUMENT doc, int pageIndex)
{
    // page size
    double pageWidth;
    double pageHeight;

    FPDF_GetPageSizeByIndex(doc, pageIndex, &pageWidth, &pageHeight);

    // render page
    FPDF_PAGE page = FPDF_LoadPage(doc, pageIndex);

    char *result = malloc((int)pageWidth * (int)pageHeight * 4);

    FPDF_BITMAP pageBitmap = FPDFBitmap_CreateEx((int)pageWidth, (int)pageHeight, FPDFBitmap_BGRA, result, (int)pageWidth * 4);
    int background = 0xFFFFFFFF;

    FPDFBitmap_FillRect(pageBitmap, 0, 0, (int)pageWidth, (int)pageHeight, background);
    FPDF_RenderPageBitmap(pageBitmap, page, 0, 0, (int)pageWidth, (int)pageHeight, 0, FPDF_ANNOT | FPDF_PRINTING);
    FPDFBitmap_Destroy(pageBitmap);
    FPDF_ClosePage(page);

    return result;
}

EMSCRIPTEN_KEEPALIVE char *PDFium_GetLastError()
{
    char *result = "";

    unsigned long err = FPDF_GetLastError();

    switch (err)
    {
    case FPDF_ERR_SUCCESS:
        result = "success";
        break;
    case FPDF_ERR_UNKNOWN:
        result = "unknown error";
        break;
    case FPDF_ERR_FILE:
        result = "file not found or could not be opened";
        break;
    case FPDF_ERR_FORMAT:
        result = "file not in PDF format or corrupted";
        break;
    case FPDF_ERR_PASSWORD:
        result = "password required or incorrect password";
        break;
    case FPDF_ERR_SECURITY:
        result = "unsupported security scheme";
        break;
    case FPDF_ERR_PAGE:
        result = "page not found or content error";
        break;
    default:
        result = "unknown error";
    }

    return result;
}