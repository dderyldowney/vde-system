# C VM Dockerfile
# Inherits from vde-base and adds C compiler at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y gcc make cmake gdb && \
    rm -rf /var/lib/apt/lists/*
