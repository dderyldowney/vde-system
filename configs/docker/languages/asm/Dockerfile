# ASM VM Dockerfile
# Inherits from vde-base and adds assembler tools at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y nasm yasm gdb && \
    rm -rf /var/lib/apt/lists/*
