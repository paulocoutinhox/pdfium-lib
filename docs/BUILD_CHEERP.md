# Build for Cheerp

1. Execute all **general** steps

2. Install Cheerp compiler:  

https://leaningtech.com/cheerp/

3. Get PDFium:  
```python3 make.py run build-pdfium-cheerp```  

4. Patch:  
```python3 make.py run patch-cheerp```  

5. PDFium Linux dependencies
```./build/linux/pdfium/build/install-build-deps.sh```

6. Compile:  
```python3 make.py run build-cheerp```  
  
7. Install libraries:  
```python3 make.py run install-cheerp```  

8. Test:  
```python3 make.py run test-cheerp```  
  
9. Generate javascript libraries:  
```python3 make.py run generate-cheerp```  

Obs:
- The file **make.py** need be executed with python version 3.  
- You need run all steps in a Linux machine (real, vm or docker) to it works.
- With docker you can skip steps 2 and 3.


## Docker

You can use docker to build and test on local machine before deploy.

Build the image with command:

```docker build -t pdfium-cheerp -f docker/cheerp/Dockerfile docker/cheerp```

Test with command:

```docker run -v ${PWD}:/app -it pdfium-cheerp echo "test"```

Now you can execute any command with pattern:

```docker run -v ${PWD}:/app -it pdfium-cheerp [COMMAND]```

Obs: This is the recommended way to build and is used on CD server.

## Run on browser

You can test the sample using commands:

```
python3 make.py run test-cheerp
python -m http.server --directory sample-cheerp/build
```

or with docker you can use:

```
docker run -v ${PWD}:/app -it pdfium-cheerp python3 make.py run test-cheerp
python3 -m http.server --directory sample-cheerp/build
```

## Run on terminal

You can test the sample using commands:

```
python3 make.py run test-cheerp
node sample-cheerp/build/index.js
```

or with docker you can use:

```
docker run -v ${PWD}:/app -it pdfium-cheerp python3 make.py run test-cheerp
docker run -v ${PWD}:/app -it pdfium-cheerp node sample-cheerp/build/index.js
```

## Web demo

You can test pdfium on web browser here:

https://pdfviewer.github.io/
