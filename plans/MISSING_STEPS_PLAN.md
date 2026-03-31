# Missing Step Definitions Plan

## Analysis Summary
- **Total Undefined Steps:** 60 (unique: ~55)
- **Strategy:** Add all steps to appropriate existing files in batches

## File Assignments

### FILE 1: ssh_config_steps.py (MAJOR - 25 steps)
**Category: SSH Agent & Key Management**

| Step Type | Pattern | Implementation Notes |
|-----------|---------|---------------------|
| GIVEN | `I do not have an SSH agent running` | Add decorator to existing `step_ssh_agent_not_running` |
| GIVEN | `my SSH agent is not running` | Add decorator to existing `step_ssh_agent_not_running` |
| GIVEN | `I have all key types in ~/.ssh/vde/` | Create keys of all types (ed25519, rsa, ecdsa) |
| GIVEN | `I have SSH configured` | Verify SSH config exists |
| WHEN | `I create my first VM` | Add decorator to existing step |
| THEN | `the SSH agent should be started automatically` | Verify agent running |
| THEN | `an SSH key should be generated automatically` | Verify key exists in ~/.ssh/vde/ |
| THEN | `an ed25519 key should be generated` | Verify ed25519 key exists |
| THEN | `the key should be loaded into the agent` | Verify key in agent |
| THEN | `the key should be generated with a comment` | Verify key has comment |
| THEN | `I should see the SSH agent status` | Check output contains status |
| THEN | `I should see my available SSH keys` | Check output lists keys |
| THEN | `I should see keys loaded in the agent` | Check agent has keys |
| THEN | `I should see usage examples` | Check output has examples |
| THEN | `the list-vms command should show available VMs` | Run VDE command "vde list" |
| THEN | `my keys should be loaded automatically` | Verify keys in agent |
| THEN | `my keys should be loaded into the agent` | Verify keys in agent |
| THEN | `all keys should be loaded into the agent` | Verify all keys loaded |
| THEN | `I should be informed of what happened` | Check output has info |
| THEN | `I should be able to use SSH immediately` | Verify SSH works |
| THEN | `the best key should be selected for SSH config` | Verify config has correct key |
| THEN | `all my SSH keys should be detected` | Verify all keys found |
| THEN | `my existing SSH keys should be detected automatically` | Verify keys detected |
| THEN | `ed25519 should be the preferred key type` | Verify ed25519 is default |

### FILE 2: vm_lifecycle_steps.py (10 steps)
**Category: VM Creation & Management**

| Step Type | Pattern | Implementation Notes |
|-----------|---------|---------------------|
| GIVEN | `I have VMs configured` | Check configs exist |
| WHEN | `I create a VM` | Call vde create |
| WHEN | `I create a new VM` | Call vde create |
| WHEN | `I start a VM` | Call vde start |
| WHEN | `I start the VM` | Call vde start |
| WHEN | `I shutdown and rebuild the VM` | Stop, remove, create |
| WHEN | `I use SSH to connect to any VM` | SSH to a VM |
| THEN | `the VM should start normally` | Verify VM running |
| THEN | `my SSH configuration should still work` | Test SSH connection |
| THEN | `I should not need to reconfigure SSH` | Verify config unchanged |

### FILE 3: ssh_connection_steps.py (8 steps)
**Category: SSH Connections & Config**

| Step Type | Pattern | Implementation Notes |
|-----------|---------|---------------------|
| THEN | `the SSH config entries should exist` | Verify config has entries |
| THEN | `I should be able to use short hostnames` | Test vde-python works |
| THEN | `I should not need to remember port numbers` | Verify config has ports |
| THEN | `my keys should still work` | Test SSH auth |
| THEN | `my public keys should be copied to public-ssh-keys/` | Verify public keys copied |
| THEN | `all my public keys should be in the VM's authorized_keys` | Verify in container |
| THEN | `I should be able to use any of the keys` | Test each key |
| THEN | `I should not need to manually copy keys` | Verify auto-copy |

### FILE 4: documented_workflow_steps.py (8 steps)
**Category: Documentation & User Experience**

| Step Type | Pattern | Implementation Notes |
|-----------|---------|---------------------|
| WHEN | `I read the documentation` | Read README or help |
| THEN | `I should see that SSH is automatic` | Check docs mention auto |
| THEN | `I should not see manual setup instructions` | Verify no manual steps |
| THEN | `I should be able to start using VMs immediately` | Verify quick start |
| THEN | `no SSH configuration messages should be displayed` | Check output |
| THEN | `the setup should happen automatically` | Verify auto setup |
| THEN | `I should only see VM creation messages` | Check output focus |
| THEN | `I should not need to configure anything manually` | Verify no manual config |

### FILE 5: ssh_remote_access_steps.py (4 steps)
**Category: Remote Access & Tools**

| Step Type | Pattern | Implementation Notes |
|-----------|---------|---------------------|
| WHEN | `I use the system ssh command` | Run ssh command |
| WHEN | `I use OpenSSH clients` | Test OpenSSH |
| WHEN | `I use VSCode Remote-SSH` | Test VSCode config |
| THEN | `all should work with the same configuration` | Verify consistent |
| THEN | `all should use my SSH keys` | Verify key usage |

## Implementation Order
1. ssh_config_steps.py (most steps, core functionality)
2. vm_lifecycle_steps.py (VM operations)
3. ssh_connection_steps.py (SSH connections)
4. documented_workflow_steps.py (user experience)
5. ssh_remote_access_steps.py (remote access)
