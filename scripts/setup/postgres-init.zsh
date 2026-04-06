#!/usr/bin/env zsh
# VDE USP Hydration Ritual: postgres
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_postgres_pkgs="postgresql postgresql-contrib"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_postgres_pkgs}

# Start Service for setup
service postgresql start || true

# Dynamic Path Resolution
PG_VER=$(ls /etc/postgresql | head -n 1)
PG_BASE="/etc/postgresql/${PG_VER}/main"

# User & DB Creation (Idempotent)
su - postgres -c "psql -tc \"SELECT 1 FROM pg_user WHERE usename = 'devuser'\" | grep -q 1" || \
su - postgres -c "psql -c \"CREATE USER devuser WITH PASSWORD 'vde_pass' SUPERUSER;\""

su - postgres -c "psql -lqt | cut -d \| -f 1 | grep -qw devuser" || \
su - postgres -c "createdb -O devuser devuser"

# Configuration Hardening
grep -q "0.0.0.0/0" "${PG_BASE}/pg_hba.conf" || \
echo "host all all 0.0.0.0/0 md5" >> "${PG_BASE}/pg_hba.conf"
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "${PG_BASE}/postgresql.conf"

# Final Reset & Verification
service postgresql restart
pg_isready -h localhost

# 3. PERSISTENCE ANCHOR
local _zshenv="/home/devuser/.zshenv"
mkdir -p /home/devuser
touch "${_zshenv}"
grep -q "postgresql start" "${_zshenv}" || {
    echo "sudo service postgresql start >/dev/null 2>&1" >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"

# 4. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
