#!/usr/bin/env zsh
# Test script for shutdown performance

VDE_ROOT_DIR="${0:a:h:h}"
export VDE_ROOT_DIR

vm="vde-python"
compose_file="$VDE_ROOT_DIR/configs/docker/python/docker-compose.yml"

echo "Bringing up container for slow shutdown test..."
docker compose -f "$compose_file" -p vde-python up -d >/dev/null 2>&1
echo "Running standard 'docker compose down'..."
time docker compose -f "$compose_file" -p vde-python down -v >/dev/null 2>&1

echo "Bringing up container for fast shutdown test..."
docker compose -f "$compose_file" -p vde-python up -d >/dev/null 2>&1
echo "Running fast shutdown..."
time {
    docker kill --signal=TERM vde-python-vde-python-1 >/dev/null 2>&1 || true
    while true; do
        st=$(docker inspect -f '{{.State.Status}}' vde-python-vde-python-1 2>/dev/null || echo "removed")
        if [[ "$st" != "running" ]]; then
            break
        fi
        sleep 0.1
    done
    docker compose -f "$compose_file" -p vde-python down -v >/dev/null 2>&1 || true
}
