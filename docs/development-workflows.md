# Development Workflows

Example workflows for common development scenarios with VDE.

[← Back to README](../README.md)

---

## Example 1: Python API with PostgreSQL

A full-stack Python API with PostgreSQL database.

```bash
# 1. Create Python VM
./scripts/create-virtual-for python

# 2. Create PostgreSQL VM
./scripts/create-virtual-for postgres

# 3. Start both VMs
./scripts/start-virtual python postgres

# 4. Connect to Python VM
ssh python-dev

# 5. Set up project
cd ~/workspace
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn psycopg2-binary

# 6. Test database connection
ssh postgres
createdb testdb
exit

psql -h postgres -U devuser -d testdb

# 7. Run your API
uvicorn main:app --reload
```

---

## Example 2: Full-Stack JavaScript with Redis

Node.js/Express application with Redis caching.

```bash
# 1. Create VMs
./scripts/create-virtual-for js
./scripts/create-virtual-for redis

# 2. Start VMs
./scripts/start-virtual js redis

# 3. Connect to JS VM
ssh js-dev

# 4. Set up Express app
cd ~/workspace
npm init -y
npm install express redis

# 5. Create app
cat > app.js << 'EOF'
const express = require('express');
const redis = require('redis');
const app = express();

const client = redis.createClient({
  host: 'redis',
  port: 6379
});

app.get('/', (req, res) => {
  res.send('Hello from VDE!');
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
EOF

# 6. Run app
node app.js
```

---

## Example 3: Microservices with Multiple Languages

A microservices architecture using different languages for each service.

```bash
# 1. Create VMs for each service
./scripts/create-virtual-for python   # API Gateway
./scripts/create-virtual-for go       # Payment Service
./scripts/create-virtual-for rust     # Analytics Service
./scripts/create-virtual-for postgres # Database
./scripts/create-virtual-for redis    # Cache

# 2. Start all VMs
./scripts/start-virtual python go rust postgres redis

# 3. Each service runs in its own VM
# Python: ssh python-dev
# Go: ssh go-dev
# Rust: ssh rust-dev

# 4. Services communicate via Docker network
# python-dev can access: postgres, redis
# go-dev can access: postgres, redis
# etc.
```

---

## Daily Workflow

### Morning Setup

```bash
# Start your development environments
./scripts/start-virtual python postgres redis
```

### During Development

```bash
# Check what's running
./scripts/vde-ai "what's running?"

# Connect to your primary VM
ssh python-dev

# Work in the container
cd ~/workspace
# ... do work ...
```

### Evening Cleanup

```bash
# Stop everything to save resources
./scripts/shutdown-virtual all
```

---

## Troubleshooting Workflow

When something isn't working:

```bash
# 1. Check container status
docker ps

# 2. Check container logs
docker logs python-dev

# 3. Restart with rebuild
./scripts/start-virtual python --rebuild

# 4. Connect and debug
ssh python-dev
# ... investigate inside container ...
```

---

[← Back to README](../README.md)
