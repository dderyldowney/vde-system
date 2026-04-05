#!/usr/bin/env zsh
# VDE Setup Script: testport2
# Part of the Universal Script Parity (USP) mandate.

apt-get update
apt-get install -y top
apt-get clean
rm -rf /var/lib/apt/lists/*
