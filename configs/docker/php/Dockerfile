# PHP VM Dockerfile
# Inherits from vde-base and adds PHP/Composer at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y php php-cli php-xml php-mbstring php-curl composer && \
    rm -rf /var/lib/apt/lists/*
