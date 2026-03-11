# Scala VM Dockerfile
# Inherits from vde-base and adds Scala/sbt at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y scala-defaults sbt && \
    rm -rf /var/lib/apt/lists/*
