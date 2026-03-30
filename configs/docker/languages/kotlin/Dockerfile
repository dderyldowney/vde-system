# Kotlin VM Dockerfile
# Inherits from vde-base and adds Kotlin at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y curl zip unzip default-jdk && \
    su ${USERNAME} -c "curl -s 'https://get.sdkman.io' | bash" && \
    su ${USERNAME} -c "source /home/${USERNAME}/.sdkman/bin/sdkman-init.sh && sdk install kotlin" && \
    rm -rf /var/lib/apt/lists/*
