#!/usr/bin/env zsh
# Nginx Initialization Script (USP Compliant)
# Part of the Universal Script Parity (USP) mandate.

vde_log_info "Initializing Nginx service VM..." "setup"

# 1. Install packages
apt-get update
apt-get install -y nginx-extras

# 2. Cleanup
apt-get clean
rm -rf /var/lib/apt/lists/*

vde_log_success "Nginx initialization complete." "setup"
