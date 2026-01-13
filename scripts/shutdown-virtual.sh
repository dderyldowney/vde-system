#!/usr/bin/env bash
set -e

SERVICE="$1"

shutdown_service() {
    local svc="$1"
    echo "Shutting down $svc VM..."
    COMPOSE_FILE="./configs/docker/$svc/docker-compose.yml"
    docker-compose -f "$COMPOSE_FILE" down
}

if [ "$SERVICE" = "all" ]; then
    for svc in python rust js csharp ruby postgres redis mongodb; do
        shutdown_service "$svc"
    done
else
    shutdown_service "$SERVICE"
fi

