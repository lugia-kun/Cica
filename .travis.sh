#!/bin/bash

set -ev

tag=$(git log -n1 --format=%H -- Dockerfile entrypoint.sh)
if docker pull lugiakun/ocami:$tag; then
    docker tag lugiakun/ocami:$tag ocami_ocami:latest
else
    docker-compose build
    if echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin; then
        docker tag ocami_ocami:latest lugiakun/ocami:$tag
        docker push lugiakun/ocami:$tag
    fi
fi
