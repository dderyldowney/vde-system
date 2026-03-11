# Ruby VM Dockerfile
# Inherits from vde-base and adds Ruby at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y ruby-full && \
    rm -rf /var/lib/apt/lists/*
