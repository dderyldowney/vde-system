#!/usr/bin/env zsh
# vde-js initialization (Anti-Entropy Hardened)
# Part of the Universal Script Parity (USP) mandate.
set -e

# 1. Install core tools
apt-get update
apt-get install -y curl git build-essential

# 2. Setup Node.js
curl -fsSL https://deb.nodesource.com/setup_22.x -o /tmp/setup_node.sh
bash /tmp/setup_node.sh
apt-get install -y nodejs

# 3. Cleanup
apt-get clean
rm -rf /var/lib/apt/lists/*
