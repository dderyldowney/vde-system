#!/usr/bin/env zsh
# @shared-law (Forge Component)
echo "Testing substitution..."
_path="${(%):-%N}"
echo "Path: $_path"
