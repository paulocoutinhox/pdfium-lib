FROM ubuntu:22.04

# general
ARG DEBIAN_FRONTEND=noninteractive

ENV PROJ_TARGET="android"

ENV ANDROID_NDK_VERSION="r25c"
ENV ANDROID_HOME="/opt/android-sdk-linux"
ENV ANDROID_NDK_HOME="/opt/android-ndk-linux"

ENV GRADLE_VERSION="8.10"
ENV GRADLE_HOME="/opt/gradle-8.10"

ENV JAVA_VERSION="17"
ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64/"

ENV PYTHONIOENCODING="utf8"
ENV LC_ALL=C.UTF-8

ENV PATH ${PATH}:${ANDROID_HOME}/platform-tools/:${ANDROID_NDK_HOME}:${ANDROID_HOME}/ndk-bundle:${ANDROID_HOME}/tools/bin/

# packages
RUN apt-get -y update
RUN apt-get install -y build-essential sudo file git wget curl cmake ninja-build zip unzip tar python2.7 python3 python3-pip openjdk-${JAVA_VERSION}-jdk nano lsb-release tzdata python3-setuptools --no-install-recommends && \
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

# gradle
ENV PATH=${PATH}:${GRADLE_HOME}/bin
RUN wget -q https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip \
    && unzip gradle-${GRADLE_VERSION}-bin.zip -d /opt \
    && rm gradle-${GRADLE_VERSION}-bin.zip
RUN gradle --version

# google depot tools
ENV DEPOT_TOOLS_UPDATE=0
ENV DEPOT_TOOLS_WIN_TOOLCHAIN=0
RUN git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git -b main /opt/depot-tools
ENV PATH=${PATH}:/opt/depot-tools

# pdfium
RUN mkdir /build
WORKDIR /build
RUN gclient config --custom-var checkout_configuration=minimal --unmanaged https://pdfium.googlesource.com/pdfium.git
RUN echo "target_os = [ 'android' ]" >> .gclient
RUN gclient sync -r origin/chromium/7169 --no-history --shallow

# pdfium reset and clean directories
RUN git -C /build/pdfium reset --hard
RUN git -C /build/pdfium clean -df

RUN git -C /build/pdfium/build reset --hard
RUN git -C /build/pdfium/build clean -df

RUN git -C /build/pdfium/third_party/libjpeg_turbo reset --hard
RUN git -C /build/pdfium/third_party/libjpeg_turbo clean -df

RUN git -C /build/pdfium/base/allocator/partition_allocator reset --hard
RUN git -C /build/pdfium/base/allocator/partition_allocator clean -df

# pdfium checkout
WORKDIR /build/pdfium
RUN git status

# system dependencies
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN apt-get install -o APT::Immediate-Configure=false -f apt \
    && apt-get -f install \
    && dpkg --configure -a \
    && apt-get -y dist-upgrade \
    && echo n | ./build/install-build-deps.sh --android || true \
    && rm -rf /build

# ninja
RUN ln -nsf /opt/depot-tools/ninja-linux64 /usr/bin/ninja

# dependencies
RUN pip3 install --upgrade pip
RUN pip3 install setuptools docopt pygemstones

# working dir
WORKDIR /app
