# Build for Android

1. Execute all **general** steps

2. Get PDFium:  
```python3 make.py run build-pdfium-android```  

3. Patch:  
```python3 make.py run patch-android```  

4. PDFium android dependencies
```./build/android/pdfium/build/install-build-deps-android.sh```

5. Compile:  
```python3 make.py run build-android```  
  
6. Install libraries:  
```python3 make.py run install-android```  

7. Test:  
```python3 make.py run test-android```  

Obs:
- The file **make.py** need be executed with python version 3.  
- You need run all steps in a Linux machine (real, vm or docker) to it works.


## Docker

You can use docker to build and test on local machine before deploy.

Build the image with command:

```docker build -t pdfium-android -f docker/android/Dockerfile docker/android```

Test with command:

```docker run -v ${PWD}:/app -it pdfium-android echo "test"```

Now you can execute any command with pattern:

```docker run -v ${PWD}:/app -it pdfium-android [COMMAND]```