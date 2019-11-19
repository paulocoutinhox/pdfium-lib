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
        fprintf(stderr, "Load pdf docs unsuccessful: ");
        switch (err)
        {
        case FPDF_ERR_SUCCESS:
            fprintf(stderr, "Success");
            break;
        case FPDF_ERR_UNKNOWN:
            fprintf(stderr, "Unknown error");
            break;
        case FPDF_ERR_FILE:
            fprintf(stderr, "File not found or could not be opened");
            break;
        case FPDF_ERR_FORMAT:
            fprintf(stderr, "File not in PDF format or corrupted");
            break;
        case FPDF_ERR_PASSWORD:
            fprintf(stderr, "Password required or incorrect password");
            break;
        case FPDF_ERR_SECURITY:
            fprintf(stderr, "Unsupported security scheme");
            break;
        case FPDF_ERR_PAGE:
            fprintf(stderr, "Page not found or content error");
            break;
        default:
            fprintf(stderr, "Unknown error %ld", err);
        }

        fprintf(stderr, ".\n");
        FPDF_DestroyLibrary();

        return EXIT_FAILURE;
    }

    int pageCount = FPDF_GetPageCount(doc);
    std::cout << "Total of pages: " << pageCount << std::endl;
    
    FPDF_CloseDocument(doc);

    FPDF_DestroyLibrary();

    return EXIT_SUCCESS;
}