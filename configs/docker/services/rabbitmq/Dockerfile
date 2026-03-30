# RabbitMQ VM Dockerfile
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y erlang-nox rabbitmq-server && \
    rm -rf /var/lib/apt/lists/*
