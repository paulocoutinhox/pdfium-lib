#include <iostream>

#include "fpdfview.h"

int main(int argc, char **argv)
{
    std::cout << "Opening PDF..." << std::endl;

    FPDF_LIBRARY_CONFIG config;
    config.version = 2;
    config.m_pUserFontPaths = nullptr;
    config.m_pIsolate = nullptr;
    config.m_v8EmbedderSlot = 0;

    FPDF_InitLibraryWithConfig(&config);

    FPDF_STRING testDoc = "f1.pdf";
    FPDF_DOCUMENT doc = FPDF_LoadDocument(testDoc, nullptr);

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

    FPDF_CloseDocument(doc);

    FPDF_DestroyLibrary();

    return EXIT_SUCCESS;
}