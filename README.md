# Mobile PDFium

[![Build Status](https://travis-ci.com/prsolucoes/mobile-pdfium.svg?branch=master)](https://travis-ci.com/prsolucoes/mobile-pdfium)

This project compile PDFium to all supported platforms. Current project compiles to:  

- [x] iOS device
- [x] iOS simulator
- [ ] Android
- [x] macOS
- [ ] Linux
- [ ] Windows

## Requirements

1. ninja (brew install ninja)  
2. python
3. pip

Obs: Only python version 3 is supported

## How to compile (general)

1. Get the source:  
```git clone https://github.com/prsolucoes/mobile-pdfium.git```  

2. Install pip requirements:  
```pip3 install -r requirements.txt``` 

3. Get Google Depot Tools:  
```python3 make.py run build-depot-tools```  
```export PATH=$PATH:$PWD/build/depot-tools```  

4. Get PDFium:  
```python3 make.py run build-pdfium```  

Obs:
- The file **make.py** need be executed with python version 3.  
- These steps you only need make one time.  
- If you change **pdfium** git commit revision on file **modules/config.py** only execute step 4.

## How to compile for iOS

Check tutorial here: [Build for iOS](docs/BUILD_IOS.md)

## How to compile for macOS

Check tutorial here: [Build for macOS](docs/BUILD_MACOS.md)

## Prebuilt binary

For iOS (arm64 and x86_64):

https://www.dropbox.com/s/5zuddojoz7cqq80/libpdfium.a?dl=1

For macOS (x86_64):

https://www.dropbox.com/s/lt2py3p6ru1ixte/libpdfium.a?dl=1

## How to include files and extend pdfium

Check tutorial here: [How to include files](docs/HOW_TO_INCLUDE_FILES.md)
