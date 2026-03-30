# C# VM Dockerfile
# Inherits from vde-base and adds .NET SDK at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y wget apt-transport-https && \
    wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb && \
    dpkg -i /tmp/packages-microsoft-prod.deb || apt-get install -f -y && \
    rm /tmp/packages-microsoft-prod.deb && \
    apt-get update -y && \
    apt-get install -y dotnet-sdk-8.0 aspnetcore-runtime-8.0 && \
    rm -rf /var/lib/apt/lists/*
