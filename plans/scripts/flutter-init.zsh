#!/usr/bin/env zsh
# VDE Setup Script: flutter
# Version: 1.3.0
# Mandalorian Compliance: Local variables, ZSH only.

local _vde_alias="flutter"
echo "Initializing ${_vde_alias}..."

su devuser -c 'git clone --depth 1 https://github.com/flutter/flutter.git /home/devuser/flutter && export PATH="$PATH:/home/devuser/flutter/bin" && flutter precache'

exit 0