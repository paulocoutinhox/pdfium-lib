# Build for WASM

1. Execute all **general** steps

2. Get Emscripten SDK:
```python3 make.py build-emsdk```

3. Execute EMSDK environment file "emsdk_env" according to your system.

4. Get PDFium:
```python3 make.py build-pdfium-wasm```

5. Patch:
```python3 make.py patch-wasm```

6. PDFium Linux dependencies
```./build/wasm32/pdfium/build/install-build-deps.sh```

7. Compile:
```python3 make.py build-wasm```

8. Install libraries:
```python3 make.py install-wasm```

9. Test:
```python3 make.py test-wasm```

10. Generate javascript libraries:
```python3 make.py generate-wasm```

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

## Docker (macOS arm64)

If you are in a macOS with arm64 processors (M*), build with command:

```docker build --platform linux/amd64 -t pdfium-wasm -f docker/wasm/Dockerfile docker/wasm```

## Run on browser

You can test the sample using commands:

```
python3 make.py test-wasm
python3 -m http.server --directory sample-wasm/build
```

or with docker you can use:

```
docker run -v ${PWD}:/app -it pdfium-wasm python3 make.py test-wasm
python3 -m http.server --directory sample-wasm/build
```

## Run on terminal

You can test the sample using commands:

```
python3 make.py test-wasm
node sample-wasm/build/index.js
```

or with docker you can use:

```
docker run -v ${PWD}:/app -it pdfium-wasm python3 make.py test-wasm
docker run -v ${PWD}:/app -it pdfium-wasm node sample-wasm/build/index.js
```

## Web demo

You can test pdfium on web browser here:

https://pdfviewer.github.io/
