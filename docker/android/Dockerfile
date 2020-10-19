FROM ubuntu:16.04

# general
ARG DEBIAN_FRONTEND=noninteractive

ENV PROJ_TARGET="android"

ENV ANDROID_NDK_VERSION="r21d"
ENV ANDROID_COMPILE_SDK="30"
ENV ANDROID_BUILD_TOOLS="30.0.2"
ENV ANDROID_SDK_TOOLS_REV="4333796"
ENV ANDROID_CMAKE_REV="3.6.4111459"
ENV ANDROID_CMAKE_REV_3_10="3.10.2.4988404"
ENV GRADLE_VERSION="6.1.1"
ENV JAVA_VERSION="8"

ENV JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"
ENV GRADLE_HOME="/opt/gradle-6.1.1"
ENV ANDROID_HOME="/opt/android-sdk-linux"
ENV ANDROID_NDK_HOME="/opt/android-ndk-linux"

ENV PATH ${PATH}:${ANDROID_HOME}/platform-tools/:${ANDROID_NDK_HOME}:${ANDROID_HOME}/ndk-bundle:${ANDROID_HOME}/tools/bin/

# packages
RUN apt-get -y update
RUN apt-get install -y build-essential sudo file git wget curl cmake ninja-build zip unzip tar python2.7 python3 python3-pip openjdk-${JAVA_VERSION}-jdk nano lsb-release --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

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

# # ndk
# RUN mkdir /opt/android-ndk-tmp && \
#     cd /opt/android-ndk-tmp && \
#     wget -q https://dl.google.com/android/repository/android-ndk-${ANDROID_NDK_VERSION}-linux-x86_64.zip && \
#     unzip -q android-ndk-${ANDROID_NDK_VERSION}-linux-x86_64.zip && \
#     mv ./android-ndk-${ANDROID_NDK_VERSION} ${ANDROID_NDK_HOME} && \
#     cd ${ANDROID_NDK_HOME} && \
#     rm -rf /opt/android-ndk-tmp

# # sdk
# RUN mkdir -p ${ANDROID_HOME} && \
#     wget --quiet --output-document=${ANDROID_HOME}/android-sdk.zip https://dl.google.com/android/repository/sdk-tools-linux-${ANDROID_SDK_TOOLS_REV}.zip && \
#     unzip -qq ${ANDROID_HOME}/android-sdk.zip -d ${ANDROID_HOME} && \
#     rm ${ANDROID_HOME}/android-sdk.zip && \
#     mkdir -p $HOME/.android && \
#     echo 'count=0' > $HOME/.android/repositories.cfg

# RUN yes | sdkmanager --licenses > /dev/null && \ 
#     yes | sdkmanager --update && \
#     yes | sdkmanager 'tools' && \
#     yes | sdkmanager 'platform-tools' && \
#     yes | sdkmanager 'build-tools;'$ANDROID_BUILD_TOOLS && \
#     yes | sdkmanager 'platforms;android-'$ANDROID_COMPILE_SDK && \
#     yes | sdkmanager 'platforms;android-28' && \
#     yes | sdkmanager 'extras;android;m2repository' && \
#     yes | sdkmanager 'extras;google;google_play_services' && \
#     yes | sdkmanager 'extras;google;m2repository' 

# RUN yes | sdkmanager 'cmake;'$ANDROID_CMAKE_REV && \
#     yes | sdkmanager --channel=3 --channel=1 'cmake;'$ANDROID_CMAKE_REV_3_10

# google depot tools
RUN git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git /opt/depot-tools
ENV PATH=${PATH}:/opt/depot-tools

# pdfium - dependencies
RUN mkdir /build
WORKDIR /build
RUN gclient config --unmanaged https://pdfium.googlesource.com/pdfium.git
RUN gclient sync
WORKDIR /build/pdfium
RUN git checkout e21911cc1c77d39dbc51001845bbfce2783e6514

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

RUN apt-get install -o APT::Immediate-Configure=false -f apt 
RUN apt-get -f install
RUN dpkg --configure -a
RUN apt-get -y dist-upgrade
RUN echo n | ./build/install-build-deps-android.sh
RUN rm -rf /build

# ninja
RUN ln -nsf /opt/depot-tools/ninja-linux64 /usr/bin/ninja

# dependencies
RUN pip3 install --upgrade pip
RUN pip3 install docopt python-slugify tqdm

# working dir
WORKDIR /app