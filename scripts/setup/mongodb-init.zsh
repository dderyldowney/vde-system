#!/usr/bin/env zsh
# @armor (Spoke Hydration)
# VDE USP Hydration Ritual: mongodb
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_mongodb_pkgs="mongodb-org-shell mongodb git docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_mongodb_pkgs}

# 3. SPOKE IGNITION REGISTRATION
local _spoke_ignition="/usr/local/bin/vde-spoke-ignition.zsh"
cat <<EOF > "${_spoke_ignition}"
#!/usr/bin/env zsh
# MongoDB Spoke Ignition
# Starts the database in the background on container start

if ! service mongodb status >/dev/null 2>&1; then
    echo "[VDE-MONGODB] Forged in Beskar: Starting MongoDB..."
    sudo service mongodb start >/dev/null 2>&1
fi
EOF
chmod +x "${_spoke_ignition}"

# 4. PERSISTENCE ANCHOR (Hardened Bridge)
local dev_home=~devuser
local _zshenv="${dev_home}/.zshenv"
mkdir -p ${dev_home}
touch "${_zshenv}"
# Remove legacy startup if present
sed -i "/mongodb start/d" "${_zshenv}"
# Ensure bridge identity is available
grep -q "SSH_AUTH_SOCK" "${_zshenv}" || {
    echo "export SSH_AUTH_SOCK=${dev_home}/.ssh/vde/agent.sock" >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"

# Stop service to maintain BTO state
service mongodb stop || true

# 5. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
