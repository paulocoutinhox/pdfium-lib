import Foundation
import PDFKit

class VDPDFDocument {

    var pkPDFDocument: PDFDocument

    var pdfiumDocument: PDFiumDocument

    var pages: [VDPDFPage] = []

    var text: String {
        var text: String = ""
        for page in pages {
            if let pageText = page.text {
                text += pageText
                text += "\n"
            }
        }
        return text;
    }

    var pageCount: Int {
        return pkPDFDocument.pageCount
    }

    init?(url: URL, password: String!) {
        guard let pdfiumDocument = PDFiumDocument(url: url, password: password) else {
            return nil
        }

        guard let pkPDFDocument = PDFDocument(url: url) else {
            return nil
        }

        self.pdfiumDocument = pdfiumDocument
        self.pkPDFDocument = pkPDFDocument

        for pageIndex in 0..<pageCount {
            let page = VDPDFPage(document: self, pageIndex: pageIndex)
            pages.append(page)
        }
    }
}
