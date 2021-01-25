FROM ubuntu:18.04

# general
ARG DEBIAN_FRONTEND=noninteractive

ENV PROJ_TARGET="wasm"

ENV JAVA_VERSION="8"

ENV JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"

# packages
RUN apt-get -y update
RUN apt-get install -y build-essential sudo file git wget curl cmake ninja-build zip unzip tar python2.7 python3 python3-pip openjdk-${JAVA_VERSION}-jdk nano lsb-release libglib2.0-dev tzdata --no-install-recommends && \
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
RUN git checkout d3664703dfa9dc530246de50a16b8e8523b676d6

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

RUN apt-get install -o APT::Immediate-Configure=false -f apt 
RUN apt-get -f install
RUN dpkg --configure -a
RUN apt-get -y dist-upgrade
RUN echo n | ./build/install-build-deps.sh
RUN rm -rf /build

# ninja
RUN ln -nsf /opt/depot-tools/ninja-linux64 /usr/bin/ninja

# dependencies
RUN pip3 install --upgrade pip
RUN pip3 install docopt python-slugify tqdm

# emsdk
RUN mkdir /emsdk
WORKDIR /emsdk
RUN git clone https://github.com/emscripten-core/emsdk.git .
RUN ./emsdk install 2.0.12
RUN ./emsdk activate 2.0.12
ENV PATH="${PATH}:/emsdk:/emsdk/upstream/emscripten:/emsdk/node/12.18.1_64bit/bin"

# working dir
WORKDIR /app