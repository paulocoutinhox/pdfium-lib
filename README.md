# Mobile PDFium

[![Build Status](https://travis-ci.com/prsolucoes/mobile-pdfium.svg?branch=master)](https://travis-ci.com/prsolucoes/mobile-pdfium)

This project compile PDFium to mobile platforms. Current project compiles to:  

- [x] iOS device
- [x] iOS simulator
- [x] macOS
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

You can download a prebuilt copy here:  
https://www.dropbox.com/s/x1ls3vdoknwge02/libpdfium-2019-11-26.a?dl=1