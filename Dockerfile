FROM ubuntu:18.04 AS fontforge-build

RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install \
    software-properties-common gcc python3-dev libxml2-dev \
    gettext libtool libfreetype6-dev automake autoconf patch git

WORKDIR /work
RUN git clone https://github.com/fontforge/fontforge.git

WORKDIR /work/fontforge
RUN git checkout 1d421d1a6f0a76c4bf7dc947d68c03614232d341
RUN ./bootstrap
RUN ./configure --prefix=/opt/fontforge && make && make install

FROM ubuntu:18.04
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install \
    libltdl7 libfreetype6 libpython3.6 libglib2.0-0 libxml2 curl unar

WORKDIR /work
COPY --from=fontforge-build /opt/fontforge /opt/fontforge
ADD entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT entrypoint.sh
