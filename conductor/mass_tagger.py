#!/usr/bin/env python3
# @shared-law (Forge Component)
import os
import re
from pathlib import Path

# The VDE Root - Hardcoded to the current workspace root to avoid directory drift
VDE_ROOT = Path("/Users/dderyldowney/VDE")

# Tagging logic based on Mandate 24
def get_tag_info(file_path):
    rel_path = str(file_path.relative_to(VDE_ROOT))
    
    if rel_path.startswith("bin/") or rel_path.startswith("scripts/"):
        if "security" in rel_path or "uap" in rel_path or "audit" in rel_path:
            return "@forge", "Governance Auditor"
        return "@armor", "Engine Logic"
        
    if rel_path.startswith("lib/"):
        if "security" in rel_path or "audit" in rel_path or "metrics" in rel_path:
            return "@shared-law", "Governance Library"
        return "@armor", "Engine Core"
        
    if rel_path.startswith("tests/features/steps/"):
        return "@forge", "BDD Step Definition"
        
    if rel_path.startswith("tests/"):
        return "@forge", "Test Logic"
        
    if rel_path.startswith(".github/"):
        return "@forge", "Governance Workflow"
        
    if rel_path.startswith(".gemini_security/"):
        return "@forge", "Security Governance"
        
    if rel_path.startswith("githooks/"):
        return "@forge", "Governance Gate"
        
    if rel_path.startswith("data/"):
        return "@armor", "Beskar Registry DNA"
        
    if rel_path.startswith("docs/"):
        return "@shared-law", "Sovereign Documentation"
        
    if rel_path.startswith("templates/"):
        return "@shared-law", "Sovereign Template"
        
    if rel_path.startswith("env-files/"):
        return "@armor", "Spoke Environment"

    return "@shared-law", "Forge Component"

def get_comment_syntax(file_path, tag, effect):
    ext = file_path.suffix.lower()
    name = file_path.name
    
    if ext in [".zsh", ".sh", ".py", ".yml", ".yaml", ".env", ".conf"] or name in ["Dockerfile", "Makefile"] or not ext:
        return f"# {tag} ({effect})\n"
    if ext in [".md", ".html", ".xml"]:
        return f"<!-- {tag} ({effect}) -->\n"
    if ext in [".json"]:
        # JSON is tricky. We'll add a dummy key at the top if it's a dict.
        # But Mandate 24 says: For .json: Use '"@tag": "(Effect)",' at the beginning of the object.
        # We will handle JSON natively in the injection logic.
        return f'  "{tag}": "({effect})",\n'
    if ext in [".js", ".c", ".cpp", ".java", ".go", ".rs"]:
        return f"// {tag} ({effect})\n"
    if ext in [".sql"]:
        return f"-- {tag} ({effect})\n"
        
    return f"# {tag} ({effect})\n"

def is_binary(file_path):
    try:
        with open(file_path, 'tr') as check_file:
            check_file.read(1024)
            return False
    except UnicodeDecodeError:
        return True

def process_file(file_path):
    if is_binary(file_path) or file_path.suffix == ".bak":
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        return False

    if not lines:
        return False

    # Check if tag already exists in lines 1-3
    tag_pattern = re.compile(r'(@armor|@forge|@shared-law)')
    for i in range(min(3, len(lines))):
        if tag_pattern.search(lines[i]):
            return False # Already tagged

    tag, effect = get_tag_info(file_path)
    comment_line = get_comment_syntax(file_path, tag, effect)

    # Insert logic
    if file_path.suffix == ".json":
        # Try to insert after the first '{'
        inserted = False
        for i, line in enumerate(lines):
            if '{' in line:
                # Insert after the {
                parts = line.split('{', 1)
                lines[i] = parts[0] + '{\n' + comment_line + parts[1]
                inserted = True
                break
        if not inserted:
            # If no {, just put it at line 2
            if len(lines) > 1:
                lines.insert(1, comment_line)
            else:
                lines.append(comment_line)
    else:
        # Standard insert at line 2 (index 1)
        # If it's a 1-line file, just append
        if len(lines) > 1:
            lines.insert(1, comment_line)
        else:
            lines.append(comment_line)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return True

def main():
    exclude_dirs = ['.git', '.cache', 'logs', 'node_modules', '__pycache__', 'SKILLS', 'projects']
    tagged_count = 0

    for root, dirs, files in os.walk(VDE_ROOT):
        # Prune excluded dirs
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            # Skip specific files
            if file in ['vde-security-audit.zsh', 'vde-root-guard', 'README.md', 'fifo_test.log', 'vde_exec.log']:
                continue
                
            file_path = Path(root) / file
            if process_file(file_path):
                tagged_count += 1
                print(f"Tagged: {file_path.relative_to(VDE_ROOT)}")

    print(f"\\n[SUCCESS] Successfully tagged {tagged_count} files.")

if __name__ == "__main__":
    main()
