#!/usr/bin/zsh
# VDE PostgreSQL Initialization Logic
service postgresql start

# Identify version dynamically
PG_VER=$(ls /etc/postgresql)

# Internal Database Setup
su - postgres -c "psql -c \"CREATE USER devuser WITH PASSWORD 'vde_pass';\""
su - postgres -c "createdb -O devuser devuser"

# Network and Authentication Hardening
echo "host all all 0.0.0.0/0 md5" >> "/etc/postgresql/$PG_VER/main/pg_hba.conf"
echo "listen_addresses='*'" >> "/etc/postgresql/$PG_VER/main/postgresql.conf"

# Persistence Restart
service postgresql restart
