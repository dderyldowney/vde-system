#!/bin/bash
vm="vde-python"
compose_file="/Users/dderyldowney/dev/configs/docker/python/docker-compose.yml"

echo "Bringing up container for slow shutdown test..."
docker compose -f "$compose_file" -p vde-python up -d >/dev/null 2>&1
echo "Running standard 'docker compose down'..."
time docker compose -f "$compose_file" -p vde-python down -v >/dev/null 2>&1

echo "Bringing up container for fast shutdown test..."
docker compose -f "$compose_file" -p vde-python up -d >/dev/null 2>&1
echo "Running fast shutdown..."
time {
    # 1. Ask docker to kill with TERM
    docker kill --signal=TERM vde-python-vde-python-1 >/dev/null 2>&1 || true
    # 2. Wait for it to not be running by monitoring State.Status
    while true; do
        st=$(docker inspect -f '{{.State.Status}}' vde-python-vde-python-1 2>/dev/null || echo "removed")
        if [[ "$st" != "running" ]]; then
            break
        fi
        sleep 0.1
    done
    # 3. Clean up the compose network / volumes
    docker compose -f "$compose_file" -p vde-python down -v >/dev/null 2>&1 || true
}
