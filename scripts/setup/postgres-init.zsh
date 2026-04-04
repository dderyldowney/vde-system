#!/usr/bin/zsh
# VDE PostgreSQL Initialization Logic (Anti-Entropy / USP)

# 1. Start the service
service postgresql start

# 2. Wait for PostgreSQL to be physically ready (The Circuit Breaker)
echo "Waiting for PostgreSQL to ignite..."
until pg_isready; do
  echo "Database not ready. Retrying in 1s..."
  sleep 1
done
echo "PostgreSQL is online and accepting connections."

# Identify version dynamically
PG_VER=$(ls /etc/postgresql | head -n 1)

# 3. Internal Database Setup
# Use -c to ensure commands are executed even if the shell environment differs
su - postgres -c "psql -c \"CREATE USER devuser WITH PASSWORD 'vde_pass';\""
su - postgres -c "createdb -O devuser devuser"

# 4. Network and Authentication Hardening
echo "host all all 0.0.0.0/0 md5" >> "/etc/postgresql/$PG_VER/main/pg_hba.conf"
echo "listen_addresses='*'" >> "/etc/postgresql/$PG_VER/main/postgresql.conf"

# 5. Persistence Restart
service postgresql restart
