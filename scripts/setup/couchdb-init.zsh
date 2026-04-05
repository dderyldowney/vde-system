#!/usr/bin/env zsh
# VDE Setup Script: couchdb
# Part of the Universal Script Parity (USP) mandate.

apt-get update
apt-get install -y couchdb
apt-get clean
rm -rf /var/lib/apt/lists/*
