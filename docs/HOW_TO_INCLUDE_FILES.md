# How to include files

Sometimes you want include files (.h, .cpp, ...) in pdfium source set to be compiled with libpdfium  and extend their features and more.

To do this you need follow this steps:

1. Inside **"pdfium/BUILD.gn"** you have all files that are included to be compile. Go to dependencies tag inside **"BUILD.gn"** and add your folder that will have your sources. I will use "my_sources" as my example:

```
component("pdfium") {
  ...

  deps = [
    "constants",
    "core/fpdfapi/page",
    "core/fpdfapi/parser",
    "core/fpdfdoc",
    "core/fxcodec",
    "core/fxcrt",
    "core/fxge",
    "fpdfsdk",
    "fpdfsdk/formfiller",
    "fxjs",
    "third_party:pdfium_base",
    "third_party:skia_shared",
    "my_sources",
  ]

  ....
}
```

2. Create a folder **"my_sources"**.
3. Inside **"my_sources"** add a file called **"BUILD.gn"**. 
4. Inside **"BUILD.gn"** add this structure with your file list:

```
source_set("my_sources") {
  sources = [
    "my_source_file.cpp",
    "my_header_file.h",
  ]
```

All files that i put on my example (my_source_file.cpp and my_header_file.h) is stored relative to **BUILD.gn** file. If you put in some folder you need put the folder name. Example:

```
source_set("my_sources") {
  sources = [
    "src/my_source_file.cpp",
    "include/my_header_file.h",
  ]
```

5. Now compile!

If can check other examples to see how Google organize their sources. Check others **BUILD.gn** file like these:

1. pdfium/core/fpdfapi/parser/BUILD.gn
2. pdfium/core/fpdfapi/render/BUILD.gn

Thanks.