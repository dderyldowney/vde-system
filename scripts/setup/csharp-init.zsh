#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE USP Hydration Script: csharp
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
typeset vde_csharp_pkgs="curl libicu-dev git"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_csharp_pkgs}

# 3. DOTNET INSTALLATION (Shell-Safe Handshake)
typeset dev_home="/home/devuser"
mkdir -p "${dev_home}"

# Download installer
curl -fsSL https://dot.net/v1/dotnet-install.sh -o /tmp/dotnet-install.sh
chmod +x /tmp/dotnet-install.sh

# Mandate C exception (Signet #551): dotnet-install.sh is a Bash script (uses
# bashisms and relies on pipefail); Microsoft ships no zsh/native installer, and
# running it under sh triggers pipefail errors. Invoking it under bash is the
# unavoidable third-party path. (A direct SDK-tarball install was considered but
# kept on the vendor installer so channel 8.0 patch releases track automatically.)
sudo -H -u devuser bash /tmp/dotnet-install.sh --channel 8.0 --install-dir "${dev_home}/.dotnet"

# 4. PERSISTENCE ANCHOR
typeset _zshenv="${dev_home}/.zshenv"
{
    echo 'export DOTNET_ROOT="${HOME}/.dotnet"'
    echo 'export PATH="${PATH}:${DOTNET_ROOT}:${DOTNET_ROOT}/tools"'
} >> "${_zshenv}"
chown devuser:devuser "${_zshenv}"

# 5. PURGING THE GHOSTS (Rule 12.5)
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h:h}}"
source "${VDE_ROOT_DIR}/lib/vde-core" || { echo "CRITICAL: vde-core library missing" >&2; exit 1; }
vde_purge_ghosts
rm -f /tmp/dotnet-install.sh
