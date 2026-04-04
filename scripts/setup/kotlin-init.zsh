#!/usr/bin/env zsh
# VDE Kotlin/SDKMAN Absolute Zero Anchor (Final Hardened Logic)
set -e

# 1. Clean and Setup Directories as Root
export SDKMAN_DIR="/home/devuser/.sdkman"
rm -rf "$SDKMAN_DIR"
mkdir -p "$SDKMAN_DIR/src"
chown -R devuser:devuser "$SDKMAN_DIR"

# 2. Complete Installation as devuser in ONE SHOT
# This prevents the "SDKMAN found" error and ensures bin/ exists.
su - devuser -c "
    set -e
    export SDKMAN_DIR=\"\$HOME/.sdkman\"
    curl -s 'https://get.sdkman.io?rcupdate=false' | bash
    # Force find the init script (installer sometimes puts it in tmp/)
    INIT_SCRIPT=\$(find \"\$SDKMAN_DIR\" -name \"sdkman-init.sh\" | head -n 1)
    source \"\$INIT_SCRIPT\"
    sdk install kotlin < /dev/null
    
    # Anchor persistence immediately
    ZSHENV=\"\$HOME/.zshenv\"
    echo 'export SDKMAN_DIR=\"\$HOME/.sdkman\"' >> \"\$ZSHENV\"
    echo \"[[ -s \\\"\$INIT_SCRIPT\\\" ]] && source \\\"\$INIT_SCRIPT\\\"\" >> \"\$ZSHENV\"
"
