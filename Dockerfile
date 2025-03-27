FROM ubuntu:22.04
LABEL maintainer="Shady Gmira shady.gmira@gmail.com, Chrysanthi Mandraveli chrysanthimad@gmail.com"

ENV DEBIAN_FRONTEND=noninteractive

# Install essential packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    python3 \
    python3-pip \
    python3-tk \
    python3-venv

# Create a non-root user with a dynamic UID (passed as a build argument)
USER "$USER"
WORKDIR /app

ARG UID=1000
ENV USER=devuser
RUN useradd -m -u "$UID" "$USER"


