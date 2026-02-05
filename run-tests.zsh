#!/usr/bin/env zsh
# run-tests.zsh - Run VDE tests with automatic Docker detection

# Check if Docker is available
if docker info >/dev/null 2>&1; then
    DOCKER_AVAILABLE=true
else
    DOCKER_AVAILABLE=false
fi

echo "Docker available: $DOCKER_AVAILABLE"

if [ "$DOCKER_AVAILABLE" = "true" ]; then
    echo "Running all tests..."
    behave tests/features/ --tags=-@wip
else
    echo "Docker not available - running docker-free tests only..."
    behave tests/features/docker-free/
fi
