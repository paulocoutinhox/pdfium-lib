# general
make_debug = False
make_task = ""
targets = ["ios", "macos"]

# pdfium
pdfium_git_commit = "e21911cc1c77d39dbc51001845bbfce2783e6514"

# macos
configurations_macos = ["release"]
targets_macos = [
    {"target_os": "macos", "target_cpu": "x64", "pdfium_os": "mac"},
]

# ios
configurations_ios = ["release"]
targets_ios = [
    {"target_os": "ios", "target_cpu": "arm64", "pdfium_os": "ios"},
    {"target_os": "ios", "target_cpu": "x64", "pdfium_os": "ios"},
]
