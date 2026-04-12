#!/usr/bin/env zsh
#===============================================================================
# vde-spine-check.zsh - @system-spine Empirical Check Script
#
# Verifies the Unyielding Tetrad of VDE:
# Pillar I: Zsh 5.0+
# Pillar II: Git
# Pillar III: Docker
# Pillar IV: SSH (vde_student identity)
#
# Reference: VDE-SPEC v1.3.0
#===============================================================================

# Pillar I: Zsh
main() {
    if [[ -z "${ZSH_VERSION}" ]] || ! [[ "${ZSH_VERSION}" =~ "^5\." ]]; then
        echo "[CRITICAL] Pillar I (Zsh) failed: Zsh 5.0+ required." >&2
        return 1
    fi

    # Pillar II: Git
    if ! command -v git &>/dev/null; then
        echo "[CRITICAL] Pillar II (Git) failed: git not found." >&2
        return 1
    fi
    local git_test_dir=$(mktemp -d)
    (cd "${git_test_dir}" && git init --quiet --template='' && rm -rf .git) || { echo "[CRITICAL] Pillar II (Git) failed: git init failed."; return 1; }
    rmdir "${git_test_dir}"

    # Pillar III: Docker
    if ! docker info &>/dev/null; then
        echo "[CRITICAL] Pillar III (Docker) failed: Docker daemon not responsive." >&2
        return 1
    fi
    if ! docker run --rm alpine echo 'Forge Active' | grep -q 'Forge Active'; then
        echo "[CRITICAL] Pillar III (Docker) failed: Alpine diagnostic probe failed." >&2
        return 1
    fi

    # Pillar IV: SSH
    local ssh_identities=("${(f)$(ssh-add -l 2>/dev/null)}")
    if ! grep -q "vde_student" <<< "${ssh_identities}"; then
        # Attempt to add if missing
        local vde_key="${HOME}/.ssh/vde/vde_student"
        if [[ -f "${vde_key}" ]]; then
            ssh-add "${vde_key}" &>/dev/null || { echo "[CRITICAL] Pillar IV (SSH) failed: Failed to add vde_student identity."; return 1; }
        else
            echo "[CRITICAL] Pillar IV (SSH) failed: vde_student identity not found at ${vde_key}." >&2
            return 1
        fi
    fi

    echo "[SUCCESS] The Unyielding Tetrad is active. Sovereign Ecosystem stable."
    return 0
}

main "$@"
