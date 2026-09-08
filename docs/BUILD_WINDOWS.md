# Build for Windows

1. First, execute all steps in the [How to compile](https://github.com/paulocoutinhox/pdfium-lib/tree/master?tab=readme-ov-file#how-to-compile) section

2. Tell depot tools to use your own Visual Studio instead of the internal Google toolchain:
```
set DEPOT_TOOLS_WIN_TOOLCHAIN=0
```

3. Get PDFium:
```python3 make.py build-pdfium-windows```

4. Patch:
```python3 make.py patch-windows```

5. Compile:
```python3 make.py build-windows```

6. Install libraries:
```python3 make.py install-windows```

7. Test:
```python3 make.py test-windows```

Obs:
- The file **make.py** need be executed with python version 3.
- You need Visual Studio 2022 with the **Desktop development with C++** workload and the Windows SDK.
- The `DEPOT_TOOLS_WIN_TOOLCHAIN` variable must be set in every terminal used to build.

# Sample

The sample project is here: `sample`.

The libraries are installed in `build/windows/release`, with one directory per architecture inside `lib`.

# Architectures

Only `x64` is built by default. To add another one, append it to `targets_windows` in `modules/config.py`:

```
targets_windows = [
    {"target_os": "windows", "target_cpu": "x64", "pdfium_os": "win"},
    {"target_os": "windows", "target_cpu": "arm64", "pdfium_os": "win"},
]
```

Obs: `arm64` needs the ARM64 build tools installed in Visual Studio.
