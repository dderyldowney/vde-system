#!/usr/bin/env zsh
# VDE Setup Script: rabbitmq
# Part of the Universal Script Parity (USP) mandate.

apt-get update
apt-get install -y erlang-nox rabbitmq-server
apt-get clean
rm -rf /var/lib/apt/lists/*
