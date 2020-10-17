# Build for Android

1. Execute all **general** steps

2. Patch:  
```python3 make.py run patch-android```  

3. PDFium android dependencies
```./build/android/pdfium/build/install-build-deps-android.sh```

4. Compile:  
```python3 make.py run build-android```  
  
5. Install libraries:  
```python3 make.py run install-android```  

6. Test:  
```python3 make.py run test-android```  

Obs:
- The file **make.py** need be executed with python version 3.  
- You need run all steps in a Linux machine (real, vm or docker) to it works.
