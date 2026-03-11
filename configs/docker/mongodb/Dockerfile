# MongoDB VM Dockerfile
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y mongodb-org-shell && \
    rm -rf /var/lib/apt/lists/*
