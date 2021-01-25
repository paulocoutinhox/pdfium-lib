# Build for WASM

1. Execute all **general** steps

2. Get Emscripten SDK:  
```python3 make.py run build-emsdk```  

3. Get PDFium:  
```python3 make.py run build-pdfium-wasm```  

4. Patch:  
```python3 make.py run patch-wasm```  

5. Compile:  
```python3 make.py run build-wasm```  
  
6. Install libraries:  
```python3 make.py run install-wasm```  

7. Test:  
```python3 make.py run test-wasm```  

Obs:
- The file **make.py** need be executed with python version 3.  
- You need run all steps in a Linux machine (real, vm or docker) to it works.


## Docker

You can use docker to build and test on local machine before deploy.

Build the image with command:

```docker build -t pdfium-wasm -f docker/wasm/Dockerfile docker/wasm```

Test with command:

```docker run -v ${PWD}:/app -it pdfium-wasm echo "test"```

Now you can execute any command with pattern:

```docker run -v ${PWD}:/app -it pdfium-wasm [COMMAND]```

Obs: This is the recommended way to build and is used on CD server.