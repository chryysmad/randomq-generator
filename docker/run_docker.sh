#!/bin/bash
# Script to build the Docker image. Dynamically creates the user
# based on `$(id -u)` and `$(id -g)` to preserve file ownership.

usage() {
    echo "Usage: $0 [-h] [-b] [-n] [-u]"
    echo " -h                               This help message"
    echo " -b                               Build the docker image, with cached layers"
    echo " -n                               Build the docker image, without cached layers"
    echo " -u                               Run docker compose up"
}

if [ "$#" -lt 1 ]; then
    usage
    exit 1
fi

BUILD=false
BUILD_ARGS=""
COMPOSEUP=false

while getopts "hbnu" opt; do
    case ${opt} in
        h )
            usage
            exit 0
            ;;
        b )
            BUILD=true
            ;;
        n )
            BUILD=true
            BUILD_ARGS="--no-cache"
            ;;
        u )
            COMPOSEUP=true
            ;;
        * )
            usage
            exit 1
            ;;
    esac
done

# Export host user info for Docker build
export USER_UID=$(id -u)
export USER_GID=$(id -g)
export USERNAME=$(id -un)
export HOME=$HOME
export SSH_AUTH_SOCK=$SSH_AUTH_SOCK

if [ "$BUILD" = true ]; then
    echo "Building docker image"
    if [ -n "$BUILD_ARGS" ]; then
        docker compose build $BUILD_ARGS
    else
        docker compose build
    fi
fi

if [ "$COMPOSEUP" = true ]; then
    echo "Starting docker container"
    docker compose up -d
    docker compose exec -it randomq bash
fi
