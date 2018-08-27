FROM ubuntu:18.04
MAINTAINER miiton <468745+miiton@users.noreply.github.com>

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install \
    software-properties-common fontforge unar git curl

ADD entrypoint.sh /usr/local/bin/entrypoint.sh
WORKDIR /work

ENTRYPOINT entrypoint.sh
