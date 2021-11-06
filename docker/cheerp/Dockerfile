FROM ubuntu:18.04

# general
ARG DEBIAN_FRONTEND=noninteractive

ENV PROJ_TARGET="wasm"
ENV JAVA_VERSION="8"
ENV JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"

# packages
RUN apt-get -y update
RUN apt-get install -y build-essential sudo file git wget curl ninja-build zip unzip tar software-properties-common openjdk-${JAVA_VERSION}-jdk nano lsb-release libglib2.0-dev tzdata doxygen --no-install-recommends && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get install -y python3.9 python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# define timezone
RUN echo "America/Sao_Paulo" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN /bin/echo -e "LANG=\"en_US.UTF-8\"" > /etc/default/local

# python
RUN python --version
RUN python3 --version
RUN pip --version
RUN pip3 --version

# cmake
ADD https://cmake.org/files/v3.11/cmake-3.11.4-Linux-x86_64.sh /tmp/cmake-3.11.4-Linux-x86_64.sh
RUN mkdir /opt/cmake
RUN sh /tmp/cmake-3.11.4-Linux-x86_64.sh --prefix=/opt/cmake --skip-license
RUN ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
RUN cmake --version

# java
ENV PATH=${PATH}:${JAVA_HOME}/bin
RUN echo ${JAVA_HOME}
RUN java -version

# google depot tools
RUN git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git /opt/depot-tools
ENV PATH=${PATH}:/opt/depot-tools

# pdfium - dependencies
RUN mkdir /build
WORKDIR /build
RUN gclient config --unmanaged https://pdfium.googlesource.com/pdfium.git
RUN gclient sync
WORKDIR /build/pdfium
RUN git checkout 31722577db9dc12a249ca6cdf2ff34e51a998360

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

RUN apt-get install -o APT::Immediate-Configure=false -f apt \
    && apt-get -f install \
    && dpkg --configure -a \
    && apt-get -y dist-upgrade \
    && echo n | ./build/install-build-deps.sh \
    && rm -rf /build

# ninja
RUN ln -nsf /opt/depot-tools/ninja-linux64 /usr/bin/ninja

# dependencies
RUN pip3 install --upgrade pip
RUN pip3 install setuptools docopt python-slugify tqdm

# libjpeg
RUN mkdir /opt/libjpeg
WORKDIR /opt/libjpeg
RUN curl https://ijg.org/files/jpegsrc.v9c.tar.gz -o jpegsrc.v9c.tar.gz
RUN tar -xvf jpegsrc.v9c.tar.gz
WORKDIR /opt/libjpeg/jpeg-9c
RUN ./configure --prefix=/usr
RUN make && make install

# nodejs and npm
RUN curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
RUN apt-get install -y nodejs
RUN npm install -g npm@latest

# cheerp
RUN mkdir /cheerp
WORKDIR /cheerp
RUN git clone https://github.com/leaningtech/cheerp-compiler
RUN git clone https://github.com/leaningtech/cheerp-utils
RUN git clone https://github.com/leaningtech/cheerp-newlib
RUN git clone https://github.com/leaningtech/cheerp-libs

# cheerp - compiler
WORKDIR /cheerp/cheerp-compiler
RUN mkdir build
WORKDIR /cheerp/cheerp-compiler/build
RUN cmake -C ../llvm/CheerpCmakeConf.cmake -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_PROJECTS=clang -G Ninja ../llvm/
RUN ninja -j4
RUN ninja install

# cheerp - utils
WORKDIR /cheerp/cheerp-utils
RUN mkdir build
WORKDIR /cheerp/cheerp-utils/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/opt/cheerp ..
RUN make install

# cheerp - c library
WORKDIR /cheerp/cheerp-newlib/newlib
RUN mkdir build
WORKDIR /cheerp/cheerp-newlib/newlib/build
RUN ../configure --host=cheerp-genericjs --with-cxx-headers=/cheerp/cheerp-compiler/libcxx/include --prefix=/opt/cheerp --enable-newlib-io-long-long --enable-newlib-iconv --enable-newlib-iconv-encodings=utf-16,utf-8,ucs_2 --enable-newlib-mb --enable-newlib-nano-formatted-io
RUN make
RUN make install
RUN CHEERP_PREFIX=/opt/cheerp ../build-bc-libs.sh genericjs

# cheerp - c++ library
WORKDIR /cheerp/cheerp-compiler/libcxxabi
RUN mkdir build
WORKDIR /cheerp/cheerp-compiler/libcxxabi/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/opt/cheerp -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=/opt/cheerp/share/cmake/Modules/CheerpToolchain.cmake -DLIBCXXABI_ENABLE_SHARED=OFF -DLIBCXXABI_ENABLE_ASSERTIONS=OFF -DLIBCXXABI_LIBCXX_PATH=/cheerp/cheerp-compiler/cheerp-libcxx/ -DLIBCXXABI_LIBCXX_INCLUDES=$CHEERP_SRC/cheerp-compiler/libcxx/include -DLIBCXXABI_ENABLE_THREADS=0 -DLLVM_CONFIG=/opt/cheerp/bin/llvm-config ..
RUN make
RUN make install

# cheerp - libraries
WORKDIR /cheerp/cheerp-libs
RUN make -C webgles install INSTALL_PREFIX=/opt/cheerp CHEERP_PREFIX=/opt/cheerp
RUN make -C wasm install INSTALL_PREFIX=/opt/cheerp CHEERP_PREFIX=/opt/cheerp
RUN make -C stdlibs install_genericjs INSTALL_PREFIX=/opt/cheerp CHEERP_PREFIX=/opt/cheerp

# cheerp - asm.js/wasm version of standard libraries
WORKDIR /cheerp/cheerp-newlib/newlib
RUN mkdir build_asmjs
WORKDIR /cheerp/cheerp-newlib/newlib/build_asmjs
RUN ../configure --host=cheerp-asmjs --with-cxx-headers=/cheerp/cheerp-compiler/libcxx/include --prefix=/opt/cheerp --enable-newlib-io-long-long --enable-newlib-iconv --enable-newlib-iconv-encodings=utf-16,utf-8,ucs_2 --enable-newlib-mb --enable-newlib-nano-formatted-io
RUN make
RUN make install
RUN CHEERP_PREFIX=/opt/cheerp ../build-bc-libs.sh asmjs

# cheerp - c++ library
WORKDIR /cheerp/cheerp-compiler/libcxx
RUN mkdir build_asmjs
WORKDIR /cheerp/cheerp-compiler/libcxx/build_asmjs
RUN cmake -DCMAKE_INSTALL_PREFIX=/opt/cheerp -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=/opt/cheerp/share/cmake/Modules/CheerpWasmToolchain.cmake -DLIBCXX_ENABLE_SHARED=OFF -DLIBCXX_ENABLE_ASSERTIONS=OFF -DLIBCXX_CXX_ABI_INCLUDE_PATHS=/cheerp/cheerp-compiler/libcxxabi/include -DLIBCXX_CXX_ABI=libcxxabi -DCMAKE_CXX_FLAGS="-fexceptions" ..
RUN make
RUN make install

# cheerp - c++ abi library
WORKDIR /cheerp/cheerp-compiler/libcxxabi
RUN mkdir build_asmjs
WORKDIR /cheerp/cheerp-compiler/libcxxabi/build_asmjs
RUN cmake -DCMAKE_INSTALL_PREFIX=/opt/cheerp -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=/opt/cheerp/share/cmake/Modules/CheerpWasmToolchain.cmake -DLIBCXXABI_ENABLE_SHARED=OFF -DLIBCXXABI_ENABLE_ASSERTIONS=OFF -DLIBCXXABI_LIBCXX_PATH=/cheerp/cheerp-compiler/libcxx/ -DLIBCXXABI_LIBCXX_INCLUDES=/cheerp/cheerp-compiler/libcxx/include -DLIBCXXABI_ENABLE_THREADS=0 -DLLVM_CONFIG=/opt/cheerp/bin/llvm-config ..
RUN make
RUN make install

# cheerp - libraries
WORKDIR /cheerp/cheerp-libs
RUN make -C stdlibs install_asmjs INSTALL_PREFIX=/opt/cheerp CHEERP_PREFIX=/opt/cheerp

# version
RUN cc --version

# test
RUN bash -c 'echo "int main() { return 0; }" > /tmp/main.cc'
RUN bash -c 'cc -o /tmp/main.html /tmp/main.cc'

# working dir
WORKDIR /app