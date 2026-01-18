#!/usr/bin/env zsh
# Backup SSH Setup for VDE Testing
# Backs up your personal SSH keys and config so we can test VDE's SSH automation

set -e

BACKUP_DIR="$HOME/.ssh-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "====================================="
echo "SSH Setup Backup"
echo "==================================="
echo ""
echo "Creating backup of your personal SSH setup..."
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup SSH keys
echo "Backing up SSH keys..."
key_count=0
for key in id_ed25519 id_rsa id_ecdsa id_dsa id_rsa.pub id_ecdsa.pub id_dsa.pub; do
    if [[ -f "$HOME/.ssh/$key" ]]; then
        cp "$HOME/.ssh/$key" "$BACKUP_DIR/$key"
        echo "  Backed up: $key"
        ((key_count++))
    fi
done

# Backup SSH config
if [[ -f "$HOME/.ssh/config" ]]; then
    cp "$HOME/.ssh/config" "$BACKUP_DIR/config"
    echo "  Backed up: config"
    ((key_count++))
fi

# Backup known_hosts
if [[ -f "$HOME/.ssh/known_hosts" ]]; then
    cp "$HOME/.ssh/known_hosts" "$BACKUP_DIR/known_hosts"
    echo "  Backed up: known_hosts"
    ((key_count++))
fi

# Create a README in the backup directory
cat > "$BACKUP_DIR/README.md" <<EOF
# SSH Setup Backup

This directory contains your personal SSH setup, backed up on $(date).

## Files in this backup:
- SSH keys (private and public)
- SSH config
- known_hosts

## To restore:
```bash
cd ~
rm -rf .ssh/
mv .ssh-backup/ .ssh/
```

## To delete backup:
```bash
rm -rf "$BACKUP_DIR"
```

---

**IMPORTANT:** This backup is for VDE testing only. When done testing, restore your setup.
EOF

echo ""
echo "====================================="
echo "Backup complete!"
echo "====================================="
echo ""
echo "Backed up $key_count items to: $BACKUP_DIR"
echo ""
echo "Your personal SSH setup is safely backed up."
echo ""
echo "To restore when done testing:"
echo "  rm -rf ~/.ssh/"
echo "  mv ~/.ssh-backup/ ~/.ssh/"
echo ""
echo "To delete backup:"
echo "  rm -rf "$BACKUP_DIR""

echo ""
echo "Now your personal SSH setup is safely backed up."
echo "We can test VDE's SSH automation safely!"
