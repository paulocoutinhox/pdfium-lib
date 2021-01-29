# PDFium Library

![PDFium - iOS](https://github.com/prsolucoes/pdfium-lib/workflows/PDFium%20-%20iOS/badge.svg)
![PDFium - macOS](https://github.com/prsolucoes/pdfium-lib/workflows/PDFium%20-%20macOS/badge.svg)
![PDFium - Android](https://github.com/prsolucoes/pdfium-lib/workflows/PDFium%20-%20Android/badge.svg)
![PDFium - WASM](https://github.com/paulo-coutinho/pdfium-lib/workflows/PDFium%20-%20WASM/badge.svg)

This project compile PDFium to all supported platforms. Current project compiles to:  

- [x] iOS device (armv7, arm64)
- [x] iOS simulator (x86_64)
- [X] Android (armv7, armv8, x86, x86_64)
- [x] macOS (x86_64, arm64)
- [ ] Linux
- [ ] Windows
- [x] WASM (web assembly)

## Requirements

1. ninja (brew install ninja)  
2. python
3. pip

Obs: Only python version 3 is supported

## How to compile (general)

1. Get the source:  
```git clone https://github.com/prsolucoes/pdfium-lib.git```  
```cd pdfium-lib```  

2. Install pip requirements:  
```pip3 install -r requirements.txt``` 

3. Get Google Depot Tools:  
```python3 make.py run build-depot-tools```  
```export PATH=$PATH:$PWD/build/depot-tools```  

Obs:
- The file **make.py** need be executed with python version 3.  
- These steps you only need make one time.  
- If you change **pdfium** git commit revision on file **modules/config.py** only execute step 4.

## How to compile for iOS

Check tutorial here: [Build for iOS](docs/BUILD_IOS.md)

## How to compile for macOS (with Apple Silicon - M1)

Check tutorial here: [Build for macOS](docs/BUILD_MACOS.md)

## How to compile for Android

Check tutorial here: [Build for Android](docs/BUILD_ANDROID.md)

## How to compile for WASM

Check tutorial here: [Build for WASM](docs/BUILD_WASM.md)

## Prebuilt binary

Access releases page to download prebuilt binaries:

https://github.com/prsolucoes/pdfium-lib/releases

## How to include files and extend pdfium

Check tutorial here: [How to include files](docs/HOW_TO_INCLUDE_FILES.md)
