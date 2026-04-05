#!/usr/bin/env zsh
# VDE Setup Script: redis
# Part of the Universal Script Parity (USP) mandate.

apt-get update
apt-get install -y redis-tools
apt-get clean
rm -rf /var/lib/apt/lists/*
