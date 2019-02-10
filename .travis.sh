#!/bin/bash

set -ev

tag=$(git log -n1 --format=%H -- Dockerfile entrypoint.sh)
docker pull lugia-kun/ocami:$tag
if [[ $? == 0 ]]; then
    docker tag lugia-kun/ocami:$tag ocami_ocami:latest
else
    docker-compose build
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    docker tag ocami_ocami:latest lugiakun/ocami:$tag
    docker push lugiakun/ocami:$tag
fi
