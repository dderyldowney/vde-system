# Flutter VM Dockerfile
# Inherits from vde-base and adds Flutter SDK at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y curl git unzip xz-utils zip libglu1-mesa && \
    rm -rf /var/lib/apt/lists/*

RUN su ${USERNAME} -c "git clone --depth 1 https://github.com/flutter/flutter.git /home/${USERNAME}/flutter"

RUN echo 'export PATH=$HOME/flutter/bin:$PATH' >> /home/${USERNAME}/.zshrc && \
    echo 'export PATH=$HOME/flutter/bin:$PATH' >> /home/${USERNAME}/.zprofile

ENV PATH=/home/${USERNAME}/flutter/bin:${PATH}
