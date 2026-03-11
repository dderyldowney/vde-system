# Swift VM Dockerfile
# Inherits from vde-base and adds Swift toolchain at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y binutils git libc6-dev curl && \
    rm -rf /var/lib/apt/lists/*
