// Rendering happens here so that it never blocks the ui thread.
// The version comes from the worker url and is forwarded to every asset it loads, so a new release busts the cache of the worker and of the engine together.
const VERSION = new URLSearchParams(self.location.search).get('v') || "";
const VERSION_QUERY = VERSION ? "?v=" + encodeURIComponent(VERSION) : "";

importScripts('pdfium.js' + VERSION_QUERY);

const FPDF_FLAGS = {
    ANNOT: 0x01,
    REVERSE_BYTE_ORDER: 0x10,
};

const LAST_ERROR = {
    0: "success",
    1: "unknown error",
    2: "file not found or could not be opened",
    3: "file not in PDF format or corrupted",
    4: "password required or incorrect password",
    5: "unsupported security scheme",
    6: "page not found or content error",
};

const PASSWORD_ERROR = 4;

// The destination is BGRx and not BGRA, because an alpha destination makes blend modes composite against the white fill.
const BITMAP_BGRX = 3;
const BYTES_PER_PIXEL = 4;

let Module = null;
const FPDF = {};

// The bytes of the last open attempt, kept so a password retry does not resend them.
let sourceBytes = null;
let activeDocument = null;

// The jobs waiting to be rendered, and the generation that decides which ones are still wanted.
let queue = [];
let generation = 0;
let drainScheduled = false;

PDFiumModule().then((instance) => {
    Module = instance;
    bindFunctions();
    FPDF.Init();
    self.postMessage({ type: 'ready' });
});

function bindFunctions() {
    FPDF.Init = Module.cwrap('PDFium_Init');
    FPDF.LoadCustomDocument = Module.cwrap('FPDF_LoadCustomDocument', 'number', ['number', 'string']);
    FPDF.CloseDocument = Module.cwrap('FPDF_CloseDocument', '', ['number']);
    FPDF.GetPageCount = Module.cwrap('FPDF_GetPageCount', 'number', ['number']);
    FPDF.GetPageSizeByIndex = Module.cwrap('FPDF_GetPageSizeByIndex', 'number', ['number', 'number', 'number', 'number']);
    FPDF.GetLastError = Module.cwrap('FPDF_GetLastError', 'number');
    FPDF.LoadPage = Module.cwrap('FPDF_LoadPage', 'number', ['number', 'number']);
    FPDF.ClosePage = Module.cwrap('FPDF_ClosePage', '', ['number']);
    FPDF.RenderPageBitmap = Module.cwrap('FPDF_RenderPageBitmap', '', ['number', 'number', 'number', 'number', 'number', 'number', 'number', 'number']);
    FPDF.Bitmap_CreateEx = Module.cwrap('FPDFBitmap_CreateEx', 'number', ['number', 'number', 'number', 'number', 'number']);
    FPDF.Bitmap_FillRect = Module.cwrap('FPDFBitmap_FillRect', '', ['number', 'number', 'number', 'number', 'number', 'number']);
    FPDF.Bitmap_Destroy = Module.cwrap('FPDFBitmap_Destroy', '', ['number']);
}

self.onmessage = (event) => {
    const message = event.data;

    switch (message.type) {
        case 'open':
            open(message);
            break;

        case 'close':
            closeDocument();
            break;

        case 'render':
            enqueue(message);
            break;

        case 'drop':
            queue = queue.filter((job) => job.index !== message.index || job.quality !== 'full');
            break;

        case 'cancel':
            generation = message.gen;
            queue = queue.filter((job) => job.gen >= generation);
            break;
    }
};

// Opens a document, letting pdfium read only the blocks it needs from the source bytes.
function open(message) {
    closeDocument();

    if (message.buffer) {
        sourceBytes = new Uint8Array(message.buffer);
    }

    if (!sourceBytes) {
        self.postMessage({ type: 'openError', message: "no document to open" });
        return;
    }

    // The bytes have to outlive the call, because pdfium keeps reading them while the document is open.
    const bytes = sourceBytes;

    const readBlock = (param, position, bufferPtr, size) => {
        Module.HEAPU8.set(bytes.subarray(position, position + size), bufferPtr);
        return 1;
    };

    const readerPtr = Module.addFunction(readBlock, 'iiiii');

    // Builds the FPDF_FILEACCESS struct, holding m_FileLen, m_GetBlock and m_Param.
    const fileAccessPtr = Module.wasmExports.malloc(12);
    Module.setValue(fileAccessPtr + 0, bytes.length, 'i32');
    Module.setValue(fileAccessPtr + 4, readerPtr, 'i32');
    Module.setValue(fileAccessPtr + 8, 0, 'i32');

    const handle = FPDF.LoadCustomDocument(fileAccessPtr, message.password || "");

    // The struct is no longer needed once the document is created.
    Module.wasmExports.free(fileAccessPtr);

    if (!handle) {
        Module.removeFunction(readerPtr);

        const code = FPDF.GetLastError();

        self.postMessage({
            type: 'openError',
            message: LAST_ERROR[code] || "could not open document",
            needsPassword: code === PASSWORD_ERROR,
        });

        return;
    }

    const pageCount = FPDF.GetPageCount(handle);

    // Rejects a document that opened but carries no pages.
    if (pageCount <= 0) {
        FPDF.CloseDocument(handle);
        Module.removeFunction(readerPtr);
        self.postMessage({ type: 'openError', message: "this document has no pages" });
        return;
    }

    activeDocument = { handle, readerPtr, bytes, pageCount, sizes: readPageSizes(handle, pageCount) };

    self.postMessage({
        type: 'opened',
        pageCount,
        sizes: activeDocument.sizes,
    });
}

function closeDocument() {
    queue = [];

    if (!activeDocument) {
        return;
    }

    FPDF.CloseDocument(activeDocument.handle);
    Module.removeFunction(activeDocument.readerPtr);
    activeDocument = null;
}

// Returns the size of every page, without loading the pages themselves.
function readPageSizes(handle, pageCount) {
    const widthPtr = Module.wasmExports.malloc(8);
    const heightPtr = Module.wasmExports.malloc(8);
    const sizes = [];

    for (let index = 0; index < pageCount; index++) {
        FPDF.GetPageSizeByIndex(handle, index, widthPtr, heightPtr);

        // The doubles are read straight from the heap, which malloc keeps 8 byte aligned.
        sizes.push({
            width: Module.HEAPF64[widthPtr >> 3],
            height: Module.HEAPF64[heightPtr >> 3],
        });
    }

    Module.wasmExports.free(widthPtr);
    Module.wasmExports.free(heightPtr);

    return sizes;
}

// Queues a render, replacing any request still waiting for the same page and quality.
function enqueue(job) {
    if (job.gen > generation) {
        generation = job.gen;
    }

    queue = queue.filter((other) => other.index !== job.index || other.quality !== job.quality);
    queue.push(job);
    scheduleDrain();
}

function scheduleDrain() {
    if (drainScheduled) {
        return;
    }

    drainScheduled = true;

    // A macrotask is used instead of a microtask so that pending messages land between two renders.
    // That is what makes cancelling a fast scroll or a zoom take effect.
    setTimeout(drain, 0);
}

// Returns the most useful job, taking previews before full renders and then the closest to the viewport.
function takeNext() {
    let best = -1;

    for (let index = 0; index < queue.length; index++) {
        const job = queue[index];

        if (job.gen < generation) {
            continue;
        }

        if (best < 0) {
            best = index;
            continue;
        }

        const current = queue[best];
        const jobRank = job.quality === 'preview' ? 0 : 1;
        const bestRank = current.quality === 'preview' ? 0 : 1;

        if (jobRank < bestRank || (jobRank === bestRank && job.priority < current.priority)) {
            best = index;
        }
    }

    if (best < 0) {
        queue = [];
        return null;
    }

    const job = queue[best];
    queue = queue.filter((other) => other !== job && other.gen >= generation);

    return job;
}

async function drain() {
    drainScheduled = false;

    const job = takeNext();

    if (!job || !activeDocument) {
        return;
    }

    try {
        const image = renderPage(job);
        const payload = { type: 'rendered', index: job.index, quality: job.quality, gen: job.gen, scale: job.scale, width: image.width, height: image.height };

        // An ImageBitmap transfers without a copy and paints without touching the cpu.
        if (typeof createImageBitmap === 'function') {
            const bitmap = await createImageBitmap(image);
            self.postMessage({ ...payload, bitmap }, [bitmap]);
        } else {
            self.postMessage({ ...payload, pixels: image.data.buffer }, [image.data.buffer]);
        }
    } catch (error) {
        self.postMessage({ type: 'renderError', index: job.index, message: String(error && error.message || error) });
    }

    if (queue.length > 0) {
        scheduleDrain();
    }
}

function renderPage(job) {
    const size = activeDocument.sizes[job.index];
    const width = Math.max(1, Math.ceil(size.width * job.scale));
    const height = Math.max(1, Math.ceil(size.height * job.scale));
    const byteCount = width * height * BYTES_PER_PIXEL;

    const page = FPDF.LoadPage(activeDocument.handle, job.index);

    if (!page) {
        throw new Error("could not load page " + (job.index + 1));
    }

    const bufferPtr = Module.wasmExports.malloc(byteCount);
    const bitmap = FPDF.Bitmap_CreateEx(width, height, BITMAP_BGRX, bufferPtr, width * BYTES_PER_PIXEL);

    FPDF.Bitmap_FillRect(bitmap, 0, 0, width, height, 0xFFFFFFFF);
    FPDF.RenderPageBitmap(bitmap, page, 0, 0, width, height, 0, FPDF_FLAGS.REVERSE_BYTE_ORDER | FPDF_FLAGS.ANNOT);

    // The pixels are copied out of the heap before the native buffer is released.
    const pixels = new Uint8ClampedArray(Module.HEAPU8.buffer, bufferPtr, byteCount).slice();

    FPDF.Bitmap_Destroy(bitmap);
    Module.wasmExports.free(bufferPtr);
    FPDF.ClosePage(page);

    return new ImageData(pixels, width, height);
}
