FROM ubuntu:18.04

# general
ARG DEBIAN_FRONTEND=noninteractive

ENV PROJ_TARGET="android"

ENV ANDROID_NDK_VERSION="r21d"
ENV ANDROID_COMPILE_SDK="30"
ENV ANDROID_BUILD_TOOLS="30.0.2"
ENV ANDROID_SDK_TOOLS_REV="4333796"
ENV ANDROID_CMAKE_REV="3.6.4111459"
ENV ANDROID_CMAKE_REV_3_10="3.10.2.4988404"
ENV ANDROID_HOME="/opt/android-sdk-linux"
ENV ANDROID_NDK_HOME="/opt/android-ndk-linux"

ENV GRADLE_VERSION="6.1.1"
ENV GRADLE_HOME="/opt/gradle-6.1.1"

ENV JAVA_VERSION="8"
ENV JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"

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
RUN git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git /opt/depot-tools
ENV PATH=${PATH}:/opt/depot-tools

# pdfium - dependencies
RUN mkdir /build
WORKDIR /build
RUN gclient config --unmanaged https://pdfium.googlesource.com/pdfium.git
RUN gclient sync
WORKDIR /build/pdfium
RUN git checkout 7e2c12e172e644744fc2828e7000b3689537af12

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

RUN apt-get install -o APT::Immediate-Configure=false -f apt \
    && apt-get -f install \
    && dpkg --configure -a \
    && apt-get -y dist-upgrade \
    && echo n | ./build/install-build-deps-android.sh \
    && rm -rf /build

# ninja
RUN ln -nsf /opt/depot-tools/ninja-linux64 /usr/bin/ninja

# dependencies
RUN pip3 install --upgrade pip
RUN pip3 install setuptools docopt pygemstones

# working dir
WORKDIR /app
