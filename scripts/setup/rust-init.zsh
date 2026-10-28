#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE USP Hydration Ritual: rust
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
#
# Release: Sovereign Baseline 1.5.1
# Objective: Hardened build-time hydration with Rust Mirror verification.

set -e

# 1. THE PACKAGE ALLOY
# Define system-level dependencies for Rust development and build-time hydration.
export DEBIAN_FRONTEND=noninteractive
typeset vde_rust_pkgs="build-essential curl git pkg-config libssl-dev ca-certificates docker.io"

# 2. THE FORGE WORK
# Perform the physical smelting of system packages.
apt-get update
apt-get install -y ${=vde_rust_pkgs}

# Rust-Specific Smelting: Install rustup via the Sovereign Mirror.
# This ensures the Spoke is "Born Ready" (BTO) at image creation.
# Mandate C (ZSH ONLY): run rustup's NATIVE installer binary directly instead
# of piping the vendor shell script to `sh`. The rustup-init binary does exactly
# what `sh.rustup.rs | sh` does, so no foreign shell is invoked (parity with the
# pyenv Spoke). TLS stays hardened.
sudo -H -u devuser zsh -c '
    set -e
    if ! command -v rustc >/dev/null; then
        case "$(uname -m)" in
            x86_64)        triple="x86_64-unknown-linux-gnu" ;;
            aarch64|arm64) triple="aarch64-unknown-linux-gnu" ;;
            armv7l)        triple="armv7-unknown-linux-gnueabihf" ;;
            i686|i386)     triple="i686-unknown-linux-gnu" ;;
            *) print -u2 "VDE-RUST: unsupported architecture $(uname -m)"; exit 1 ;;
        esac
        installer="$(mktemp)"
        curl --proto "=https" --tlsv1.2 -sSfL \
            "https://static.rust-lang.org/rustup/dist/${triple}/rustup-init" -o "${installer}"
        [[ -s "${installer}" ]] || { print -u2 "VDE-RUST: rustup-init download failed or empty"; exit 1; }
        chmod +x "${installer}"
        "${installer}" -y --no-modify-path
        rm -f "${installer}"
    fi
'

# 3. PERSISTENCE ANCHORS
# Direct injection as commanded by the Clan Leader.
# Ensures the cargo path is the UNIQUE and VERY LAST LINE of $HOME/.zshrc and $HOME/.zshenv.

sudo -H -u devuser zsh -c '
    # Ensure configuration files exist
    touch ~/.zshenv ~/.zshrc

    # Purge existing entries to ensure uniqueness
    sed -i "/\.cargo\/bin/d" ~/.zshenv
    sed -i "/\.cargo\/bin/d" ~/.zshrc

    # Append the mandated path export to the end of the files
    echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\"" >> ~/.zshenv
    echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\"" >> ~/.zshrc
'

# 3.5. COMPONENT HYDRATION
# Install rust-analyzer as devuser, with cargo/bin already on PATH from the
# persistence anchors above. Must run after .zshrc/.zshenv are written.
sudo -H -u devuser zsh -c '
    export PATH="$HOME/.cargo/bin:$PATH"
    rustup component add rust-analyzer
    rustup component add rust-src
'

# 4. PURGING THE GHOSTS (Rule 12.5)
# Clean up build artifacts to maintain a hardened, immutable baseline.
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h:h}}"
source "${VDE_ROOT_DIR}/lib/vde-core" || { echo "CRITICAL: vde-core library missing" >&2; exit 1; }
vde_purge_ghosts
