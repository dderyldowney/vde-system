# MySQL VM Dockerfile
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y default-mysql-server && \
    rm -rf /var/lib/apt/lists/*
