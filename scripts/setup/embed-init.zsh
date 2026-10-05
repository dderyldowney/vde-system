#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE USP Hydration Ritual: embed
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
#
# Signet #533. Objective: one Spoke carrying the embedded toolchain family for
# Python, C, C++ and Rust, so a Foundling flashing an ESP32, writing firmware
# against arm-none-eabi-gcc and driving a harness in Rust needs one Spoke
# rather than three with disjoint tools.
#
# Born Ready (BTO): every toolchain is baked here, at image build time. No
# runtime apt, no runtime downloads.

set -e

# A piped installer's exit status is the reader's, not curl's: if curl -f hits a
# 404, the shell reads empty stdin and exits 0, shipping an image without the
# tool while the build reports success. pipe_fail propagates curl's failure.
setopt pipe_fail

# 1. THE PACKAGE ALLOY
# Every package below was verified present in Debian 12 bookworm before this
# ritual was written. esptool is deliberately absent: it is not packaged for
# bookworm and Debian 12 enforces PEP 668, so it arrives via pipx in step 4.
export DEBIAN_FRONTEND=noninteractive
typeset vde_embed_pkgs="build-essential cmake pkg-config git curl ca-certificates libssl-dev \
gcc-arm-none-eabi binutils-arm-none-eabi libnewlib-arm-none-eabi \
gdb-multiarch openocd stlink-tools dfu-util avrdude \
clang lld llvm llvm-dev clangd lldb clang-tidy clang-format clang-tools libclang-dev \
libc++-dev libc++abi-dev \
g++ gcc-multilib \
libusb-1.0-0-dev libudev-dev \
python3 python3-pip python3-venv pipx python3-serial python3-usb \
picocom minicom screen \
docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_embed_pkgs}

# 3. THE RUST ALLOY
# Installed via rustup as the rust Spoke does, then given the bare-metal
# targets. thumbv7em-none-eabihf is the STM32F303 (Cortex-M4F); the others
# cover Cortex-M3, Cortex-M0 and the RISC-V ESP32-C3.
sudo -u devuser zsh -c '
    set -e
    if ! command -v rustc >/dev/null; then
        _installer=$(mktemp)
        curl --proto "=https" --tlsv1.2 -sSfL https://sh.rustup.rs -o "${_installer}"
        [[ -s "${_installer}" ]] || { print -u2 "rustup installer download failed or empty"; exit 1; }
        sh "${_installer}" -y --no-modify-path
        rm -f "${_installer}"
    fi
'

# PERSISTENCE ANCHORS: cargo on PATH for login and non-login shells, exactly
# once, as the rust Spoke mandates.
sudo -u devuser zsh -c '
    set -e
    touch ~/.zshenv ~/.zshrc
    sed -i "/\.cargo\/bin/d" ~/.zshenv
    sed -i "/\.cargo\/bin/d" ~/.zshrc
    echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\"" >> ~/.zshenv
    echo "export PATH=\"\$HOME/.cargo/bin:\$PATH\"" >> ~/.zshrc
'

sudo -u devuser zsh -c '
    set -e
    export PATH="$HOME/.cargo/bin:$PATH"
    rustup component add rust-analyzer rust-src
    rustup target add thumbv7em-none-eabihf
    rustup target add thumbv7m-none-eabi
    rustup target add thumbv6m-none-eabi
    rustup target add riscv32imc-unknown-none-elf
    # The Rust side of the LLVM suite: llvm-tools ships llvm-objcopy and
    # friends inside the toolchain, and cargo-binutils exposes them as
    # "cargo size", "cargo objdump", "cargo nm" for firmware inspection and
    # for producing .bin/.hex images from an ELF.
    rustup component add llvm-tools
    cargo install cargo-binutils
'

# 4. THE PYTHON ALLOY
# pipx gives esptool an isolated venv, which satisfies PEP 668 without
# --break-system-packages and keeps it off the system interpreter.
# pyserial arrives as python3-serial above, so it is importable system-wide.
sudo -u devuser zsh -c '
    set -e
    export PATH="$HOME/.local/bin:$PATH"
    pipx install esptool
'

sudo -u devuser zsh -c '
    set -e
    touch ~/.zshenv ~/.zshrc
    sed -i "/\.local\/bin/d" ~/.zshenv
    sed -i "/\.local\/bin/d" ~/.zshrc
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.zshenv
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.zshrc
'

# 5. THE PROBE ALLOY
# probe-rs from its official prebuilt release: the same binary the project
# ships, without a 15-minute source build. Still build-time, so Born Ready
# holds. probe-rs needs libusb and libudev, installed in step 1.
sudo -u devuser zsh -c '
    set -e
    export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
    if ! command -v probe-rs >/dev/null; then
        _installer=$(mktemp)
        curl --proto "=https" --tlsv1.2 -sSfL \
            https://github.com/probe-rs/probe-rs/releases/latest/download/probe-rs-tools-installer.sh \
            -o "${_installer}"
        [[ -s "${_installer}" ]] || { print -u2 "probe-rs installer download failed or empty"; exit 1; }
        sh "${_installer}"
        rm -f "${_installer}"
        command -v probe-rs >/dev/null || { print -u2 "probe-rs did not install"; exit 1; }
    fi
'

# 6. PURGING THE GHOSTS (Rule 12.5)
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h:h}}"
source "${VDE_ROOT_DIR}/lib/vde-core" || { echo "CRITICAL: vde-core library missing" >&2; exit 1; }
vde_purge_ghosts
