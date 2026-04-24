import subprocess
# @shared-law (Forge Component)
import os
import sys

def test_ssh():
    vde_root = os.getcwd()
    bin_vde = os.path.join(vde_root, "bin", "vde")
    
    env = os.environ.copy()
    env["VDE_ROOT_DIR"] = vde_root
    env["VDE_LOG_OUTPUT"] = "file"
    
    print(f"Testing vde enter with SSH_AUTH_SOCK={env.get('SSH_AUTH_SOCK')}")
    
    # Try with BatchMode
    cmd = ["zsh", bin_vde, "enter", "python", "-o", "BatchMode=yes", "ssh-add -l"]
    print(f"Executing: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        cwd=vde_root
    )
    
    print(f"RC: {result.returncode}")
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")

if __name__ == "__main__":
    test_ssh()
