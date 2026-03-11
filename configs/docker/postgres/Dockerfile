# PostgreSQL VM Dockerfile
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*
