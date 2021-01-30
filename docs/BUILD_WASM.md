# Build for WASM

1. Execute all **general** steps

2. PDFium linux dependencies
```./build/linux/pdfium/build/install-build-deps.sh```

3. Get Emscripten SDK:  
```python3 make.py run build-emsdk```  

4. Get PDFium:  
```python3 make.py run build-pdfium-wasm```  

5. Patch:  
```python3 make.py run patch-wasm```  

6. Compile:  
```python3 make.py run build-wasm```  
  
7. Install libraries:  
```python3 make.py run install-wasm```  

8. Test:  
```python3 make.py run test-wasm```  
  
9. Generate javascript libraries:  
```python3 make.py run generate-wasm```  

Obs:
- The file **make.py** need be executed with python version 3.  
- You need run all steps in a Linux machine (real, vm or docker) to it works.
- With docker you can skip steps 2 and 3.


## Docker

You can use docker to build and test on local machine before deploy.

Build the image with command:

```docker build -t pdfium-wasm -f docker/wasm/Dockerfile docker/wasm```

Test with command:

```docker run -v ${PWD}:/app -it pdfium-wasm echo "test"```

Now you can execute any command with pattern:

```docker run -v ${PWD}:/app -it pdfium-wasm [COMMAND]```

Obs: This is the recommended way to build and is used on CD server.

## Run on browser

You can test the sample using commands:

```
python3 make.py run test-wasm
python -m http.server --directory sample-wasm/build
```

or with docker you can use:

```
docker run -v ${PWD}:/app -it pdfium-wasm python3 make.py run test-wasm
python3 -m http.server --directory sample-wasm/build
```

## Run on terminal

You can test the sample using commands:

```
python3 make.py run test-wasm
node --experimental-wasm-threads --experimental-wasm-bulk-memory sample-wasm/build/index.js
```

or with docker you can use:

```
docker run -v ${PWD}:/app -it pdfium-wasm python3 make.py run test-wasm
docker run -v ${PWD}:/app -it pdfium-wasm node --experimental-wasm-threads --experimental-wasm-bulk-memory sample-wasm/build/index.js
```

## Web demo

You can test pdfium on web browser here:

https://paulo-coutinho.github.io/pdfium-lib/