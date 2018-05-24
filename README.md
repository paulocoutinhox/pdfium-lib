# Mobile PDFium

This project compile PDFium to mobile platforms. Current project compiles to:  

- [x] iOS  
- [ ] Android  

## Requirements

1. ninja (brew install ninja)  
2. python3  
3. pip3  

## How to compile 

1. Get the source:  
```git clone github.com/prsolucoes/mobile-pdfium.git```  

2. Install pip requirements:  
```pip3 install -r requirements.txt``` 
or  
```pip3 install -r requirements.txt --user``` 

3. Get Google Depot Tools:  
```python3 make.py build-depot-tools```  

4. Get Chromium:  
```python3 make.py build-chromium```  

5. Get PDFium:  
```python3 make.py build-pdfium```  

6. Apply patchs:  
```Check **patchs** section of this file```  

7. Compile for iOS:  
```python3 make.py build-ios```  
  
8. Install iOS libraries:  
```python3 make.py install-ios```  


Obs:
- The file **make.py** need be executed with python3.  
- The steps 1, 2, 3, 4, 5 and 6 you only need make one time.  


## Patchs

1. Remove assert lines from libjpeg_turbo build files:  
- pdfium/build/secondary/third_party/libjpeg_turbo/BUILD.gn  
- chromium/build/secondary/third_party/libjpeg_turbo/BUILD.gn  
- chromium/third_party/BUILD.gn  

2. Replace line 62 from **pdfium/core/fxcrt/fx_system.h**:  
- FROM #include <Carbon/Carbon.h>  
- TO #include <CoreGraphics/CoreGraphics.h>  

3. Add to file **pdfium/BUILD.gn** on line 243, the code:  
```
if (is_ios) {
  libs += [
    "CoreGraphics.framework"
  ]
}
```

3. Add to file **pdfium/BUILD.gn** on line 1132, the code:  
```
if (is_ios) {
  sources += [ "core/fxge/apple/fx_apple_platform.cpp" ]
}
```

4. Add to file **pdfium/BUILD.gn** on line 1158, the code:  
```
if (is_ios) {
  sources += [
    "core/fxge/apple/apple_int.h",
    "core/fxge/apple/fx_mac_imp.cpp",
    "core/fxge/apple/fx_quartz_device.cpp",
  ]
}
```

5. Replace line 18 from **pdfium/core/fxge/apple/apple_int.h**:  
- FROM #include <Carbon/Carbon.h>  
- TO #include <CoreGraphics/CoreGraphics.h>  

6. Disable neon file for ARM (armv7) of libjpeg_turbo if you have problems like me. Delete line 119 of file **pdfium/build/secondary/third_party/libjpeg_turbo/BUILD.gn**:
```
"simd/jsimd_arm_neon.S",
```

Obs: If anyone know how to make the patch from command line, please, help with this.