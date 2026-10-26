#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE USP Hydration Script: python (pyenv-managed; latest stable CPython at build)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
#
# Python is provided by pyenv (compiled from source), NOT the distro's apt
# python3. At image-build time we install the LATEST STABLE CPython available
# and set it as the global interpreter, so vde-python tracks upstream Python
# instead of being frozen at whatever the base image happens to ship.
set -e

export DEBIAN_FRONTEND=noninteractive
typeset DEVUSER="devuser"
typeset DEVHOME="/home/${DEVUSER}"

# 1. THE PACKAGE ALLOY — these are the PREREQUISITES pyenv needs to COMPILE
#    CPython from source, plus the VDE client tools. No distro python here;
#    pyenv owns the interpreter.
typeset -a vde_python_pkgs=(
    make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev
    libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev
    libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git
    libgdbm-dev libgdbm-compat-dev
    postgresql-client redis-tools docker.io
)

# 2. THE FORGE WORK — install the toolchain (hydration runs as root).
apt-get update
apt-get install -y ${vde_python_pkgs[@]}

# 3. INSTALL pyenv as devuser. The pyenv installer is third-party and runs under
#    bash (we only invoke it, exactly as upstream documents); it lands entirely
#    in ${DEVHOME}/.pyenv.
sudo -u "${DEVUSER}" bash -c 'curl -fsSL https://pyenv.run | bash'

# 4. WIRE pyenv INTO devuser's zsh login (the tribe speaks zsh — Mandate C).
#    Idempotent: only append if not already present. This is the zsh form of the
#    standard pyenv shell init.
typeset zrc="${DEVHOME}/.zshrc"
if ! grep -q 'PYENV_ROOT' "${zrc}" 2>/dev/null; then
    {
        echo ''
        echo '# pyenv (VDE python hydration)'
        echo 'export PYENV_ROOT="$HOME/.pyenv"'
        echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"'
        echo 'eval "$(pyenv init -)"'
    } >> "${zrc}"
    chown "${DEVUSER}:${DEVUSER}" "${zrc}" 2>/dev/null || true
fi

# 5. BUILD the LATEST STABLE CPython available at build time and set it GLOBAL,
#    as devuser. "Latest stable" = the highest pure X.Y.Z in pyenv's known list;
#    the regex drops pre-releases (rc/dev/a/b) and non-CPython variants (pypy,
#    graalpy, …), and `tail -1` takes the newest since the list is ascending.
sudo -u "${DEVUSER}" zsh -c '
    set -e
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    ver="$(pyenv install --list 2>/dev/null | tr -d " " | grep -E "^[0-9]+\.[0-9]+\.[0-9]+$" | tail -1)"
    if [[ -z "${ver}" ]]; then
        echo "CRITICAL: could not resolve a stable CPython from pyenv install --list" >&2
        exit 1
    fi
    echo "VDE: installing latest stable CPython ${ver} via pyenv (set as global)"
    pyenv install -s "${ver}"
    pyenv global "${ver}"
    pyenv rehash
    python --version
'

# 6. PURGING THE GHOSTS (Rule 12.5)
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h:h}}"
source "${VDE_ROOT_DIR}/lib/vde-core" || { echo "CRITICAL: vde-core library missing" >&2; exit 1; }
vde_purge_ghosts
