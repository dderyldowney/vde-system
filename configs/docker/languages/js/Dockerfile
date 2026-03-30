# JavaScript/Node.js VM Dockerfile
# Inherits from vde-base and adds Node.js at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update && \
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*
