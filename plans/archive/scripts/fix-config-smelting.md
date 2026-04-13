# Implementation Plan: Pure ZSH Configuration Management (The Scavenger's Ban)

## Objective
Eliminate dependency on `jq` for core VM configuration tasks (smelting and loading) by using pure ZSH string manipulation. This ensures high performance and 100% portability even on systems without `jq` or Docker, adhering to Rule G.

## Key Files & Context
- `lib/vde-core`: Contains `vde_translate_conf_to_json`.
- `lib/vm-common`: Contains `load_vm_types`.
- `data/vm-types.conf`: The Raw Beskar (pipe-delimited source of truth).
- `data/vm-types.json`: The Pure Beskar (JSON artifact for validation/external tools).

## Implementation Steps

### 1. Refactor `vde_translate_conf_to_json` in `lib/vde-core`
- Implement pure ZSH conversion from `.conf` to `.json`.
- Use an internal JSON escaping helper for safety.
- Eliminate the `vde_query_json` (JQ) call inside the `while` loop.

### 2. Refactor `load_vm_types` in `lib/vm-common`
- Add a pure ZSH parser for the `.conf` file as the primary fallback if `jq` is missing or the cache is invalid.
- Ensure that even if `jq` is missing, we can load all VM properties (aliases, display, pkgs, ports) from the Raw Beskar.

## Proposed Code Changes

### lib/vde-core: `vde_translate_conf_to_json`
```zsh
vde_translate_conf_to_json() {
    local conf_file="$1"
    local json_file="$2"
    
    local lang_entries=()
    local svc_entries=()
    
    # Helper to escape JSON strings (The Scavenger's Escaper)
    _vde_escape_json() {
        local str="$1"
        str="${str//\\/\\\\}" # Backslashes
        str="${str//\"/\\\"}" # Quotes
        str="${str//$'\n'/\\n}" # Newlines
        echo -n "$str"
    }

    while IFS='|' read -r _v_type _v_name _v_aliases _v_disp _v_pkgs _v_cmd _v_env _v_port _extra; do
        [[ -z "${_v_name}" || "${_v_type}" == "#"* ]] && continue
        
        local category="language"
        [[ "${_v_type}" == "service" ]] && category="service"
        
        # Build aliases array
        local aliases_json="[]"
        if [[ -n "${_v_aliases}" ]]; then
            local a_list=()
            local a
            for a in ${(s:,:)_v_aliases}; do
                a_list+=("\"$(_vde_escape_json "${a}")\"")
            done
            aliases_json="[${(j:,:)a_list}]"
        fi
        
        local cmd_json="null"
        [[ -n "${_v_cmd}" ]] && cmd_json="\"$(_vde_escape_json "${_v_cmd}")\""
        
        local svc_json="null"
        [[ -n "${_v_env}" ]] && svc_json="\"$(_vde_escape_json "${_v_env}")\""
        
        local ssh_port_json="null"
        [[ -n "${_v_port}" ]] && ssh_port_json="${_v_port}"
        
        local entry="        {
          \"name\": \"$(_vde_escape_json "${_v_name}")\",
          \"aliases\": ${aliases_json},
          \"display\": \"$(_vde_escape_json "${_v_disp}")\",
          \"pkgs\": \"$(_vde_escape_json "${_v_pkgs}")\",
          \"custom_cmd\": ${cmd_json},
          \"service_port\": ${svc_json},
          \"ssh_port\": ${ssh_port_json}
        }"
        
        if [[ "${category}" == "service" ]]; then
            svc_entries+=("${entry}")
        else
            lang_entries+=("${entry}")
        fi
    done < "$conf_file"
    
    # Build final JSON using Pure Beskar template
    {
        echo "{"
        echo "  \"version\": \"1.1\","
        echo "  \"vms\": {"
        echo "    \"language\": ["
        echo "${(j:,\n:)lang_entries}"
        echo "    ],"
        echo "    \"service\": ["
        echo "${(j:,\n:)svc_entries}"
        echo "    ]"
        echo "  }"
        echo "}"
    } > "$json_file"
    
    log_success "The Pure Beskar (.json) has been reconciled via Pure ZSH." "forge"
}
```

### lib/vm-common: `load_vm_types` (Snippet)
```zsh
    # Update the logic to fallback to CONF parser if JQ fails or is missing
    if [[ "${use_cache}" -ne 1 ]]; then
        if [[ -f "${VM_TYPES_JSON}" ]] && command -v jq >/dev/null 2>&1; then
            # ... existing JQ-based loading ...
        elif [[ -f "${VM_TYPES_CONF}" ]]; then
            _info "Parsing VM types from Raw Beskar (.conf) via ZSH..."
            while IFS='|' read -r _v_type _v_name _v_aliases _v_disp _v_pkgs _v_cmd _v_env _v_port _extra; do
                [[ -z "${_v_name}" || "${_v_type}" == "#"* ]] && continue
                
                VM_TYPE[${_v_name}]="${_v_type#vde-}" # Handle prefixed names if any
                [[ "${_v_type}" == "lang" ]] && lang_vms_array+=("${_v_name}")
                [[ "${_v_type}" == "service" ]] && service_vms_array+=("${_v_name}")
                
                VM_ALIASES[${_v_name}]="${_v_aliases}"
                VM_DISPLAY[${_v_name}]="${_v_disp}"
                VM_INSTALL[${_v_name}]="${_v_pkgs}"
                VM_CUSTOM_CMD[${_v_name}]="${_v_cmd}"
                VM_SVC_PORT[${_v_name}]="${_v_env}"
                VM_SSH_PORT[${_v_name}]="${_v_port}"
            done < "${VM_TYPES_CONF}"
            
            lang_vms=("${lang_vms_array[@]}")
            service_vms=("${service_vms_array[@]}")
        fi
    fi
```

## Verification & Testing
1. Rename `jq` to `jq.bak` (if possible) or simulate `command -v jq` failure.
2. Touch `data/vm-types.conf`.
3. Run `bin/vde start kotlin`.
4. Verify `data/vm-types.json` is correctly generated and valid.
5. Verify `.cache/vm-types.cache` is correctly generated and valid.
6. Verify kotlin starts with correct port 2211.
