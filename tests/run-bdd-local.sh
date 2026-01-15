#!/usr/bin/env zsh
# Run BDD tests locally with Docker socket access
# Mirrors the GitHub Actions setup in .github/workflows/vde-ci.yml

set -e

VDE_ROOT_DIR="${VDE_ROOT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
export VDE_ROOT_DIR

echo "VDE Root Directory: $VDE_ROOT_DIR"
cd "$VDE_ROOT_DIR"

# Create VDE directories if they don't exist
echo "Creating VDE directories..."
mkdir -p projects/{python,rust,js,csharp,ruby,go,java}
mkdir -p data/{postgres,mongodb,redis}
mkdir -p logs/nginx
mkdir -p public-ssh-keys
mkdir -p .cache .locks

# Generate test SSH key if it doesn't exist
if [[ ! -f public-ssh-keys/test_id_ed25519 ]]; then
    echo "Generating test SSH key..."
    ssh-keygen -t ed25519 -f public-ssh-keys/test_id_ed25519 -N "" -C "bdd-test@vde"
    cp public-ssh-keys/test_id_ed25519.pub public-ssh-keys/id_ed25519.pub
fi

# Create Docker network
echo "Creating Docker network..."
docker network create dev-net 2>/dev/null || echo "Network already exists"

# Build BDD test container
echo "Building BDD test container..."
docker build -t vde-bdd-tester -f tests/docker/bdd-test/Dockerfile .

# Run BDD tests with Docker socket access
echo "Running BDD feature tests with Docker socket access..."
docker run --rm \
    -v "$VDE_ROOT_DIR:/vde" \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v "$VDE_ROOT_DIR/projects:/vde/projects" \
    -v "$VDE_ROOT_DIR/data:/vde/data" \
    -v "$VDE_ROOT_DIR/logs:/vde/logs" \
    -v "$VDE_ROOT_DIR/public-ssh-keys:/vde/public-ssh-keys" \
    -e VDE_ROOT_DIR=/vde \
    -e PYTHONUNBUFFERED=1 \
    --network host \
    vde-bdd-tester \
    behave "$@" tests/features/

# Cleanup
echo ""
echo "Cleaning up test containers..."
docker ps -aq --filter "name=python-dev" --filter "name=rust-dev" --filter "name=js-dev" | xargs -r docker stop 2>/dev/null || true
docker ps -aq --filter "name=python-dev" --filter "name=rust-dev" --filter "name=js-dev" | xargs -r docker rm 2>/dev/null || true
