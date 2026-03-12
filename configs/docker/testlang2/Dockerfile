# Testlang VM Dockerfile (for testing only)
# Inherits from vde-base and adds curl for testing
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
