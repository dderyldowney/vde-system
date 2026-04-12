#!/usr/bin/env zsh
# test-sentinel.zsh - Test the pre-commit hook sentinel

set -e

PROJECT_ROOT="$(cd "$(dirname "${0}")/../.." && pwd)"
TEST_REPO="${PROJECT_ROOT}/plans/scripts/test-repo"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
RESET='\033[0m'

# Cleanup
rm -rf "${TEST_REPO}"
mkdir -p "${TEST_REPO}"
cd "${TEST_REPO}"

# Initialize repo
git init -q

# Create dummy hook link
mkdir -p .git/hooks
ln -sf "${PROJECT_ROOT}/githooks/pre-commit" ".git/hooks/pre-commit"
chmod +x .git/hooks/pre-commit

# Also create bin/vde-spine-check.zsh in the test repo if needed
mkdir -p bin
cat <<EOF > bin/vde-spine-check.zsh
#!/usr/bin/env zsh
exit 0
EOF
chmod +x bin/vde-spine-check.zsh

echo "Test 1: Bash shebang check"
cat <<EOF > test-script.sh
#!/bin/bash
echo "This should be blocked"
EOF
git add test-script.sh

if git commit -m "Test bash shebang" > /dev/null 2>&1; then
    echo -e "${RED}FAILURE: Commit with bash shebang was ALLOWED${RESET}"
    exit 1
else
    echo -e "${GREEN}SUCCESS: Commit with bash shebang was BLOCKED${RESET}"
fi
git rm -f test-script.sh > /dev/null 2>&1

echo "Test 1.1: Valid Zsh shebang"
cat <<EOF > zsh-script.zsh
#!/usr/bin/env zsh
echo "This should be allowed"
EOF
git add zsh-script.zsh

if git commit -m "Test zsh shebang"; then
    echo -e "${GREEN}SUCCESS: Commit with zsh shebang was ALLOWED${RESET}"
else
    echo -e "${RED}FAILURE: Commit with zsh shebang was BLOCKED${RESET}"
    exit 1
fi

echo "Test 2: Secrets check"
cat <<EOF > config.zsh
#!/usr/bin/env zsh
API_KEY="sk_12345"
EOF
git add config.zsh

if git commit -m "Test secrets" > /dev/null 2>&1; then
    echo -e "${RED}FAILURE: Commit with secrets was ALLOWED${RESET}"
    exit 1
else
    echo -e "${GREEN}SUCCESS: Commit with secrets was BLOCKED${RESET}"
fi

echo "Test 3: Spine check failure"
cat <<EOF > bin/vde-spine-check.zsh
#!/usr/bin/env zsh
exit 1
EOF
chmod +x bin/vde-spine-check.zsh

cat <<EOF > valid.zsh
#!/usr/bin/env zsh
echo "This is valid"
EOF
git add valid.zsh

if git commit -m "Test spine check failure" > /dev/null 2>&1; then
    echo -e "${RED}FAILURE: Commit with spine check failure was ALLOWED${RESET}"
    exit 1
else
    echo -e "${GREEN}SUCCESS: Commit with spine check failure was BLOCKED${RESET}"
fi

echo -e "\n${GREEN}All tests passed!${RESET}"
rm -rf "${TEST_REPO}"
