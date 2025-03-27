#!/bin/bash
#
# A script to run a Docker container with X11 (and Wayland) forwarding.
# This is for local dev only!
#
# Usage:
#   ./run_docker.sh [OPTIONS] <container_name>
#
# Options:
#   -h  Show help
#   -b  Build image (with cache)
#   -n  Build image (no cache)
#   -i  Interactive
#   -d  Detached
#
# Example:
#   ./run_docker.sh -b -it myimage
#   ./run_docker.sh -b -itd myimage
#

usage() {
  cat <<EOF
Usage: $0 [OPTIONS] <container_name>

Options:
  -h  Show this help message
  -b  Build the Docker image using cached layers
  -n  Build the Docker image without using cache
  -i  Pass the interactive flag (-i) to docker run
  -d  Run container in detached mode

Example:
  $0 -b -it myimage
EOF
}

BUILD=false
NO_CACHE=false
DETACHED=false
EXTRA_ARGS=()

while getopts "hbnitd" opt; do
    case "$opt" in
        h) usage; exit 0;;
        b) BUILD=true;;
        n) BUILD=true; NO_CACHE=true;;
        i) EXTRA_ARGS+=("-it");;
        d) DETACHED=true;;
        *) usage; exit 1;;
    esac
done
shift $((OPTIND - 1))

CONTAINER_NAME="$1"
if [ -z "$CONTAINER_NAME" ]; then
    echo "Error: Container name is required."
    usage
    exit 1
fi

# Build the Docker image if requested
if [ "$BUILD" = true ]; then
    echo "Building image '$CONTAINER_NAME'..."
    if [ "$NO_CACHE" = true ]; then
        docker build --no-cache -t "$CONTAINER_NAME" .
    else
        docker build -t "$CONTAINER_NAME" .
    fi
fi

# Make sure DISPLAY is set; otherwise X apps won't open.
if [ -z "$DISPLAY" ]; then
    echo "Warning: \$DISPLAY is not set. X11 GUI apps may not work."
    echo "If your Wayland session is using XWayland, typically you have DISPLAY=:0 or DISPLAY=:1."
    echo "Please ensure your host's DISPLAY variable is set correctly."
fi

echo "Granting access to X server for local Docker connections..."
# This allows Docker containers (on the same system) to connect to X without .Xauthority.
xhost +local:docker

DOCKER_RUN_OPTS=(
    --rm
    -v "$(pwd):/app/project"
    -w /app/project
    -e "DISPLAY=${DISPLAY}"
    -v "/tmp/.X11-unix:/tmp/.X11-unix:rw"
    --net=host
    "${EXTRA_ARGS[@]}"
)

# Detect and configure Wayland socket forwarding if in use.
if [ -n "$WAYLAND_DISPLAY" ]; then
    echo "Wayland session detected. Setting up Wayland socket forwarding..."
    if [ -z "$XDG_RUNTIME_DIR" ]; then
        echo "Warning: \$XDG_RUNTIME_DIR is not set. Cannot forward Wayland socket."
    else
        DOCKER_RUN_OPTS+=(-e "WAYLAND_DISPLAY=$WAYLAND_DISPLAY")
        DOCKER_RUN_OPTS+=(-e "XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR")
        DOCKER_RUN_OPTS+=(-v "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY:$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY")
    fi
fi

if [ "$DETACHED" = true ]; then
    echo "Starting container '$CONTAINER_NAME' in detached mode..."
    docker run -d --name "$CONTAINER_NAME" \
    "${DOCKER_RUN_OPTS[@]}" \
    "$CONTAINER_NAME" \
    /bin/bash
    
    echo "Container started in detached mode."
    echo "To attach: docker exec -it $CONTAINER_NAME /bin/bash"
else
    echo "Starting container '$CONTAINER_NAME' interactively..."
    docker run \
    "${DOCKER_RUN_OPTS[@]}" \
    "$CONTAINER_NAME" \
    /bin/bash
fi

echo "Revoking X server access from local Docker connections..."
xhost -local:docker
