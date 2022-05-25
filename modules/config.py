# general
debug = False
task = ""

# pdfium
pdfium_git_branch = "5082"
pdfium_git_commit = "3da2ecad3a1402295b3cc020765f6790652f32f1"
# ^ ref: https://pdfium.googlesource.com/pdfium/+/refs/heads/chromium/5082
# OBS 1: don't forget change in android docker file (docker/android/Dockerfile)
# OBS 2: don't forget change in wasm docker file (docker/wasm/Dockerfile)

# emsdk
emsdk_version = "2.0.24"
# OBS 1: don't forget change in wasm docker file (docker/wasm/Dockerfile)

# macos
configurations_macos = ["release"]
targets_macos = [
    {"target_os": "macos", "target_cpu": "x64", "pdfium_os": "mac"},
    {"target_os": "macos", "target_cpu": "arm64", "pdfium_os": "mac"},
]

# ios
configurations_ios = ["release"]
targets_ios = [
    {"target_os": "ios", "target_cpu": "arm", "pdfium_os": "ios"},
    {"target_os": "ios", "target_cpu": "arm64", "pdfium_os": "ios"},
    {"target_os": "ios", "target_cpu": "x64", "pdfium_os": "ios"},
]

# android
configurations_android = ["release"]
targets_android = [
    {
        "target_os": "android",
        "target_cpu": "arm",
        "pdfium_os": "android",
        "android_cpu": "armeabi-v7a",
    },
    {
        "target_os": "android",
        "target_cpu": "x86",
        "pdfium_os": "android",
        "android_cpu": "x86",
    },
    {
        "target_os": "android",
        "target_cpu": "arm64",
        "pdfium_os": "android",
        "android_cpu": "arm64-v8a",
    },
    {
        "target_os": "android",
        "target_cpu": "x64",
        "pdfium_os": "android",
        "android_cpu": "x86_64",
    },
]

# wasm
configurations_wasm = ["release"]
targets_wasm = [
    {"target_os": "wasm", "target_cpu": "x64", "pdfium_os": "linux"},
]
