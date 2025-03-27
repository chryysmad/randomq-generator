#!/bin/bash
xhost +local:docker

# Set up Wayland forwarding if running a Wayland session.
WAYLAND_ARGS=""
if [ -n "$WAYLAND_DISPLAY" ] && [ -n "$XDG_RUNTIME_DIR" ]; then
    WAYLAND_ARGS="-v $XDG_RUNTIME_DIR/$WAYLAND_DISPLAY:$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY \
    -e WAYLAND_DISPLAY=$WAYLAND_DISPLAY \
    -e XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR"
    echo "Running in Wayland session. Setting up Wayland forwarding."
fi

docker run -it --rm \
--net=host \
-e DISPLAY=$DISPLAY \
-v /tmp/.X11-unix:/tmp/.X11-unix \
-v $HOME/.Xauthority:/home/dev/.Xauthority \
-u $(id -u):$(id -g) \
-v $(pwd):/app \
-v $HOME/.ssh:/home/dev/.ssh \
randomq
# $WAYLAND_ARGS \

xhost -local:docker
