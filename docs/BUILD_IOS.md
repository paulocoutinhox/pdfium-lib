# Build for iOS

1. Execute all **general** steps

2. Get PDFium:
```python3 make.py build-pdfium-ios```

3. Patch:
```python3 make.py patch-ios```

4. Compile:
```python3 make.py build-ios```

5. Install libraries:
```python3 make.py install-ios```

6. Test:
```python3 make.py test-ios```

Obs:
- The file **make.py** need be executed with python version 3.

# Sample

The sample project is here: `sample-apple/Sample.xcodeproj`.

Copy the `pdfium.xcframework` to folder `sample-apple/Sample/Vendor`.
