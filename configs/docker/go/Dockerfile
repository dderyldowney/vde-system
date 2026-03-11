# Go VM Dockerfile
# Inherits from vde-base and adds Go at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y golang-go && \
    rm -rf /var/lib/apt/lists/*
