# Mobile PDFium

This project compile PDFium to mobile platforms. Current project compiles to:  

- [x] iOS  
- [ ] Android  

## Requirements

1. ninja (brew install ninja)  
2. python3  
3. pip (generally called pip3 for python3)  

## How to compile 

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

5. Apply patchs:

    For iOS:  
    ```python3 make.py run apply-patch-ios```  

6. Compile for iOS:  
```python3 make.py run build-ios```  
  
7. Install iOS libraries:  
```python3 make.py run install-ios```  


Obs:
- The file **make.py** need be executed with python3.  
- The steps 1, 2, 3, 4 and 5 you only need make one time.  
- If you change pdfium source code, execute steps 6 and 7 only.
