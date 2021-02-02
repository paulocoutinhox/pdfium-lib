# PDF Viewer

You can test PDF Viewer on web browser here:

[https://pdfviewer.github.io/](https://pdfviewer.github.io/)

### Parameters

You can use some URL parameters to automatically open your PDF file and/or change viewer behaviour:

1. **title** = Any text that you want as title on page
2. **url** = Your PDF public URL to be downloaded by the viewer
3. **open** = Auto open after load (0 = disabled, 1 = enabled, default = 1)
4. **debug** = Debug console (0 = disabled, 1 = enabled, default = 1)

Example:

[https://pdfviewer.github.io/?title=Demo%20PDF%20with%201MB&url=https://file-examples-com.github.io/uploads/2017/10/file-example_PDF_1MB.pdf&debug=1&open=1](https://pdfviewer.github.io/?title=Demo%20PDF%20with%201MB&url=https://file-examples-com.github.io/uploads/2017/10/file-example_PDF_1MB.pdf&debug=1&open=1)

### Project

The main project is hosted here:

[https://github.com/paulo-coutinho/pdfium-lib](https://github.com/paulo-coutinho/pdfium-lib)

The PDF Viewer use PDFium project from Google to parse PDF data and render final image.
