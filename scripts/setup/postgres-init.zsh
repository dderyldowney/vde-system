#!/usr/bin/env zsh
# VDE USP Hydration Ritual: postgres
# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
local vde_postgres_pkgs="postgresql postgresql-contrib git docker.io"

# 2. THE FORGE WORK
apt-get update
apt-get install -y ${=vde_postgres_pkgs}

# Start Service for setup
service postgresql start || true

# Dynamic Path Resolution
PG_VER=$(ls /etc/postgresql | head -n 1)
PG_BASE="/etc/postgresql/${PG_VER}/main"

# User & DB Creation (Idempotent)
if [[ -z "${POSTGRES_DEV_PASSWORD}" ]]; then
    echo -e "${RED}[ERROR] Rule 12 Violation: POSTGRES_DEV_PASSWORD is not set.${RESET}"
    echo -e "  The Forge requires a password to be provided via the environment for Spoke ignition."
    exit 1
fi
local pg_dev_pass="${POSTGRES_DEV_PASSWORD}"
su - postgres -c "psql -tc \"SELECT 1 FROM pg_user WHERE usename = 'devuser'\" | grep -q 1" || \
su - postgres -c "psql <<EOF
CREATE USER devuser WITH PASSWORD '${pg_dev_pass}' SUPERUSER;
EOF
"

su - postgres -c "psql -lqt | cut -d \| -f 1 | grep -qw devuser" || \
su - postgres -c "createdb -O devuser devuser"

# Configuration Hardening
grep -q "0.0.0.0/0" "${PG_BASE}/pg_hba.conf" || \
echo "host all all 0.0.0.0/0 md5" >> "${PG_BASE}/pg_hba.conf"
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "${PG_BASE}/postgresql.conf"

# Final Reset & Verification
service postgresql restart
pg_isready -h localhost

# 3. SPOKE IGNITION REGISTRATION
local _spoke_ignition="/usr/local/bin/vde-spoke-ignition.zsh"
cat <<EOF > "${_spoke_ignition}"
#!/usr/bin/env zsh
# PostgreSQL Spoke Ignition
# Starts the database in the background on container start

if ! pg_isready -h localhost >/dev/null 2>&1; then
    echo "[VDE-POSTGRES] Forged in Beskar: Starting PostgreSQL..."
    sudo service postgresql start >/dev/null 2>&1
fi
EOF
chmod +x "${_spoke_ignition}"

# 4. PERSISTENCE ANCHOR (Hardened Bridge)
local _zshenv="/home/devuser/.zshenv"
mkdir -p /home/devuser
touch "${_zshenv}"
# Remove legacy startup if present
sed -i "/postgresql start/d" "${_zshenv}"
# Ensure bridge identity is available
grep -q "SSH_AUTH_SOCK" "${_zshenv}" || {
    echo "export SSH_AUTH_SOCK=/home/devuser/.ssh/vde/agent.sock" >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"

# Stop service to maintain BTO state
service postgresql stop || true

# 5. PURGING THE GHOSTS
apt-get clean
rm -rf /var/lib/apt/lists/*
