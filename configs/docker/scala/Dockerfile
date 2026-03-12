# Scala VM Dockerfile
# Inherits from vde-base and adds Scala at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y scala && \
    rm -rf /var/lib/apt/lists/*
