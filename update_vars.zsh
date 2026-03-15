#!/usr/bin/env zsh
# Script to update variable expansion syntax to ${VAR}

# Identify all shell scripts
FILES=($(find . -type f \( -not -path "*/.*" \) | xargs file | grep -E "shell|zsh" | grep -vE "\.pyc|\.pdf|\.png|\.jpg|\.test" | cut -d: -f1))

echo "Found ${#FILES[@]} files to process."

for file in "${FILES[@]}"; do
    if [[ ! -f "$file" ]]; then continue; fi
    
    # Check if it is a directory (sometimes find gives it)
    if [[ -d "$file" ]]; then continue; fi

    # Skip specific files
    if [[ "$file" == "./update_vars.zsh" ]]; then continue; fi

    # echo "Processing ${file}..."
    
    # Backup
    cp "$file" "${file}.bak"
    
    # Apply replacement
    # Using perl with lookarounds to be safe
    # (?<![\{\\]) - not preceded by { or \
    # \$ - literal $
    # ([a-zA-Z_]\w*|[0-9]+|[@*?\$!#-]) - capture group for variable name/special char
    # (?![a-zA-Z0-9_]*\}) - not followed by something that looks like an existing expansion (wait, my previous test used this or not?)
    
    # In my previous successful test, I used:
    # perl -pe 's/(?<![\{\\])\$([a-zA-Z_]\w*|[0-9]+|[@*?\$!#-])/\$\{$1\}/g'
    # Wait, if I have $VAR, it becomes ${VAR}.
    # If I have ${VAR}, the $ is followed by {, so the lookaround (?<![\{\\]) is NOT what prevents it.
    # Ah, \$ followed by [a-zA-Z_] DOES NOT match ${VAR} because { is NOT in [a-zA-Z_].
    
    perl -pi -e 's/(?<![\{\\])\$([a-zA-Z_]\w*|[0-9]+|[@*?\$!#-])/\$\{$1\}/g' "$file"
    
    # Verify syntax
    if ! zsh -n "$file" 2>/dev/null; then
        echo "  [ERROR] Syntax error in ${file}. Restoring backup."
        mv "${file}.bak" "$file"
    else
        # Success
        rm "${file}.bak"
    fi
done

echo "Update complete."
