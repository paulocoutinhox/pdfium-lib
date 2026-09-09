# Build for Linux

1. First, execute all steps in the [How to compile](https://github.com/paulocoutinhox/pdfium-lib/tree/master?tab=readme-ov-file#how-to-compile) section

2. Get PDFium:
```python3 make.py build-pdfium-linux```

3. Patch:
```python3 make.py patch-linux```

4. Compile:
```python3 make.py build-linux```

5. Install libraries:
```python3 make.py install-linux```

6. Test:
```python3 make.py test-linux```

Obs:
- The file **make.py** need be executed with python version 3.
- You need a C++ toolchain installed, on Debian and Ubuntu: `sudo apt-get install build-essential pkg-config`.
- The library is built against the system C++ runtime, so build it on the oldest distribution you need to support.

# Sample

The sample project is here: `sample`.

The libraries are installed in `build/linux/release`, with one directory per architecture inside `lib`.

The build produces a shared `libpdfium.so` linked against the system C++ runtime, which is what a distribution package expects.

# Architectures

Only `x64` is built by default. To add another one, append it to `targets_linux` in `modules/config.py`:

```
targets_linux = [
    {"target_os": "linux", "target_cpu": "x64", "pdfium_os": "linux"},
    {"target_os": "linux", "target_cpu": "arm64", "pdfium_os": "linux"},
]
```

Obs: cross compiling needs a toolchain for the target architecture.
