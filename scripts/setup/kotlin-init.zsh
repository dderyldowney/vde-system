#!/usr/bin/zsh
# VDE Kotlin/SDKMAN Beskar Forge - V4
# Forged for Din Deryl - This is the Way.

# 1. THE JAVA ALLOY: SDKMAN requires Java. Hammer it in first.
echo "Syncing with the Registry... (apt update)"
sudo apt-get update

echo "Fixing the Scavenger's Bug (missing man1 dir)..."
sudo mkdir -p /usr/share/man/man1

echo "Hammering in the Headless JDK and core tools..."
sudo apt-get install -y --no-install-recommends default-jdk-headless curl zip unzip vim

# 2. PURGING THE GHOSTS: Clean up apt artifacts immediately.
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*

# 3. SDKMAN INITIALIZATION
export SDKMAN_DIR="$HOME/.sdkman"
export sdkman_auto_answer=true

# Force clean start if directory is a ghost
if [[ -d "$SDKMAN_DIR" && ! -f "$SDKMAN_DIR/bin/sdkman-init.sh" ]]; then
    echo "Detected corrupted .sdkman directory. Purging for clean install..."
    rm -rf "$SDKMAN_DIR"
fi

# Install SDKMAN if missing
if [[ ! -d "$SDKMAN_DIR" ]]; then
    echo "Installing SDKMAN..."
    curl -s "https://get.sdkman.io?rcupdate=false" | zsh
fi

# 4. HYDRATION: Physically source the init script
INIT_SCRIPT="$SDKMAN_DIR/bin/sdkman-init.sh"
if [[ -f "$INIT_SCRIPT" ]]; then
    source "$INIT_SCRIPT"
    # Install Kotlin with null pipe to prevent hang
    echo "Installing Kotlin..."
    sdk install kotlin < /dev/null
else
    echo "ERROR: SDKMAN failed to populate. The Forge is cold."
    exit 1
fi

# 5. PATH ANCHORING
if [[ -d "$SDKMAN_DIR/candidates/kotlin/current" ]]; then
    KOTLIN_BIN="$SDKMAN_DIR/candidates/kotlin/current/bin"
    if ! grep -q "$KOTLIN_BIN" "$HOME/.zshenv"; then
        {
            echo "export SDKMAN_DIR=\"$SDKMAN_DIR\""
            echo "[[ -s \"$INIT_SCRIPT\" ]] && source \"$INIT_SCRIPT\""
            echo "export PATH=\"\$PATH:$KOTLIN_BIN\""
        } >> "$HOME/.zshenv"
    fi
fi

# 6. FINAL ARTIFACT PURGE: Delete all scripts EXCEPT this one to stop the sprawl
find /vde/scripts/setup/ -type f ! -name "kotlin-init.zsh" -delete
echo "Cleanup complete. Only the Kotlin Beskar remains in /vde/scripts/setup/."

