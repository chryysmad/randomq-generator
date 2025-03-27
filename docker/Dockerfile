FROM ubuntu:22.04
LABEL maintainer="Shady Gmira shady.gmira@gmail.com, Chrysanthi Mandraveli chrysanthimad@gmail.com"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    openssh-client \
    ca-certificates \
    gnupg \
    python3 \
    python3-pip \
    python3-tk \
    python3-venv \
    x11-apps && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ARG UID
ARG GID
ARG USERNAME

RUN groupadd --gid "$GID" "$USERNAME" && \
    useradd -m -u "$UID" -g "$GID" "$USERNAME"

ENV USER=$USERNAME
ENV HOME=/home/$USERNAME

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
