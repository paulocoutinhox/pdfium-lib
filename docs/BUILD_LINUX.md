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

`x64` and `arm64` are built, both from an x64 machine. Adding another one is an entry in `targets_linux` in `modules/config.py`.

Cross compiling uses the sysroot chromium publishes for each architecture, which `build-pdfium-linux` downloads after cloning. Building against it also keeps the glibc requirement at the one Debian Bullseye ships, instead of the one on the machine that compiled it.

# Packaging

The release asset `linux.tgz` expands to a single `release` directory holding `include` and `lib/<arch>`. Distribution packages can install it directly, without building anything.

The library links the system C++ runtime, so it needs `libstdc++.so.6` and a glibc at least as new as the one it was built against. The published binary requires **glibc 2.35**, which covers Ubuntu 22.04 and later, Debian 12 and later, and any rolling distribution. Its soname is `libpdfium.so`, without a version suffix.

## Arch Linux

Save this as `PKGBUILD`, run `updpkgsums` to fill in the checksums, then `makepkg -si`.

```bash
# Maintainer: Your Name <your@email>

pkgname=pdfium-bin
pkgver=8046b
pkgrel=1
pkgdesc="PDFium, Google's PDF rendering library, prebuilt by pdfium-lib"
arch=('x86_64')
url="https://github.com/paulocoutinhox/pdfium-lib"
license=('BSD-3-Clause')
depends=('gcc-libs' 'glibc')
provides=('pdfium' 'libpdfium.so')
conflicts=('pdfium')

source=(
    "$pkgname-$pkgver.tar.gz::$url/releases/download/$pkgver/linux.tgz"
    "LICENSE-$pkgver.md::https://raw.githubusercontent.com/paulocoutinhox/pdfium-lib/$pkgver/LICENSE.md"
)

# Run updpkgsums to fill these in.
sha256sums=('SKIP'
            'SKIP')

package() {
    # The archive expands to a single release directory.
    cd "$srcdir/release"

    install -Dm755 "lib/x64/libpdfium.so" "$pkgdir/usr/lib/libpdfium.so"

    install -d "$pkgdir/usr/include/pdfium"
    cp -a include/. "$pkgdir/usr/include/pdfium/"
    find "$pkgdir/usr/include/pdfium" -type f -exec chmod 644 {} +

    install -Dm644 "$srcdir/LICENSE-$pkgver.md" \
        "$pkgdir/usr/share/licenses/$pkgname/LICENSE.md"

    install -Dm644 /dev/stdin "$pkgdir/usr/lib/pkgconfig/pdfium.pc" <<EOF
prefix=/usr
libdir=\${prefix}/lib
includedir=\${prefix}/include/pdfium

Name: PDFium
Description: PDF rendering library
URL: $url
Version: $pkgver
Libs: -L\${libdir} -lpdfium
Cflags: -I\${includedir}
EOF
}
```

## Debian and Ubuntu

Nothing about the library changes, only where it is installed: these distributions place libraries in a multiarch directory instead of `/usr/lib`.

```bash
VERSION=8046b

curl -LO "https://github.com/paulocoutinhox/pdfium-lib/releases/download/$VERSION/linux.tgz"
tar -xzf linux.tgz

mkdir -p pdfium/DEBIAN pdfium/usr/lib/x86_64-linux-gnu pdfium/usr/include/pdfium

cat > pdfium/DEBIAN/control <<EOF
Package: pdfium
Version: $VERSION
Section: libs
Priority: optional
Architecture: amd64
Depends: libc6 (>= 2.35), libstdc++6
Maintainer: Your Name <your@email>
Description: PDFium, Google's PDF rendering library
EOF

cp release/lib/x64/libpdfium.so pdfium/usr/lib/x86_64-linux-gnu/
cp -a release/include/. pdfium/usr/include/pdfium/

dpkg-deb --build pdfium
sudo dpkg -i pdfium.deb
```

## Using the package

Both layouts put the headers under `pdfium`, so a consumer includes them through that directory.

```c
#include <pdfium/fpdfview.h>
```

```bash
gcc main.c -lpdfium -o main
```
