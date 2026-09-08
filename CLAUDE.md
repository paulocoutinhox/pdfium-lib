# Project conventions

This file records how the project is organised and how work on it is expected to be done.
Read it before changing anything.

## What this project is

It compiles Google's PDFium into a distributable library for several platforms. It does not
fork PDFium and it does not vendor its source. Every build clones PDFium from upstream,
applies the minimum set of patches needed for the target platform, compiles it and stages
the result. All the value of the project sits in the tooling that makes those steps
reproducible, so keep the tooling clean and never let a fix drift into a copy of upstream code.

## Layout

```
make.py                    Task entry point, one task per platform step.
modules/
  config.py                Every configurable value: pdfium branch, targets, configurations.
  common.py                Shared tasks and the gn argument builder.
  pdfium.py                Cloning and syncing pdfium through gclient.
  patch.py                 Reusable patches applied to the checkout.
  <platform>.py            The six tasks of one platform.
docs/BUILD_<PLATFORM>.md   Build tutorial for one platform.
.github/workflows/         One workflow per platform, all with the same shape.
sample/                    Console sample used by the test task on desktop platforms.
sample-apple/              Xcode sample for macOS and iOS.
sample-wasm/               Sample for the WASM build.
extras/wasm/               Files shipped with the WASM package, including the viewer template.
build/                     Output only, ignored by git, safe to delete at any time.
```

`build/` holds three different things and the names repeat, so read paths carefully:

```
build/<platform>/pdfium/          The pdfium checkout.
build/<platform>/pdfium/build/    chromium/src/build.git, pulled by pdfium's DEPS.
build/<platform>/<config>/        The staged library and headers, what gets archived.
```

## Platform modules

Every platform module exposes the same six tasks, in this order, and nothing else:

| Task | What it does |
| --- | --- |
| `run_task_build_pdfium` | Clones and syncs pdfium through `modules/pdfium.py`. |
| `run_task_patch` | Applies the patches the platform needs. Must be idempotent. |
| `run_task_build` | Runs `gn gen` and `ninja` for every configuration and target. |
| `run_task_install` | Stages the library and the headers under `build/<platform>/<config>`. |
| `run_task_test` | Builds the sample against the staged library and runs it. |
| `run_task_archive` | Packs the staged directory into `<platform>.tgz`. |

Use `modules/macos.py` as the reference when adding a platform. Register the tasks in
`make.py`, in the docstring and in the dispatch chain, keeping the platform sections in the
same order in both.

## Configuration

`modules/config.py` is the single source of truth. A value that lives there is never
repeated anywhere else, and code reads it instead of assuming what it holds. Each platform
declares three things:

```python
configurations_<platform> = ["release"]
shared_lib_<platform> = False
targets_<platform> = [
    {"target_os": "linux", "target_cpu": "x64", "pdfium_os": "linux"},
]
```

`target_os` names the output directory, `pdfium_os` is the value gn expects, and they differ
on purpose: `macos` is `mac` to gn, `windows` is `win`. Adding an architecture is one entry
in the list and nothing else.

Build arguments belong in `get_build_args` in `modules/common.py`, never inline in a platform
module. Static builds get `pdf_is_complete_lib=true`, and every platform that ships a static
library also needs `use_custom_libcxx=false`, because the bundled libc++ never reaches a
static archive and its symbols carry an ABI namespace no system runtime provides.

## Patches

PDFium and the chromium build system it pulls in assume the toolchain Google packages
internally. Where that assumption does not hold, the patch task rewrites the checkout before
building. Rules for patches:

- Live in `modules/patch.py`, and are called from a platform's `run_task_patch`.
- Detect what the machine actually has and adapt to it. Never hardcode a version, a path or a tool location.
- Are idempotent, because CI runs the patch task twice to prove it. Report `Applied` the first time and `Skipped` afterwards.
- Are a no-op where they do not apply, so a platform module can call them unconditionally.
- Touch only files under `build/`, which is disposable. Never patch anything tracked by this repository.

The windows patches are the reference: chromium pins the SDK version in `vs_toolchain.py` and
`setup_toolchain.py`, and pins the API level in `config/win/BUILD.gn`. Both are rewritten from
what is installed on the machine.

## Continuous integration

One workflow per platform, all built from the same shape: set up Python, CMake and Ninja,
install the requirements, clone depot tools, put it on `PATH`, then run the six tasks in
order, upload the archive, and deploy it on a tag. Keep new workflows aligned with the
existing ones, and add the badge to `README.md`.

Windows differs in two ways that must not be undone:

- `DEPOT_TOOLS_UPDATE` is never set to `0`, because that skips the bootstrap that installs `git.bat` and the bundled python.
- Python is invoked by path, because the bootstrap drops a `python3.bat` that ends up ahead of the one on `PATH`.

## Code standard

Python is formatted with `black`, through `python3 make.py format`. Run it before committing.

Modules follow the shape of the existing ones: standard library imports, then `pygemstones`,
then project modules, each function separated by the `# ---` line already used across the
project. Build paths with `os.path.join`, never by concatenating strings.

Comments follow one standard, in every language used here:

- Every comment is a complete sentence, starting with a capital letter and ending with a period.
- One sentence per line. Never wrap a sentence across lines and never continue one on the next line.
- If more than one sentence is needed, finish the current one before starting the next on the following line.
- A comment above a function, method, class or module says what it does for the caller, never how it works inside.
- Keep comments objective and natural, never verbose, fragmented or narrative.
- When a sentence would start with a lowercase identifier, keep its exact spelling and rewrite the sentence so it is not at the start.
- Code and comments are written in English.

## What not to do

- Do not probe for one of several possible states when the layout can be pinned instead. Make the outcome deterministic and read it directly.
- Do not add fallbacks for cases that cannot happen, and do not write code paths that nothing exercises.
- Do not keep dead or legacy code around. Delete it.
- Do not hardcode a value that already exists in `modules/config.py`.
- Do not vendor or commit anything produced under `build/`.
- Do not fix a platform by special casing it inside shared code when the difference belongs in the platform module.

## Working agreement

Every change goes on its own branch, named in short kebab-case, matching the existing ones
such as `fix-blend-mode-render`, `better-wasm-viewer` and `support-linux-windows`. Review the
diff before committing. Push only when asked. Report what was verified and what was not,
plainly, without overstating.
