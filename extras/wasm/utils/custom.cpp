#include "fpdfview.h"
#include <emscripten.h>

#ifdef __cplusplus
extern "C"
{
#endif

    EMSCRIPTEN_KEEPALIVE void PDFium_Init();

#ifdef __cplusplus
}
#endif

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
