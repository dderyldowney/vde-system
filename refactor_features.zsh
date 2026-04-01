#!/bin/zsh
# Refactor script for VDE BDD features

FILES=$(find tests/features -name "*.feature")

for file in $FILES; do
  echo "Refactoring $file..."
  
  # Note: Order matters for some replacements (e.g., ./bin/vde before bin/vde)
  
  # Script to VDE command mappings
  sed -i '' 's/list-vms/vde list/g' "$file"
  sed -i '' 's/vde-health/vde health/g' "$file"
  sed -i '' 's/create-virtual-for/vde create/g' "$file"
  sed -i '' 's/start-virtual/vde start/g' "$file"
  sed -i '' 's/shutdown-virtual/vde stop/g' "$file"
  sed -i '' 's/ssh-vm/vde ssh/g' "$file"
  sed -i '' 's/vde-init/vde init/g' "$file"
  sed -i '' 's/add-vm-type/vde add/g' "$file"
  sed -i '' 's/uninstall-vm-type/vde uninstall/g' "$file"
  sed -i '' 's/vde-ps/vde ps/g' "$file"
  sed -i '' 's/vde-logs/vde logs/g' "$file"
  sed -i '' 's/vde-inspect/vde inspect/g' "$file"
  sed -i '' 's/vde-port/vde port/g' "$file"
  sed -i '' 's/vde-exec/vde exec/g' "$file"
  sed -i '' 's/vde-images/vde images/g' "$file"
  sed -i '' 's/vde-networks/vde networks/g' "$file"
  sed -i '' 's/vde-stats/vde stats/g' "$file"
  sed -i '' 's/vde-info/vde info/g' "$file"
  sed -i '' 's/cleanup-ports/vde cleanup-ports/g' "$file"
  sed -i '' 's/ssh-setup/vde ssh-setup/g' "$file"
  sed -i '' 's/ssh-sync/vde ssh-sync/g' "$file"
  sed -i '' 's/nuke-vde/vde nuke/g' "$file"
  
  # CLI path normalization
  sed -i '' 's|\./bin/vde|vde|g' "$file"
  sed -i '' 's|bin/vde|vde|g' "$file"
  
  # Fix double vde if any (e.g., vde vde list)
  sed -i '' 's/vde vde /vde /g' "$file"
done

echo "Done."
