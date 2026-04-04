#!/usr/bin/zsh
# VDE Kotlin/SDKMAN Absolute Zero Anchor
export SDKMAN_DIR="/home/devuser/.sdkman"
export sdkman_auto_answer=true
export sdkman_auto_selfupdate=false

# 1. Force fresh install if init script is missing
if [[ ! -f "$SDKMAN_DIR/bin/sdkman-init.sh" ]]; then
    echo "SDKMAN missing or broken. Reinstalling..."
    rm -rf "$SDKMAN_DIR"
    mkdir -p "$SDKMAN_DIR/src"
    su - devuser -c "curl -s 'https://get.sdkman.io?rcupdate=false' | bash"
fi

# 2. THE MATERIAL TRUTH: Dynamic Path Resolution
INIT_SCRIPT=$(find "$SDKMAN_DIR" -name "sdkman-init.sh" | head -n 1)

if [[ -n "$INIT_SCRIPT" && -f "$INIT_SCRIPT" ]]; then
    echo "Found init script at: $INIT_SCRIPT"
    # 3. Non-interactive Install as devuser
    su - devuser -c "source $INIT_SCRIPT && sdk install kotlin < /dev/null"
else
    echo "ERROR: SDKMAN initialization script not found in $SDKMAN_DIR"
    exit 1
fi

# 4. PERSISTENCE
CANONICAL_INIT="$SDKMAN_DIR/bin/sdkman-init.sh"
if ! grep -q "sdkman-init.sh" "/home/devuser/.zshenv" 2>/dev/null; then
    {
        echo "export SDKMAN_DIR=\"/home/devuser/.sdkman\""
        echo "[[ -s \"$CANONICAL_INIT\" ]] && source \"$CANONICAL_INIT\""
    } >> "/home/devuser/.zshenv"
fi
chown devuser:devuser "/home/devuser/.zshenv"
