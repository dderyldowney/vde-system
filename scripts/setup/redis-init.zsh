#!/usr/bin/env zsh
# VDE USP Hydration Ritual: redis
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_redis_pkgs="redis-server redis-tools git docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_redis_pkgs}

# Stop the auto-started service to prepare for configuration
service redis-server stop || true
pkill redis-server || true

# Configure Redis for inter-VM communication
sed -i 's/^bind .*/bind 0.0.0.0/' /etc/redis/redis.conf
sed -i 's/^protected-mode yes/protected-mode no/' /etc/redis/redis.conf

# 3. SPOKE IGNITION REGISTRATION
local _spoke_ignition="/usr/local/bin/vde-spoke-ignition.zsh"
cat <<EOF > "${_spoke_ignition}"
#!/usr/bin/env zsh
# Redis Spoke Ignition
# Starts the server in the background on container start

if ! pgrep -f "redis-server" >/dev/null; then
    echo "[VDE-REDIS] Forged in Beskar: Starting Redis..."
    sudo /usr/bin/redis-server /etc/redis/redis.conf --daemonize yes >/dev/null 2>&1
fi
EOF
chmod +x "${_spoke_ignition}"

# 4. PERSISTENCE ANCHOR (Hardened Bridge)
local _zshenv="/home/devuser/.zshenv"
mkdir -p /home/devuser
touch "${_zshenv}"
# Remove legacy startup if present
sed -i "/redis-server/d" "${_zshenv}"
# Ensure bridge identity is available
grep -q "SSH_AUTH_SOCK" "${_zshenv}" || {
    echo "export SSH_AUTH_SOCK=/home/devuser/.ssh/vde/agent.sock" >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"

# Stop service to maintain BTO state
service redis-server stop || true
pkill redis-server || true

# 5. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
