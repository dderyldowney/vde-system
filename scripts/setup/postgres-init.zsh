#!/usr/bin/env zsh
# @armor (Engine Core)
# VDE USP Hydration Ritual: postgres
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}

# Part of the Universal Script Parity (USP) mandate.
# Forged in Beskar
set -e

# 1. THE PACKAGE ALLOY
export DEBIAN_FRONTEND=noninteractive
typeset vde_postgres_pkgs="postgresql postgresql-contrib git docker.io"

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

# Securely pass password to postgres user for creation
echo "[POSTGRES-INIT] Ensuring 'devuser' exists with secure credentials..."
su - postgres -c "psql -tc \"SELECT 1 FROM pg_user WHERE usename = 'devuser'\" | grep -q 1" || \
su - postgres -c "psql -c \"CREATE USER devuser WITH PASSWORD '${POSTGRES_DEV_PASSWORD}' SUPERUSER;\""

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
typeset _spoke_ignition="/usr/local/bin/vde-spoke-ignition.zsh"
cat <<EOF > "${_spoke_ignition}"
#!/usr/bin/env zsh
# PostgreSQL Spoke Ignition
# Forged in Beskar

if ! pg_isready -h localhost >/dev/null 2>&1; then
    echo "[VDE-POSTGRES] Igniting PostgreSQL cluster..."
    sudo service postgresql start
fi
EOF
chmod +x "${_spoke_ignition}"

# 4. PERSISTENCE ANCHOR (Hardened Bridge)
typeset dev_home=$HOME
typeset _zshenv="${dev_home}/.zshenv"
mkdir -p "${dev_home}"
touch "${_zshenv}"
# Remove legacy startup if present
sed -i "/postgresql start/d" "${_zshenv}"
# Ensure bridge identity is available
grep -q "SSH_AUTH_SOCK" "${_zshenv}" || {
    echo "export SSH_AUTH_SOCK=${dev_home}/.ssh/vde/agent.sock" >> "${_zshenv}"
}
chown devuser:devuser "${_zshenv}"

# Stop service to maintain BTO state
service postgresql stop || true

# 5. PURGING THE GHOSTS (Rule 12.5)
export VDE_ROOT_DIR="${VDE_ROOT_DIR:-${0:a:h:h:h}}"
[[ -f "${VDE_ROOT_DIR}/lib/vde-core" ]] && source "${VDE_ROOT_DIR}/lib/vde-core"
vde_purge_ghosts
