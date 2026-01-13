#!/usr/bin/env bash
set -e

# -----------------------
# Parse flags
# -----------------------
REBUILD=false
NOCACHE=false

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

# -----------------------
# Shutdown all VMs
# -----------------------
echo "Shutting down all VMs..."
./scripts/shutdown-virtual.sh all

# -----------------------
# Start all VMs with optional rebuild
# -----------------------
start_service() {
    local svc="$1"
    local compose_file="./configs/docker/$svc/docker-compose.yml"

    # Rebuild if requested
    if [ "$REBUILD" = true ]; then
        echo "Building $svc VM..."
        BUILD_CMD="docker-compose -f $compose_file build"
        [ "$NOCACHE" = true ] && BUILD_CMD="$BUILD_CMD --no-cache"
        $BUILD_CMD
    fi

    # Start container
    echo "Starting $svc VM..."
    docker-compose -f "$compose_file" up -d
}

for svc in python rust js csharp ruby postgres redis mongodb; do
    start_service "$svc"
done

echo "All VMs are up!"

