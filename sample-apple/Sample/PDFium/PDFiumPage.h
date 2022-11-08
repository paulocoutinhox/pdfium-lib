@import Foundation;
@import CoreGraphics;

NS_ASSUME_NONNULL_BEGIN

@class PDFiumDocument;

@interface PDFiumPage: NSObject

@property (nonatomic) NSInteger index;
@property (nonatomic) NSInteger charCount;
@property (nonatomic, readonly) CGRect boundingBox;
@property (nonatomic, readonly) CGRect cropBox;
@property (nonatomic, readonly) CGRect mediaBox;
@property (nonatomic, readonly, nonnull) NSString* text;
@property (nonatomic, readonly, nonnull) NSString* rawText;

- (instancetype _Nullable) initWithDocument:(PDFiumDocument* _Nonnull) document pageIndex:(NSInteger) pageIndex;
- (NSString* _Nonnull) textInRect:(CGRect) rect;
- (NSUInteger) textLocationFromPoint:(CGPoint) pagePoint tolerance: (double) tolerance;
- (CGRect) rectForCharacterIndex: (NSInteger) textIndex;
- (CGFloat) fontSizeForCharacterIndex: (NSInteger) textIndex;
- (NSArray* _Nonnull) rectsForTextRange: (NSRange) range;

@end

NS_ASSUME_NONNULL_END
