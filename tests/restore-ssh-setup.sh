#!/usr/bin/env zsh
# Restore SSH Setup after VDE Testing
# Restores your personal SSH keys and config from backup

set -e

echo "====================================="
echo "SSH Setup Restore"
echo "==================================="
echo ""
echo "This will restore your personal SSH setup from backup."
echo ""

# Find latest backup
BACKUP_DIR=$(ls -dt ~/.ssh-backup-* 2>/dev/null | head -1)

if [[ -z "$BACKUP_DIR" ]]; then
    echo "No SSH backup found."
    echo "Did you run ./tests/backup-ssh-setup.sh first?"
    echo ""
    echo "Available backups:"
    ls -d ~/.ssh-backup-* 2>/dev/null || echo "  None"
    exit 1
fi

echo "Found backup: $BACKUP_DIR"
echo ""
echo "This will:"
echo "  - Remove your current ~/.ssh/ directory"
echo "  - Restore from: $BACKUP_DIR"
echo ""
echo "⚠️  Make sure you're not currently using SSH for important tasks!"
echo ""
echo "Continue? (yes/no): "
read -r
if [[ ! "$REPLY" =~ ^[Yy] ]]; then
    echo "Cancelled"
    exit 0
fi

# Remove current .ssh directory
echo ""
echo "Removing current ~/.ssh/ directory..."
rm -rf ~/.ssh/
echo "✓ Removed"

# Restore from backup
echo "Restoring from backup..."
mv "$BACKUP_DIR" ~/.ssh/
echo "✓ Restored"

echo ""
echo "====================================="
echo "SSH Setup Restored"
echo "==================================="
echo ""
echo "Your personal SSH setup has been restored!"
echo "You're back to using your personal SSH keys."
