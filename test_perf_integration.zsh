#!/usr/bin/env zsh
source "/Users/dderyldowney/dev/tests/lib/test_common.zsh"
setup_test_env

start_time=$(date +%s%N)
generate_plan "start python" >/dev/null
end_time=$(date +%s%N)
elapsed=$((($end_time - $start_time) / 1000000))
echo "Time 1: ${elapsed}ms"
