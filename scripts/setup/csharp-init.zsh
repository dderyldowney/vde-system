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

# Load the core library first so the shared curl bounds and installer deadline are available.
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h:h}}"
source "${VDE_ROOT_DIR}/lib/vde-core" || { echo "CRITICAL: vde-core library missing" >&2; exit 1; }

# 3. DOTNET INSTALLATION (Shell-Safe Handshake)
typeset dev_home="/home/devuser"
mkdir -p "${dev_home}"

# Download installer
curl -fsSL "${VDE_CURL_BOUNDS[@]}" https://dot.net/v1/dotnet-install.sh -o /tmp/dotnet-install.sh
[[ -s /tmp/dotnet-install.sh ]] || { print -u2 "CRITICAL: dotnet-install.sh download failed or empty"; exit 1; }
chmod +x /tmp/dotnet-install.sh

# Mandate C exception (Signet #551): dotnet-install.sh is a Bash script (uses
# bashisms and relies on pipefail); Microsoft ships no zsh/native installer, and
# running it under sh triggers pipefail errors. Invoking it under bash is the
# unavoidable third-party path. (A direct SDK-tarball install was considered but
# kept on the vendor installer so channel 8.0 patch releases track automatically.)
# Listed in docs/governance/bash-exceptions.md.
# The installer does its own downloads that curl bounds cannot reach; timeout wraps the bash child so the deadline and SIGKILL apply to it, not just sudo (Signet #607).
sudo -H -u devuser timeout -k 30 "${VDE_INSTALLER_TIMEOUT}" bash /tmp/dotnet-install.sh --channel 8.0 --install-dir "${dev_home}/.dotnet"

# 4. PERSISTENCE ANCHOR
typeset _zshenv="${dev_home}/.zshenv"
{
    echo 'export DOTNET_ROOT="${HOME}/.dotnet"'
    echo 'export PATH="${PATH}:${DOTNET_ROOT}:${DOTNET_ROOT}/tools"'
} >> "${_zshenv}"
chown devuser:devuser "${_zshenv}"

# 5. PURGING THE GHOSTS (Rule 12.5)
vde_purge_ghosts
rm -f /tmp/dotnet-install.sh
