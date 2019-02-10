#!/bin/bash

set -ev

tag=$(git log -n1 --format=%H -- Dockerfile entrypoint.sh)
docker pull lugiakun/ocami:$tag
if [[ $? == 0 ]]; then
    docker tag lugiakun/ocami:$tag ocami_ocami:latest
else
    docker-compose build
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    docker tag ocami_ocami:latest lugiakun/ocami:$tag
    docker push lugiakun/ocami:$tag
fi
