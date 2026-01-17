# SSH Authentication Problem - Investigation Summary

## Problem Description

SSH authentication to VDE containers fails with "Permission denied (publickey)" despite having correct SSH keys baked into the image.

## Current Status

- **Working:** Container builds, keys are baked into image during build
- **Broken:** SSH authentication fails with `Permission denied (publickey)`

## What We Fixed

### 1. Reverted Dockerfile to Original COPY Approach
**File:** `configs/docker/base-dev.Dockerfile`

**Changed FROM (broken):**
```dockerfile
RUN mkdir -p /home/${USERNAME}/.ssh && \
    if [ -d /public-ssh-keys ]; then \
        for key in /public-ssh-keys/*.pub; do \
            [ -f "$key" ] && cat "$key" >> /home/${USERNAME}/.ssh/authorized_keys; \
        done; \
    fi
```

**Changed TO (fixed):**
```dockerfile
COPY public-ssh-keys/*.pub /tmp/ssh-keys/
RUN cat /tmp/ssh-keys/*.pub > /home/${USERNAME}/.ssh/authorized_keys 2>/dev/null || true && \
    if [ -s /home/${USERNAME}/.ssh/authorized_keys ]; then \
        chmod 600 /home/${USERNAME}/.ssh/authorized_keys && \
        chown ${USERNAME}:${USERNAME} /home/${USERNAME}/ssh/authorized_keys; \
    else \
        rm -f /home/${USERNAME}/ssh/authorized_keys; \
    fi && \
    rm -rf /tmp/ssh-keys
```

### 2. Cleaned Up Unnecessary Bind Mounts
**Files:** All `configs/docker/*/docker-compose.yml`

**Removed:**
- `public-ssh-keys:/public-ssh-keys:ro` - keys are now baked in
- `logs/<service>:/logs` - unnecessary runtime logs
- SSH agent socket bind mounts
- All SSH agent forwarding comments

**Kept:**
- Language VMs: `projects/<language>:/home/devuser/workspace`
- Service VMs: `data/<service>:/data` (persistence)
- Service VMs: `configs/<service>:/...` (configuration)

## What's Working

✅ Container builds successfully
✅ Keys copied from build context to image during build
✅ authorized_keys file exists with correct content
✅ File permissions are correct (600, devuser:devuser)
✅ SSH daemon is running and listening on port 2222
✅ Port mapping is correct (2222:22)
✅ MD5sum of source and destination keys match (136f203f52d437630c22140873278689)
✅ `sshd -T` shows `pubkeyauthentication yes`
✅ Key exchange happens (client offers public key, server responds)

## What's Broken

❌ SSH authentication: `dderyldowney@localhost: Permission denied (publickey)`

## Verification Steps Performed

1. **File content comparison:**
   - Source key: `id_ed25519.pub` (109 bytes)
   - Container key: `authorized_keys` (109 bytes)
   - MD5sum matches: `136f203f52d437630c22140873278689`

2. **Permissions check:**
   - `.ssh/` directory: `drwx------` (700) devuser:devuser ✓
   - `authorized_keys`: `-rw-------` (600) devuser:devuser ✓
   - `known_hosts`: `-rw-------` (600) devuser:devuser ✓

3. **SSH daemon status:**
   - Process running: ✓
   - Listening on port 22: ✓ (via nc -zv test)
   - PubkeyAuthentication: yes (from sshd -T) ✓

4. **Key exchange:**
   - Client offers public key (type 50 packet) ✓
   - Server responds (type 51 packet) ✓
   - No additional debug info available

5. **Logs:**
   - `/var/log/auth.log` - doesn't exist
   - `journalctl -u ssh` - no recent entries
   - Debug logging enabled but no output captured

6. **Internal SSH test:**
   - SSH from within container also fails with same error
   - Even with a fresh key generated inside container

## Potential Causes to Investigate

### 1. PAM Configuration
- UsePAM is set to `yes` in sshd_config
- PAM may be rejecting the authentication for some reason
- Check: `/etc/pam.d/sshd` configuration

### 2. Container Security Policies
- seccomp filters might be blocking something
- AppArmor profiles (if active)
- Docker security policies

### 3. Subtle Filesystem Issues
- Extended attributes (xattrs) on files
- SELinux contexts (if enabled)
- Hidden characters or encoding issues

### 4. SSH Daemon Configuration
- Some other sshd_config setting overriding auth
- Missing or incorrect AuthorizedKeysFile specification
- AuthenticationMethods configuration issue

### 5. Build Context Issues
- Keys copied from build context may not be what we expect
- Docker build cache might be causing issues

### 6. Timing/Initialization Issues
- sshd not fully initialized when connection attempted
- Something in the command wrapper causing issues
- Container startup order problem

## Files Modified

**Committed:**
- `configs/docker/base-dev.Dockerfile` - reverted to COPY approach
- All `configs/docker/*/docker-compose.yml` - removed unnecessary bind mounts
- `CLAUDE.md` - added MUST-DO for SSH key management

**Not Committed:**
- `public-ssh-keys/id_ed25519.pub` - user's public key (correctly placed)

## Next Steps for Investigation

1. Check PAM configuration: `cat /etc/pam.d/sshd`
2. Check seccomp/AppArmor: `docker inspect python-dev | grep -i seccomp`
3. Try running sshd manually without the shell wrapper
4. Check if there's a command wrapper issue in docker-compose.yml
5. Compare with a working container (if one exists)
6. Check if issue exists in original working commits
7. Investigate sshd_config more thoroughly for auth-related settings

## Original Design Reference

**Working design (commit d5bb74d):**
- BUILD: `COPY --chown=${USERNAME}:${USERNAME} public-ssh-keys/* /home/${USERNAME}/.ssh/authorized_keys`
- RUNTIME: Only essential bind mounts (projects/, data/)

**Breaking change (commit eb72198):**
- Changed to RUN trying to read from `/public-ssh-keys` at build time
- Bind mounts don't exist during build → empty directory
- authorized_keys gets deleted

## Test Commands

```bash
# Build container
docker-compose -f configs/docker/python/docker-compose.yml up -d --force-recreate

# Check SSH status
docker exec python-dev ps aux | grep sshd
docker exec python-dev netstat -tlnp | grep 22
docker port python-dev

# Test SSH
ssh -o StrictHostKeyChecking=no -p 2222 localhost 'whoami'

# Debug from within container
docker exec python-dev bash -c 'cat /home/devuser/.ssh/authorized_keys'
docker exec python-dev bash -c 'stat -c "%a %U:%G" /home/devuser/.ssh/authorized_keys'

# Check effective sshd config
docker exec python-dev sshd -T | grep pubkey
```

## Git Commits Referenced

- **d5bb74d** - Original working design with COPY
- **eb72198** - Breaking change to RUN (commit "fix: Second deep bug hunt")
- **645e0d0** - Our revert to COPY approach (current HEAD)

## Session Info

- Date: 2026-01-17
- Container tested: python-dev
- User: dderyldowney on macOS
- SSH client: OpenSSH_10.0p2
- SSH server in container: OpenSSH_9.2p1
- Image: dev-python:latest (built with no-cache)
