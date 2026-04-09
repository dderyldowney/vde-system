#!/usr/bin/env zsh
# VDE USP Hydration Script: jupyterlab
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_jupyter_pkgs="python3-pip python3-venv"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_jupyter_pkgs}

# 3. Create a dedicated venv for Jupyter
local _venv_path="/home/devuser/.vde-venv"
sudo -u devuser python3 -m venv "${_venv_path}"

# 4. Install DS stack
sudo -u devuser "${_venv_path}/bin/pip" install --upgrade pip
sudo -u devuser "${_venv_path}/bin/pip" install \
    jupyterlab \
    matplotlib \
    scikit-learn \
    tensorflow \
    numpy \
    pandas

# 5. CONFIGURE JUPYTER
local _jupyter_config="/home/devuser/.jupyter/jupyter_lab_config.py"
sudo -u devuser mkdir -p /home/devuser/.jupyter
sudo -u devuser zsh -c "cat <<EOF > ${_jupyter_config}
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.token = ''
c.ServerApp.password = ''
c.ServerApp.root_dir = '/home/devuser/workspace'
EOF"

# 6. PERSISTENCE ANCHOR
local _zshenv="/home/devuser/.zshenv"
mkdir -p /home/devuser
touch "${_zshenv}"
grep -q "jupyter lab" "${_zshenv}" || {
    echo "nohup ${_venv_path}/bin/jupyter lab --config=${_jupyter_config} >/logs/jupyter.log 2>&1 &" >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"

# 7. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
