#!/usr/bin/env zsh
echo "Testing substitution..."
_path="${(%):-%N}"
echo "Path: $_path"
