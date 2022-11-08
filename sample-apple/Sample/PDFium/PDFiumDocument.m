#import "PDFiumDocument.h"
#import "fpdf_doc.h"

@implementation PDFiumDocument {
}

+ (void)initialize {
    static dispatch_once_t onceToken = 0;
    dispatch_once(&onceToken, ^{
        FPDF_LIBRARY_CONFIG config;
        config.version = 2;
        config.m_pUserFontPaths = NULL;
        config.m_pIsolate = NULL;
        config.m_v8EmbedderSlot = 0;
        FPDF_InitLibraryWithConfig(&config);
    });
}

- (instancetype _Nullable) initWithURL:(NSURL * _Nonnull)url password:(NSString* _Nullable) password {
    FPDF_STRING cpath = (char*) url.path.UTF8String;
    FPDF_STRING cpassword = (char*) password.UTF8String;
    _pdfiumDocumentRef = FPDF_LoadDocument(cpath, cpassword);
    if (_pdfiumDocumentRef == nil) {
        return nil;
    }
    _pageCount = FPDF_GetPageCount(_pdfiumDocumentRef);
    return self;
}

- (void)dealloc {
    FPDF_CloseDocument(_pdfiumDocumentRef);
}

@end
