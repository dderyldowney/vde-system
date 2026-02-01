#!/bin/zsh
CONFIGS_DIR=configs/docker

get_allocated_ports() {
    local range_start=$1
    local range_end=$2
    local ports=""

    for compose_dir in "$CONFIGS_DIR"/*/; do
        [ -d "$compose_dir" ] || continue
        compose_file="$compose_dir/docker-compose.yml"
        if [ -f "$compose_file" ]; then
            local line
            while IFS= read -r line; do
                case "$line" in
                    *[0-9]*:22*)
                        local port
                        port=$(echo "$line" | sed 's/.*"\([0-9]*\):22".*/\1/')
                        if [ -n "$port" ] && [ "$port" != "$line" ]; then
                            if [ "$port" -ge "$range_start" ] && [ "$port" -le "$range_end" ]; then
                                ports="$ports $port"
                            fi
                        fi
                        ;;
                esac
            done < "$compose_file"
        fi
    done

    echo "$ports" | tr ' ' '\n' | grep -v '^$' | sort -n | uniq
}

echo "Testing range 9900-9905:"
get_allocated_ports 9900 9905
echo "---"
echo "Testing range 2200-2299:"
get_allocated_ports 2200 2299
