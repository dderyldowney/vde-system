# R VM Dockerfile
# Inherits from vde-base and adds R at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y r-base r-cran-littler && \
    rm -rf /var/lib/apt/lists/*
