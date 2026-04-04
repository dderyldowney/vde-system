#!/usr/bin/env zsh
# vde-js initialization (Anti-Entropy Hardened)
set -e
curl -fsSL https://deb.nodesource.com/setup_22.x -o /tmp/setup_node.sh
bash /tmp/setup_node.sh
apt-get install -y nodejs
