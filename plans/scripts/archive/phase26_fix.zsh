#!/usr/bin/env zsh
# This script applies the surgical edits for Phase 26 Error Engine and Network Isolation.
# It modifies bin/vde and lib/vde-errors.

set -e

VDE_ROOT="$HOME/VDE"

# 1. Edit bin/vde
# Change exit code from ${VDE_ERR_DOCKER:-5} to ${VDE_ERR_DOCKER:-8} in the start) case.
sed -i '' 's/vde_error_map ${VDE_ERR_DOCKER:-5} "network create"/vde_error_map ${VDE_ERR_DOCKER:-8} "network create"/' "${VDE_ROOT}/bin/vde"
sed -i '' 's/exit ${VDE_ERR_DOCKER:-5}/exit ${VDE_ERR_DOCKER:-8}/' "${VDE_ROOT}/bin/vde"

# Add --network "${net_name}" to docker run
sed -i '' '/--label "vde.managed=true" \\/a\
                    --network "${net_name}" \\\
' "${VDE_ROOT}/bin/vde"

# 2. Edit lib/vde-errors
# Align error mappings
sed -i '' 's/${VDE_ERR_TIMEOUT:-4})/${VDE_ERR_TIMEOUT:-5})/' "${VDE_ROOT}/lib/vde-errors"
sed -i '' 's/${VDE_ERR_EXISTS:-5})/${VDE_ERR_EXISTS:-6})/' "${VDE_ROOT}/lib/vde-errors"

echo "Edits applied successfully."
