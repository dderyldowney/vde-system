# Haskell VM Dockerfile
# Inherits from vde-base and adds GHC/Cabal at build-time
FROM vde-base:latest

ARG USERNAME=devuser

RUN apt-get update -y && \
    apt-get install -y ghc cabal-install && \
    rm -rf /var/lib/apt/lists/*
