#!/usr/bin/env zsh
# VDE Setup Script: mongodb
# Part of the Universal Script Parity (USP) mandate.

apt-get update
apt-get install -y mongodb-org-shell
apt-get clean
rm -rf /var/lib/apt/lists/*
