#!/usr/bin/env zsh
# VDE PostgreSQL Initialization (Hardened)
# Part of the Universal Script Parity (USP) mandate.
set -e

# 1. Install packages
apt-get update
apt-get install -y postgresql postgresql-contrib
apt-get clean
rm -rf /var/lib/apt/lists/*

# 2. Start Service
service postgresql start || true

# 3. Dynamic Path Resolution
PG_VER=$(ls /etc/postgresql | head -n 1)
PG_BASE="/etc/postgresql/${PG_VER}/main"

echo "Detected PostgreSQL ${PG_VER} at ${PG_BASE}"

# 4. User & DB Creation (Idempotent)
su - postgres -c "psql -tc \"SELECT 1 FROM pg_user WHERE usename = 'devuser'\" | grep -q 1" || \
su - postgres -c "psql -c \"CREATE USER devuser WITH PASSWORD 'vde_pass' SUPERUSER;\""

su - postgres -c "psql -lqt | cut -d \| -f 1 | grep -qw devuser" || \
su - postgres -c "createdb -O devuser devuser"

# 5. Configuration Hardening
grep -q "0.0.0.0/0" "${PG_BASE}/pg_hba.conf" || \
echo "host all all 0.0.0.0/0 md5" >> "${PG_BASE}/pg_hba.conf"

sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "${PG_BASE}/postgresql.conf"

# 6. Final Reset & Verification
service postgresql restart
pg_isready -h localhost

# 7. Persistence Anchor (Ensure service starts on entry)
ZSHENV="/home/devuser/.zshenv"
grep -q "postgresql start" "$ZSHENV" 2>/dev/null || {
    echo "sudo service postgresql start >/dev/null 2>&1" >> "$ZSHENV"
}
chown devuser:devuser "$ZSHENV"
