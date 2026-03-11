# Lua VM Dockerfile
# Inherits from vde-base and adds Lua at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y lua5.4 luarocks && \
    rm -rf /var/lib/apt/lists/*
