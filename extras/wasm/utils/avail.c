#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include "fpdfview.h"
#include "fpdf_dataavail.h"

FPDF_BOOL Is_Data_Avail(FX_FILEAVAIL *avail, size_t offset, size_t size)
{
    return 1;
}

int GetBlock(void *param, unsigned long position, unsigned char *pBuf, unsigned long size)
{
    memcpy(pBuf, ((unsigned char*)param) + position, size);
    return size;
}

FPDF_AVAIL createDocFromBuffer(void *buffer, int length) {
    FPDF_FILEACCESS file_access;
    memset(&file_access, '\0', sizeof(file_access));
    file_access.m_FileLen = length;
    file_access.m_GetBlock = GetBlock;
    file_access.m_Param = buffer;

    FX_FILEAVAIL file_avail;
    memset(&file_avail, '\0', sizeof(file_avail));
    file_avail.version = 1;
    file_avail.IsDataAvail = Is_Data_Avail;

    return FPDFAvail_Create(&file_avail, &file_access);
}
