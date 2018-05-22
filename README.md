# Mobile PDFium

This project compile PDFium to mobile platforms. Current project compiles to:  

- [x] iOS  
- [ ] Android  

## Requirements

1. ninja (brew install ninja)  

## How to compile

1. Get the source:  
git clone github.com/prsolucoes/mobile-pdfium.git

2. Get Google Depot Tools:  
make build-depot-tools

3. Get PDFium:  
make build-pdfium

4. Compile for iOS:  
make build-ios

## Options inside GN file

Copy and paste it into the editor that will open when you run **build-ios**:  

```
use_goma = false  # Googlers only. Make sure goma is installed and running first.
is_debug = true  # Enable debugging features.

pdf_use_skia = false  # Set true to enable experimental skia backend.
pdf_use_skia_paths = false  # Set true to enable experimental skia backend (paths only).

pdf_enable_xfa = false  # Set false to remove XFA support (implies JS support).
pdf_enable_v8 = false  # Set false to remove Javascript support.
pdf_is_standalone = true  # Set for a non-embedded build.
is_component_build = false # Disable component build (must be false)

clang_use_chrome_plugins = false  # Currently must be false.
```