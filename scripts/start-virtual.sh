#!/usr/bin/env bash
set -e

SERVICE="$1"
shift

REBUILD=false
NOCACHE=false

# Parse flags
for arg in "$@"; do
    case $arg in
        --rebuild)
            REBUILD=true
            ;;
        --no-cache)
            NOCACHE=true
            ;;
        *)
            echo "Unknown option $arg"
            exit 1
            ;;
    esac
done

start_service() {
    local svc="$1"
    echo "Starting $svc VM..."

    BUILD_OPTS=""
    if [ "$REBUILD" = true ]; then
        BUILD_OPTS="--build"
        [ "$NOCACHE" = true ] && BUILD_OPTS="$BUILD_OPTS --no-cache"
    fi

    COMPOSE_FILE="./configs/docker/$svc/docker-compose.yml"

    docker-compose -f "$COMPOSE_FILE" up -d $BUILD_OPTS
}

if [ "$SERVICE" = "all" ]; then
    for svc in python rust js csharp ruby postgres redis mongodb nginx; do
        start_service "$svc"
    done
else
    start_service "$SERVICE"
fi

