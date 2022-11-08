import Cocoa

class ViewController: NSViewController {

    var testFiles: [URL] = {
        return [Bundle.main.url(forResource: "sample-file", withExtension: "pdf")!]
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        runTest()
    }

    override var representedObject: Any? {
        didSet {
            // Update the view, if already loaded.
        }
    }

    func runTest() {
        let start = DispatchTime.now()
        let urls = testFiles
        for url in urls {
            autoreleasepool {
                runPDFium(url)
            }
        }
        let end = DispatchTime.now()
        let nanoTime = end.uptimeNanoseconds - start.uptimeNanoseconds
        let timeInterval = Double(nanoTime) / 1_000_000_000
        print("Total time: \(timeInterval)")
    }

    func runPDFium(_ url: URL) {
        if let pdfiumDoc = VDPDFDocument(url: url, password: nil) {
            var text: String = ""
            for page in pdfiumDoc.pages {
                if let pageText = page.text {
                    text += "PAGE \(page.index)\n"
                    text += "TEXT   START ----------------\n"
                    text += pageText
                    text += "\n"
                    text += "TEXT   END   ----------------\n"
                    text += "LAYOUT START ----------------\n"
                    text += "LAYOUT END ----------------\n"
                    page.cleanUp()
                }
            }
            print(text)
        }
    }
    
}

