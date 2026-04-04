#!/usr/bin/env zsh
# vde-rust initialization (Anti-Entropy Hardened)
set -e
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o /tmp/rustup.sh
chmod +x /tmp/rustup.sh
su - devuser -c "sh /tmp/rustup.sh -y"

# Idempotent persistence
grep -q "cargo/env" /home/devuser/.zshenv 2>/dev/null || {
    echo 'source $HOME/.cargo/env' >> /home/devuser/.zshenv
}
