FROM ubuntu:20.04

# general
ARG DEBIAN_FRONTEND=noninteractive

ENV PROJ_TARGET="cheerp"
ENV JAVA_VERSION="8"
ENV JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"

# packages
RUN apt-get -y update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:leaningtech-dev/cheerp-ppa && \
    apt-get -y update && \
    apt-get install -y build-essential sudo file git wget curl ninja-build zip unzip tar software-properties-common openjdk-${JAVA_VERSION}-jdk nano lsb-release libglib2.0-dev tzdata doxygen python3 python3-pip cheerp-core --no-install-recommends && \
    apt-get upgrade && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# define timezone
RUN echo "America/Sao_Paulo" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN /bin/echo -e "LANG=\"en_US.UTF-8\"" > /etc/default/local

# python
RUN python3 --version
RUN pip3 --version

# cmake
RUN pip3 install cmake
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

RUN ln -sf /usr/bin/python3 /usr/bin/python
RUN ln -sf /usr/bin/pip3 /usr/bin/pip

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

# compiler version
RUN cc --version

# test
RUN bash -c 'echo "int main() { return 0; }" > /tmp/main.cc'
RUN bash -c 'cc -o /tmp/main.html /tmp/main.cc'

# working dir
WORKDIR /app