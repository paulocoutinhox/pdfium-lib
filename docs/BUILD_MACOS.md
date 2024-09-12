# Build for macOS

1. First, execute all steps in the [How to compile](https://github.com/paulocoutinhox/pdfium-lib/tree/master?tab=readme-ov-file#how-to-compile) section

2. Get PDFium:
```python3 make.py build-pdfium-macos```

3. Patch:
```python3 make.py patch-macos```

4. Compile:
```python3 make.py build-macos```

5. Install libraries:
```python3 make.py install-macos```

6. Test:
```python3 make.py test-macos```

Obs:
- The file **make.py** need be executed with python version 3.

# Sample

The sample project is here: `sample-apple/Sample.xcodeproj`.

Copy the `include` and `lib` dirs to folder `sample-apple/SampleMac/Vendor`.
