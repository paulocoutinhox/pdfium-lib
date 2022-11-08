#import "PDFiumPage.h"
#import "PDFiumDocument.h"
#import "fpdf_text.h"
#import "fpdf_transformpage.h"

@interface PDFiumPage()

@end


@implementation PDFiumPage {
    PDFiumDocument* _document;
    FPDF_PAGE _pdfiumPageRef;
    FPDF_TEXTPAGE _pdfiumTextPageRef;
    NSString* _rawText;
    NSMutableString* _correctedText;
}

- (instancetype _Nullable) initWithDocument:(PDFiumDocument* _Nonnull) document pageIndex:(NSInteger) pageIndex {
    _document  = document;
    _index = pageIndex;
    _pdfiumPageRef = FPDF_LoadPage(_document.pdfiumDocumentRef, (int) self.index);
    if (_pdfiumPageRef == nil) {
        return nil;
    }
    _pdfiumTextPageRef = FPDFText_LoadPage(_pdfiumPageRef);
    if (_pdfiumTextPageRef == nil) {
        return nil;
    }
    _charCount = FPDFText_CountChars(_pdfiumTextPageRef);
    return self;
}

- (void)dealloc {
    if (_pdfiumPageRef)  {
        FPDF_ClosePage(_pdfiumPageRef);
    }
}

- (CGRect) boundingBox {
    FS_RECTF fsRect;
    if (FPDF_GetPageBoundingBox(_pdfiumPageRef, &fsRect)) {
        CGRect rect = CGRectMake(fsRect.left,
                                 fsRect.bottom,
                                 fsRect.right - fsRect.left,
                                 fsRect.top - fsRect.bottom);
        return rect;
    }
    return CGRectNull;
}

- (CGRect) cropbox {
    float left, top, right, bottom;
    if (FPDFPage_GetMediaBox(_pdfiumPageRef, &left, &bottom, &right, &top)) {
        CGRect rect = CGRectMake(left, bottom, right-left, top-bottom);
        return rect;
    }
    return CGRectNull;
}

- (CGRect) mediabox {
    float left, top, right, bottom;
    if (FPDFPage_GetCropBox(_pdfiumPageRef, &left, &bottom, &right, &top)) {
        CGRect rect = CGRectMake(left, bottom, right-left, top-bottom);
        return rect;
    }
    return CGRectNull;
}

- (NSString* _Nonnull) text {
    if (_correctedText == nil) {
        _correctedText = [self correctedStringFromOriginalString:self.rawText];
    }
    return _correctedText;
}

- (NSString* _Nonnull) rawText {
    if (_rawText == nil) {
        int charCount = FPDFText_CountChars(_pdfiumTextPageRef);
        unsigned int bufferSize = (charCount+1)*2;
        unsigned short* buffer = malloc(bufferSize);
        FPDFText_GetText(_pdfiumTextPageRef, 0, charCount, buffer);
        NSData* data = [NSData dataWithBytes:buffer length:bufferSize-1];
        _rawText = [[NSString alloc] initWithData:data encoding:NSUTF16LittleEndianStringEncoding];
        free(buffer);
        if (_rawText == nil)
            _rawText = @"";
    }
    return _rawText;
}


- (NSString* _Nonnull) textInRect:(CGRect) rect {
    int charCount = FPDFText_GetBoundedText(_pdfiumTextPageRef,
                            rect.origin.x,
                            rect.origin.y + rect.size.height,
                            rect.origin.x + rect.size.width,
                            rect.origin.y,
                            NULL, 0);
    unsigned int bufferSize = (charCount+1)*2;
    unsigned short* buffer = malloc(bufferSize);
    FPDFText_GetBoundedText(_pdfiumTextPageRef,
                            rect.origin.x,
                            rect.origin.y + rect.size.height,
                            rect.origin.x + rect.size.width,
                            rect.origin.y,
                            buffer, charCount);
    NSData* data = [NSData dataWithBytes:buffer length:bufferSize-1];
    NSMutableString* text = [[NSMutableString alloc] initWithData:data encoding:NSUTF16LittleEndianStringEncoding];
    free(buffer);
    return [self correctedStringFromOriginalString:text];
}

- (NSUInteger) textLocationFromPoint:(CGPoint) pagePoint tolerance: (double) tolerance {
    int locationOnPage = FPDFText_GetCharIndexAtPos(_pdfiumTextPageRef, pagePoint.x, pagePoint.y, tolerance, tolerance);
    if (locationOnPage == -1)
        return NSNotFound;
    return locationOnPage;
}

- (CGRect) rectForCharacterIndex: (NSInteger) textIndex {
    int originalIndex = (int) textIndex;
    double left, top, right, bottom;
    FPDFText_GetCharBox(_pdfiumTextPageRef, originalIndex, &left, &right, &bottom, &top);
    CGRect rect = CGRectMake(left, bottom, right-left, top-bottom);
    unichar ch = [_correctedText characterAtIndex:textIndex];
    if (ch == ' ' || ch == '\n') {
        rect.size = CGSizeZero;
    }
    return rect;
}

- (CGFloat) fontSizeForCharacterIndex: (NSInteger) textIndex {
    double fontSize = FPDFText_GetFontSize(_pdfiumTextPageRef, (int) textIndex);
    return fontSize;
}

- (NSArray* _Nonnull) rectsForTextRange: (NSRange) range {
    NSRange correctedRange =range;
    int rectCount = FPDFText_CountRects(_pdfiumTextPageRef, (int) correctedRange.location, (int) correctedRange.length);
    NSMutableArray* rects = [[NSMutableArray alloc] init];
    for (int rectIndex = 0; rectIndex < rectCount; rectIndex++) {
        double left, top, right, bottom;
        FPDFText_GetRect(_pdfiumTextPageRef, rectIndex, &left, &top, &right, &bottom);
        CGRect rect = CGRectMake(left, bottom, right-left, top-bottom);
        //[rects addObject:[NSValue valueWithCGRect:rect]];
    }
    return rects;
}

- (NSMutableString*) correctedStringFromOriginalString: (NSString*) originalString {
    NSMutableString* correctedString = [NSMutableString stringWithString: originalString];
    [correctedString replaceOccurrencesOfString:@"\u00A0" withString:@" " options:NSLiteralSearch range:NSMakeRange(0, correctedString.length)];
    [correctedString replaceOccurrencesOfString:@"\uFFFE" withString:@"-" options:NSLiteralSearch range:NSMakeRange(0, correctedString.length)];
    [correctedString replaceOccurrencesOfString:@"\r\n" withString:@" \n" options:NSLiteralSearch range:NSMakeRange(0, correctedString.length)];
    return correctedString;
}

@end
