FROM ubuntu:18.04
MAINTAINER lugia-kun <lugia.kun@gmail.com>

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install \
    software-properties-common gcc libgtk-3-dev python3-dev libxml2-dev \
    automake autoconf patch unar git curl

WORKDIR /work
RUN git clone https://github.com/fontforge/fontforge.git

WORKDIR /work/fontforge
RUN git checkout dad4fb502202e8b467d571f5ab0f07b7a3565f69
RUN ./bootstrap
RUN ./configure --prefix=/usr && make && make install

WORKDIR /work
RUN rm -rf fontforge
ADD entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT entrypoint.sh
