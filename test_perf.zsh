source ./lib/vm-common
source ./lib/vde-parser
# build alias map once
_build_alias_map
start_time=$(date +%s%N)
for i in {1..100}; do
    generate_plan "start python" >/dev/null 2>&1
done
end_time=$(date +%s%N)
elapsed=$((($end_time - $start_time) / 1000000))
echo "Time: ${elapsed}ms"
