import Foundation
import PDFKit

class VDPDFPage {

    var index: Int

    var characterCount: Int {
        guard let pdfiumPage = self.pdfiumPage else { return 0 }
        return Int(pdfiumPage.charCount)
    }

    var pkPDFPage: PDFPage? {
        return document?.pkPDFDocument.page(at: index)
    }

    weak var document: VDPDFDocument?

    lazy var text: String? = {
        guard let pdfiumPage = self.pdfiumPage else { return nil }
        let rawPageText = pdfiumPage.text
        let pageText = rawPageText.cleanedStringForPDFium()
        return pageText
    }()

    var layoutString: String {
        guard let text = self.text else { return "" }
        var layoutString: String = ""
        for i in 0..<text.count {
            let index = text.index(text.startIndex, offsetBy: i)
            let char = text[index]
            if char != " " && char != "\n" {
                let rect = (pdfiumPage?.rect(forCharacterIndex: i))!
                let rectString = "(\(Int(round(rect.origin.x*10))), \(Int(round(rect.origin.y*10))), \(Int(round(rect.width*10))), \(Int(round(rect.height*10))))"
                let charString = "\(char): \(rectString) (\(i))\n"
                layoutString += charString
            }
        }
        return layoutString
    }

    /*
    for i in 0..<100 {
        let start = Int.random(in: 0..<characterCount)
        let startIndex = pageText.index(pageText.startIndex, offsetBy: start)
        let text1 = pageText[startIndex]
        let rect = pdfiumPage.rect(forCharacterIndex: Int32(start))
        let point = CGPoint(x: rect.origin.x + rect.width/2.0, y: rect.origin.y + rect.height/2.0)
        let verify: Int = Int(pdfiumPage.textLocation(from: point, tolerance: 1.0))
        let verifyIndex = pageText.index(pageText.startIndex, offsetBy: verify)
        let text2 = pageText[verifyIndex]
        if text1 != text2 {
            print("Error: \(text1):\(text2) at \(start)")
        }
    }
    */

    lazy var pdfiumPage: PDFiumPage? = {
        return PDFiumPage(document: document!.pdfiumDocument, pageIndex: index)
    }()

    init(document: VDPDFDocument, pageIndex: Int) {
        self.document = document
        self.index = pageIndex
    }

    func cleanUp() {
        text = nil
        pdfiumPage = nil
    }
}

extension String {

    func cleanedStringForPDFium() -> String {
        let s1 = replacingOccurrences(of: "\n", with: "")
        let s2 = s1.replacingOccurrences(of: " ", with: "")
        //let s3 = s2.replacingOccurrences(of: "\u{FFFE}", with: "- \n")
        return s2
    }

}
