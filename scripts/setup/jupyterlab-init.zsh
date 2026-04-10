#!/usr/bin/env zsh
# VDE USP Hydration Script: jupyterlab
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_jupyter_pkgs="python3-pip python3-venv tini git docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_jupyter_pkgs}

# 3. Create a dedicated venv for Jupyter
local _venv_path="/home/devuser/.vde-venv"
sudo -u devuser python3 -m venv "${_venv_path}"

# 4. Install DS stack (Jupyter Server is the modern backend)
sudo -u devuser "${_venv_path}/bin/pip" install --upgrade pip
sudo -u devuser "${_venv_path}/bin/pip" install \
    jupyterlab \
    jupyter-server \
    matplotlib \
    scikit-learn \
    tensorflow \
    numpy \
    pandas

# 5. CONFIGURE JUPYTER SERVER (Modern Pattern)
local _jupyter_config="/home/devuser/.jupyter/jupyter_server_config.py"
sudo -u devuser mkdir -p /home/devuser/.jupyter
sudo -u devuser zsh -c "cat <<EOF > ${_jupyter_config}
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.root_dir = '/home/devuser/workspace'
# Security: Token will be loaded from environment variable JUPYTER_TOKEN
EOF"

# 6. PERSISTENCE ANCHOR (Hardened Background Pattern)
local _zshenv="/home/devuser/.zshenv"
mkdir -p /home/devuser
touch "${_zshenv}"
# Guarded start to prevent process leaks during SSH sessions
grep -q "jupyter-server" "${_zshenv}" || {
    echo "if ! pgrep -f \"jupyter-server\" >/dev/null; then" >> "${_zshenv}"
    echo "    nohup tini -g -- ${_venv_path}/bin/jupyter lab --config=${_jupyter_config} >/logs/jupyter.log 2>&1 &" >> "${_zshenv}"
    echo "fi" >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"

# 7. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
