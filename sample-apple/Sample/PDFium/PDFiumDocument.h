@import Foundation;

#import "fpdf_doc.h"

NS_ASSUME_NONNULL_BEGIN

@interface PDFiumDocument : NSObject

@property (nullable, nonatomic) FPDF_DOCUMENT pdfiumDocumentRef;
@property (nonatomic) int pageCount;

- (instancetype _Nullable) initWithURL:(NSURL * _Nonnull)url password:(NSString* _Nullable) password;

@end

NS_ASSUME_NONNULL_END
