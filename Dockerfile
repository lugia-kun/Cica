FROM ubuntu:18.04
MAINTAINER lugia-kun <lugia.kun@gmail.com>

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install \
    software-properties-common gcc libgtk-3-dev python3-dev libxml2-dev \
    automake autoconf patch unar git curl

WORKDIR /work
RUN git clone https://github.com/fontforge/fontforge.git

WORKDIR /work/fontforge
RUN git checkout e688b8c4dc634dcc128709f84b98f2407294f3fb
RUN curl -L https://github.com/fontforge/fontforge/files/2065028/addPosSubBytesString-patch.txt | patch -p1
RUN ./bootstrap
RUN ./configure --prefix=/usr && make && make install

WORKDIR /work
ADD entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT entrypoint.sh
