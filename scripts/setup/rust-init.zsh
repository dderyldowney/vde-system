#!/usr/bin/env zsh
# vde-rust initialization (Anti-Entropy Hardened)
# Part of the Universal Script Parity (USP) mandate.
set -e

# 1. Install core tools
apt-get update
apt-get install -y build-essential curl git

# 2. Setup Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o /tmp/rustup.sh
chmod +x /tmp/rustup.sh
su - devuser -c "sh /tmp/rustup.sh -y"

# 3. Cleanup
apt-get clean
rm -rf /var/lib/apt/lists/*

# Idempotent persistence
grep -q "cargo/env" /home/devuser/.zshenv 2>/dev/null || {
    echo 'source $HOME/.cargo/env' >> /home/devuser/.zshenv
}
