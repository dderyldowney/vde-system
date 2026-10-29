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

# 2b. VDE CORE (loaded before first bounded download; provides VDE_CURL_BOUNDS)
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h:h}}"
source "${VDE_ROOT_DIR}/lib/vde-core" || { echo "CRITICAL: vde-core library missing" >&2; exit 1; }

# 3. KOTLIN INSTALLATION (Hardened Home)
typeset dev_home="/home/devuser"
mkdir -p "${dev_home}"

if [[ ! -d "${dev_home}/.sdkman" ]]; then
    echo "[VDE-KOTLIN] Installing SDKMAN..."
    # Mandate C exception (Signet #551): SDKMAN is implemented in Bash — its
    # installer AND the sdkman-init.sh it generates are Bash scripts, and SDKMAN
    # requires Bash at runtime. There is no zsh/native install path, so piping
    # the vendor installer to bash is the unavoidable third-party path. (The
    # Kotlin compiler itself is installed as a SDKMAN candidate by direct
    # download below, so `sdk` still manages it.) Listed in docs/governance/bash-exceptions.md.
    # Downloaded to a file and verified first so an HTTP error cannot ship a
    # broken image with exit 0 (a curl|bash pipe would mask it).
    typeset _sdkman_installer=$(mktemp)
    curl -fsSL "${VDE_CURL_BOUNDS[@]}" "https://get.sdkman.io" -o "${_sdkman_installer}"
    [[ -s "${_sdkman_installer}" ]] || { echo "CRITICAL: SDKMAN installer download failed or empty" >&2; exit 1; }
    chmod 755 "${_sdkman_installer}"
    # SDKMAN installer does its own downloads that curl bounds cannot reach; timeout wraps the bash child so the deadline and SIGKILL apply to it, not just sudo (Signet #600)
    sudo -H -u devuser timeout -k 30 "${VDE_INSTALLER_TIMEOUT}" bash "${_sdkman_installer}"
    rm -f "${_sdkman_installer}"
fi

typeset _kt_dir="${dev_home}/.sdkman/candidates/kotlin"
if [[ ! -e "${_kt_dir}/current" ]]; then
    echo "[VDE-KOTLIN] Installing the Kotlin compiler from the release archive..."
    # Kotlin ships a plain release archive so no vendor installer or bash is needed (Mandate C).
    # It is laid out as an SDKMAN candidate so `sdk` still manages it (Signet #608).
    typeset _kt_tag
    _kt_tag=$(curl -fsSL "${VDE_CURL_BOUNDS[@]}" -o /dev/null -w '%{url_effective}' https://github.com/JetBrains/kotlin/releases/latest)
    typeset _kt_ver=${${_kt_tag:t}#v}
    [[ "${_kt_ver}" == <->.<->.<-> ]] || { echo "CRITICAL: could not resolve the Kotlin release (got '${_kt_tag}')" >&2; exit 1; }
    typeset _kt_url="https://github.com/JetBrains/kotlin/releases/download/v${_kt_ver}"
    typeset _kt_tmp=$(mktemp -d)
    curl -fsSL "${VDE_CURL_BOUNDS[@]}" -o "${_kt_tmp}/kotlin.zip" "${_kt_url}/kotlin-compiler-${_kt_ver}.zip"
    curl -fsSL "${VDE_CURL_BOUNDS[@]}" -o "${_kt_tmp}/kotlin.zip.sha256" "${_kt_url}/kotlin-compiler-${_kt_ver}.zip.sha256"
    [[ -s "${_kt_tmp}/kotlin.zip" ]] || { echo "CRITICAL: Kotlin compiler download failed or empty" >&2; exit 1; }
    [[ -s "${_kt_tmp}/kotlin.zip.sha256" ]] || { echo "CRITICAL: Kotlin compiler checksum download failed or empty" >&2; exit 1; }
    typeset _kt_want=$(<"${_kt_tmp}/kotlin.zip.sha256")
    _kt_want=${_kt_want%%[[:space:]]*}
    typeset _kt_got=$(sha256sum "${_kt_tmp}/kotlin.zip")
    _kt_got=${_kt_got%%[[:space:]]*}
    [[ "${_kt_got}" == "${_kt_want}" ]] || { echo "CRITICAL: Kotlin compiler sha256 mismatch" >&2; exit 1; }
    unzip -q "${_kt_tmp}/kotlin.zip" -d "${_kt_tmp}"
    mkdir -p "${_kt_dir}"
    rm -rf "${_kt_dir}/${_kt_ver}"
    mv "${_kt_tmp}/kotlinc" "${_kt_dir}/${_kt_ver}"
    ln -sfn "${_kt_ver}" "${_kt_dir}/current"
    rm -rf "${_kt_tmp}"
    echo "[VDE-KOTLIN] Kotlin ${_kt_ver} installed as SDKMAN candidate."
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
vde_purge_ghosts
