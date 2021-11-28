FROM ubuntu:18.04

# general
ARG DEBIAN_FRONTEND=noninteractive

ENV PROJ_TARGET="wasm"

ENV JAVA_VERSION="8"
ENV JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"

ENV PYTHONIOENCODING="utf8"
ENV LC_ALL=C.UTF-8

# packages
RUN apt-get -y update
RUN apt-get install -y build-essential sudo file git wget curl cmake ninja-build zip unzip tar python3 python3-pip openjdk-${JAVA_VERSION}-jdk nano lsb-release libglib2.0-dev tzdata doxygen python3-setuptools --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# define timezone
RUN echo "America/Sao_Paulo" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN /bin/echo -e "LANG=\"en_US.UTF-8\"" > /etc/default/local

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
RUN git checkout 64a3691918bca26c4d233c8c897d926a39e4a8b7

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
RUN pip3 install setuptools docopt pygemstones

# libjpeg
RUN mkdir /opt/libjpeg
WORKDIR /opt/libjpeg
RUN curl https://ijg.org/files/jpegsrc.v9c.tar.gz -o jpegsrc.v9c.tar.gz
RUN tar -xvf jpegsrc.v9c.tar.gz
WORKDIR /opt/libjpeg/jpeg-9c
RUN ./configure --prefix=/usr
RUN make && make install

# emsdk
RUN mkdir /emsdk
WORKDIR /emsdk
RUN git clone https://github.com/emscripten-core/emsdk.git .
RUN ./emsdk install 3.0.0
RUN ./emsdk activate 3.0.0
ENV PATH="${PATH}:/emsdk:/emsdk/upstream/emscripten"

# cache system libraries
RUN bash -c 'echo "int main() { return 0; }" > /tmp/main.cc'
RUN bash -c 'source /emsdk/emsdk_env.sh && em++ -s USE_ZLIB=1 -s USE_LIBJPEG=1 -s USE_PTHREADS=1 -s ASSERTIONS=1 -o /tmp/main.html /tmp/main.cc'

# nodejs and npm
RUN curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
RUN apt-get install -y nodejs
RUN npm install -g npm@latest

# working dir
WORKDIR /app
