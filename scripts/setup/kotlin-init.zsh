#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE USP Hydration Script: kotlin
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
typeset vde_kotlin_pkgs="curl git unzip zip"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_kotlin_pkgs} default-jdk

# 3. KOTLIN INSTALLATION (Hardened Home)
typeset dev_home="/home/devuser"
mkdir -p "${dev_home}"

if [[ ! -d "${dev_home}/.sdkman" ]]; then
    echo "[VDE-KOTLIN] Installing SDKMAN..."
    # Mandate C exception (Signet #551): SDKMAN is implemented in Bash — its
    # installer AND the sdkman-init.sh it generates are Bash scripts, and SDKMAN
    # requires Bash at runtime. There is no zsh/native install path, so piping
    # the vendor installer to bash is the unavoidable third-party path. (A direct
    # Kotlin-compiler download was considered but would drop SDKMAN's multi-SDK
    # version management.) Listed in docs/governance/bash-exceptions.md.
    # Downloaded to a file and verified first so an HTTP error cannot ship a
    # broken image with exit 0 (a curl|bash pipe would mask it).
    typeset _sdkman_installer=$(mktemp)
    curl -fsSL --connect-timeout 15 --max-time 120 "https://get.sdkman.io" -o "${_sdkman_installer}"
    [[ -s "${_sdkman_installer}" ]] || { echo "CRITICAL: SDKMAN installer download failed or empty" >&2; exit 1; }
    chmod 755 "${_sdkman_installer}"
    sudo -H -u devuser bash "${_sdkman_installer}"
    rm -f "${_sdkman_installer}"
fi

# 4. PERSISTENCE ANCHOR
typeset _zshenv="${dev_home}/.zshenv"
# Idempotent via a marker line: a re-run/re-smelt never appends a second block.
if ! grep -qsF '# VDE SDKMAN anchor' "${_zshenv}"; then
    {
        echo '# VDE SDKMAN anchor'
        echo 'export SDKMAN_DIR="${HOME}/.sdkman"'
        echo '[[ -s "${SDKMAN_DIR}/bin/sdkman-init.sh" ]] && source "${SDKMAN_DIR}/bin/sdkman-init.sh"'
    } >> "${_zshenv}"
fi

# Set ownership
chown -R devuser:devuser "${dev_home}"

# 5. PURGING THE GHOSTS (Rule 12.5)
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h:h}}"
source "${VDE_ROOT_DIR}/lib/vde-core" || { echo "CRITICAL: vde-core library missing" >&2; exit 1; }
vde_purge_ghosts
