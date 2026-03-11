*** Begin Patch
*** Add File: lib/vde-root.sh
+#!/usr/bin/env zsh
+# Centralized VDE root resolution utility
+# Purpose: ensure VDE_ROOT_DIR is defined and points to the repository root.
+# This script is intended to be sourced by other VDE scripts.
+
+set -e
+
+## If VDE_ROOT_DIR is already set and valid, keep it as authoritative.
+if [[ -n "$VDE_ROOT_DIR" ]] && [[ -d "$VDE_ROOT_DIR" ]]; then
+  return 0
+fi
+
+## Attempt to infer root from the path of the invoking script.
+## ${(%):-%N} yields the path of the current script in zsh.
+SCRIPT_PATH="${(%):-%N}"
+ROOT_CANDIDATE="${SCRIPT_PATH:A:h:h}"
+
+if [[ -d "$ROOT_CANDIDATE" ]]; then
+  export VDE_ROOT_DIR="$ROOT_CANDIDATE"
+  return 0
+fi
+
+## Fallback: use the present working directory as root.
+export VDE_ROOT_DIR="${PWD}"
+
*** End Patch
