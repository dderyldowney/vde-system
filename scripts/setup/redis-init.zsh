#!/usr/bin/env zsh
# VDE USP Hydration Ritual: redis
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_redis_pkgs="redis-server redis-tools"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_redis_pkgs}

# Stop the auto-started service to prepare for configuration
service redis-server stop || true
pkill redis-server || true

# 3. PERSISTENCE ANCHOR (ONLY FOR SERVICES: mysql, redis, mongodb, rabbitmq, couchdb, nginx, postgres)
# Append start command to devuser's .zshenv if not present
local _zshenv="/home/devuser/.zshenv"
if [[ "true" == "true" ]]; then
    # Configure Redis for container access
    local _conf="/etc/redis/redis.conf"
    if [[ -f "${_conf}" ]]; then
        sed -i "s/^bind .*/bind 0.0.0.0/" "${_conf}"
        sed -i "s/^protected-mode .*/protected-mode no/" "${_conf}"
        # Ensure it doesn't run as a daemon within the service manager if that's causing issues
        sed -i "s/^daemonize yes/daemonize no/" "${_conf}"
    fi

    # Ensure the service directory exists for PID file
    mkdir -p /run/redis
    chown redis:redis /run/redis

    # Start service to verify configuration during build
    # We use the init script directly to ensure it uses the config
    /usr/bin/redis-server /etc/redis/redis.conf --daemonize yes

    mkdir -p /home/devuser
    touch "${_zshenv}"
    # Use the config file explicitly in the startup command
    grep -q "redis-server /etc/redis/redis.conf" "${_zshenv}" || echo "sudo /usr/bin/redis-server /etc/redis/redis.conf --daemonize yes >/dev/null 2>&1" >> "${_zshenv}"
    chown devuser:devuser "${_zshenv}"
fi

# 4. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
