#!/usr/bin/env zsh
# @armor (Spoke Hydration)
# VDE USP Hydration Ritual: couchdb
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_couchdb_pkgs="couchdb git docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_couchdb_pkgs}

# 3. SPOKE IGNITION REGISTRATION
local _spoke_ignition="/usr/local/bin/vde-spoke-ignition.zsh"
cat <<EOF > "${_spoke_ignition}"
#!/usr/bin/env zsh
# CouchDB Spoke Ignition
# Starts the database in the background on container start

if ! service couchdb status >/dev/null 2>&1; then
    echo "[VDE-COUCHDB] Forged in Beskar: Starting CouchDB..."
    sudo service couchdb start >/dev/null 2>&1
fi
EOF
chmod +x "${_spoke_ignition}"

# 4. PERSISTENCE ANCHOR (Hardened Bridge)
local dev_home=~devuser
local _zshenv="${dev_home}/.zshenv"
mkdir -p "${dev_home}"
touch "${_zshenv}"
# Remove legacy startup if present
sed -i "/couchdb start/d" "${_zshenv}"
# Ensure bridge identity is available
grep -q "SSH_AUTH_SOCK" "${_zshenv}" || {
    echo "export SSH_AUTH_SOCK=${dev_home}/.ssh/vde/agent.sock" >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"

# Stop service to maintain BTO state
service couchdb stop || true

# 5. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
