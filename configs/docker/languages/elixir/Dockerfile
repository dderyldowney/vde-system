# Elixir VM Dockerfile
# Inherits from vde-base and adds Elixir/Erlang at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y elixir erlang && \
    rm -rf /var/lib/apt/lists/*
