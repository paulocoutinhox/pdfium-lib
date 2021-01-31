#include <iostream>
#include <cmath>

#include "fpdfview.h"

int main(int argc, char **argv)
{
    std::cout << "Starting..." << std::endl;

    FPDF_LIBRARY_CONFIG config;
    config.version = 2;
    config.m_pUserFontPaths = nullptr;
    config.m_pIsolate = nullptr;
    config.m_v8EmbedderSlot = 0;

    FPDF_InitLibraryWithConfig(&config);

    std::cout << "Loading PDF..." << std::endl;

    FPDF_STRING testDoc = "f1.pdf";
    FPDF_DOCUMENT doc = FPDF_LoadDocument(testDoc, nullptr);

    std::cout << "Checking PDF..." << std::endl;

    if (!doc)
    {
        unsigned long err = FPDF_GetLastError();
        std::cout << "Load pdf docs unsuccessful: ";

        switch (err)
        {
        case FPDF_ERR_SUCCESS:
            std::cout << "Success" << std::endl;
            break;
        case FPDF_ERR_UNKNOWN:
            std::cout << "Unknown error" << std::endl;
            break;
        case FPDF_ERR_FILE:
            std::cout << "File not found or could not be opened" << std::endl;
            break;
        case FPDF_ERR_FORMAT:
            std::cout << "File not in PDF format or corrupted" << std::endl;
            break;
        case FPDF_ERR_PASSWORD:
            std::cout << "Password required or incorrect password" << std::endl;
            break;
        case FPDF_ERR_SECURITY:
            std::cout << "Unsupported security scheme" << std::endl;
            break;
        case FPDF_ERR_PAGE:
            std::cout << "Page not found or content error" << std::endl;
            break;
        default:
            std::cout << "Unknown error " << err << std::endl;
        }

        std::cout << std::endl;

        FPDF_DestroyLibrary();

        return EXIT_FAILURE;
    }

    int pageCount = FPDF_GetPageCount(doc);
    std::cout << "Total of pages: " << pageCount << std::endl;

    if (pageCount > 0)
    {
        // page size
        double_t pageWidth;
        double_t pageHeight;

        FPDF_GetPageSizeByIndex(doc, 0, &pageWidth, &pageHeight);

        std::cout << "First page has size: " << floor(pageWidth * 0.0352778) << "cm X " << floor(pageHeight * 0.0352778) << "cm" << std::endl;

        // render page
        FPDF_PAGE page = FPDF_LoadPage(doc, 0);

        uint8_t buffer[(int)pageWidth * (int)pageHeight * 4];

        FPDF_BITMAP createdpages = FPDFBitmap_CreateEx((int)pageWidth, (int)pageHeight, 4, buffer, (int)pageWidth * 4);
        uint background = 0xFFFFFFFF;
        FPDFBitmap_FillRect(createdpages, 0, 0, (int)pageWidth, (int)pageHeight, background);
        FPDF_RenderPageBitmap(createdpages, page, 0, 0, (int)pageWidth, (int)pageHeight, 0, FPDF_ANNOT);
        FPDFBitmap_Destroy(createdpages);
        FPDF_ClosePage(page);

        std::cout << "Buffer size: " << (sizeof(buffer) / sizeof((buffer)[0])) << std::endl;
    }

    FPDF_CloseDocument(doc);

    FPDF_DestroyLibrary();

    return EXIT_SUCCESS;
}