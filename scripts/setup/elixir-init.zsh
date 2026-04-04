#!/usr/bin/env zsh
#===============================================================================
# elixir-init.zsh - VDE Elixir Environment Initialization
#
# This script handles the asdf-based Elixir/Erlang source build.
# It is executed as root during the Docker build process.
#===============================================================================

# 1. Generate Locales
locale-gen en_US.UTF-8

# 2. Create the Installation Script for devuser
INSTALL_SCRIPT="/tmp/install-elixir-as-devuser.sh"

cat <<EOF > "${INSTALL_SCRIPT}"
#!/bin/bash
set -e

# Clone asdf if missing
if [ ! -d "\$HOME/.asdf" ]; then
    git clone https://github.com/asdf-vm/asdf.git "\$HOME/.asdf" --branch v0.14.0
fi

# Bootstrap asdf
source "\$HOME/.asdf/asdf.sh"

# Add plugins
asdf plugin add erlang || true
asdf plugin add elixir || true

# Install Erlang (this takes time)
asdf install erlang 26.2.1
asdf global erlang 26.2.1

# Install Elixir
asdf install elixir 1.16.0-otp-26
asdf global elixir 1.16.0-otp-26

# Persist environment
echo 'source \$HOME/.asdf/asdf.sh' >> "\$HOME/.zshenv"
echo 'export LANG=en_US.UTF-8' >> "\$HOME/.zshenv"
EOF

# 3. Execute as devuser
chmod +x "${INSTALL_SCRIPT}"
su - devuser -c "${INSTALL_SCRIPT}"

# 4. Cleanup
rm -f "${INSTALL_SCRIPT}"
