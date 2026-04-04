#!/usr/bin/env zsh
# vde-csharp initialization (Anti-Entropy Hardened)
set -e
DOTNET_INSTALL_DIR="/usr/share/dotnet"
mkdir -p "${DOTNET_INSTALL_DIR}"

curl -sSL https://dot.net/v1/dotnet-install.sh -o /tmp/dotnet-install.sh
bash /tmp/dotnet-install.sh --version 8.0.100 --install-dir "${DOTNET_INSTALL_DIR}"

ln -sf "${DOTNET_INSTALL_DIR}/dotnet" /usr/bin/dotnet

# Idempotent persistence
grep -q "DOTNET_ROOT" /home/devuser/.zshenv 2>/dev/null || {
    echo "export DOTNET_ROOT=${DOTNET_INSTALL_DIR}" >> /home/devuser/.zshenv
    echo "export PATH=\$PATH:${DOTNET_INSTALL_DIR}" >> /home/devuser/.zshenv
}
