# Java VM Dockerfile
# Inherits from vde-base and adds JDK/Maven/Gradle at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y default-jdk maven gradle && \
    rm -rf /var/lib/apt/lists/*
