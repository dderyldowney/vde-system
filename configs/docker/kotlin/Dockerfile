# Kotlin VM Dockerfile
# Inherits from vde-base and adds Kotlin at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y kotlin && \
    curl -s "https://get.sdkman.io" | bash && \
    su - ${USERNAME} -c "source ~/.sdkman/bin/sdkman-init.sh && sdk install kotlin" && \
    rm -rf /var/lib/apt/lists/*
