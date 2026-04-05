#!/usr/bin/env zsh
# VDE Setup Script: mysql
# Part of the Universal Script Parity (USP) mandate.

apt-get update
apt-get install -y default-mysql-server
apt-get clean
rm -rf /var/lib/apt/lists/*
