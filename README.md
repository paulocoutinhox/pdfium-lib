# Mobile PDFium

[![Build Status](https://travis-ci.com/prsolucoes/mobile-pdfium.svg?branch=master)](https://travis-ci.com/prsolucoes/mobile-pdfium)

This project compile PDFium to mobile platforms. Current project compiles to:  

- [x] iOS device
- [x] iOS simulator
- [x] macOS
- [ ] Android

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
or  
```pip3 install -r requirements.txt --user``` 

3. Get Google Depot Tools:  
```python3 make.py run build-depot-tools```  
```export PATH=$PATH:$PWD/build/depot-tools```  

4. Get PDFium:  
```python3 make.py run build-pdfium```  

Obs:
- The file **make.py** need be executed with python3.  
- These steps you only need make one time.  
- If you change **pdfium** git commit revision on file **make.py** only execute step 4.

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

Obs:
- The file **make.py** need be executed with python3.  

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

## Prebuilt binary

For iOS (arm64 and x86_64):
https://www.dropbox.com/s/5zuddojoz7cqq80/libpdfium.a?dl=1

For macOS (x86_64):
https://www.dropbox.com/s/lt2py3p6ru1ixte/libpdfium.a?dl=1

## How to include files and extend pdfium

Check tutorial here: [How to include files](HOW_TO_INCLUDE_FILES.md)
