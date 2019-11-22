# Mobile PDFium

[![Build Status](https://travis-ci.com/prsolucoes/mobile-pdfium.svg?branch=master)](https://travis-ci.com/prsolucoes/mobile-pdfium)

This project compile PDFium to mobile platforms. Current project compiles to:  

- [x] iOS  
- [ ] Android  

## Requirements

1. ninja (brew install ninja)  
2. python3  
3. pip (generally called pip3 for python3)  

## How to compile (general)

1. Get the source:  
```git clone https://github.com/prsolucoes/mobile-pdfium.git```  

2. Install pip requirements:  
```pip3 install -r requirements.txt``` 
or  
```pip3 install -r requirements.txt --user``` 

3. Get Google Depot Tools:  
```python3 make.py run build-depot-tools```  
```export PATH=$PATH:$PWD/depot-tools```  

4. Get PDFium:  
```python3 make.py run build-pdfium```  

## How to compile for iOS

1. Execute all **general** steps

2. Apply patchs:  
```python3 make.py run apply-patch-ios```  

3. Compile:  
```python3 make.py run build-ios```  
  
4. Install libraries:  
```python3 make.py run install-ios```  

5. Check generated file:  
```file build/ios/release/libpdfium.a```  

## How to compile for macOS

1. Execute all **general** steps

2. Apply patchs:  
```python3 make.py run apply-patch-macos```  

3. Compile:  
```python3 make.py run build-macos```  
  
4. Install libraries:  
```python3 make.py run install-macos```  

5. Check generated file:  
```file build/macos/release/libpdfium.a```  

6. Run sample (optional):  
```python3 make.py run sample```  

Obs:
- The file **make.py** need be executed with python3.  
- The steps 1, 2, 3, 4 and 5 you only need make one time.  
- If you change pdfium source code, execute steps 6 and 7 only.

## Prebuilt binary

You can download a prebuilt copy here:  
https://www.dropbox.com/s/iuekzx24q99mr7t/libpdfium-2019-11-19.a?dl=1