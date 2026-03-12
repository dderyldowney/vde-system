# Swift VM Dockerfile
# Inherits from vde-base and adds Swift toolchain at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y binutils git libc6-dev curl libedit2 libgcc-12-dev libpython3.11 libsqlite3-0 libstdc++-12-dev libxml2-dev zlib1g-dev libncurses6 && \
    curl -fsSL https://swift.org/builds/swift-5.10.1-release/debian12/swift-5.10.1-RELEASE/swift-5.10.1-RELEASE-debian12.tar.gz -o /tmp/swift.tar.gz && \
    tar -xzf /tmp/swift.tar.gz -C / --strip-components=1 && \
    rm /tmp/swift.tar.gz && \
    rm -rf /var/lib/apt/lists/*
