# JUPYTERLAB RACE CONDITION REMEDIATION

## 1. Problem Analysis
The JupyterLab integration test is failing due to two distinct race conditions:
1. **The Process Name Desync:** The ignition script (`scripts/setup/jupyterlab-init.zsh`) checks for `jupyter-server`, but the actual binary is `jupyter-lab`. This causes the script to redundantly spawn the server if called multiple times.
2. **The Port Binding Window:** `vde-poll --exec` correctly detects the `jupyter-lab` process and succeeds. However, the Tornado web server takes an additional 5-10 seconds to bind to port 8888 *after* the process starts. Because the test immediately `curl`s the port upon process detection, it fails with "Connection Refused" and aborts the test prematurely instead of waiting for the port to open.

## 2. The Reforging
- **Fix 1:** Update `scripts/setup/jupyterlab-init.zsh` to correctly check for `jupyter-lab` via `pgrep`.
- **Fix 2:** Re-introduce the robust `curl` polling loop into `tests/integration/jupyterlab-spoke.test.zsh` immediately after the `vde-poll --exec` process check. This ensures we wait for both the process *and* the port binding.

## 3. Required Code Changes

### `scripts/setup/jupyterlab-init.zsh`
Change the ignition hook to match the actual execution string:
```zsh
if ! pgrep -f "jupyter-lab" >/dev/null; then
    echo "[VDE-JUPYTER] Forged in Beskar: Starting JupyterLab..." >> /logs/jupyter.log
    sudo -u devuser nohup tini -g -- ${_venv_path}/bin/jupyter lab --config=${_jupyter_config} >> /logs/jupyter.log 2>&1 &
fi
```

### `tests/integration/jupyterlab-spoke.test.zsh`
Update `test_runtime_connectivity` to poll the HTTP port after the process is verified:
```zsh
    # Use vde-poll to monitor hydration (Rule 23)
    # Mandate: JupyterLab has a ~12 minute hydration window. We wait 15m (900s).
    echo -n "(polling process...) "
    # Note: We use authorized VDE_ROOT_DIR exception here for vde-poll bootstrapping
    if VDE_ROOT_DIR="${PROJECT_ROOT}" "${PROJECT_ROOT}/bin/vde-poll" --exec "pgrep -f jupyter-lab" --timeout 900 vde-jupyterlab >/dev/null 2>&1; then
        echo -n "(polling HTTP port...) "
        local max_retries=900
        local retry=0
        
        while [[ $retry -lt $max_retries ]]; do
            if curl -s -I http://localhost:8888 | grep -q "HTTP/1.1"; then
                test_pass
                return 0
            fi
            sleep 1
            (( retry++ ))
            [[ $(( retry % 10 )) -eq 0 ]] && echo -n "."
        done
    fi
    
    test_fail "JupyterLab UI not responding on port 8888 after 900s"
```

## 4. Expected Outcome
The integration test will successfully wait for the full hydration and port binding sequence, satisfying the 12-minute window and turning the test suite 100% Green.