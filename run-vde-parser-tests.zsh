#!/usr/bin/env zsh
echo "Running vde-parser unit tests..."
cd /Users/dderyldowney/dev || exit
echo "1. Running vde-parser.test.zsh..."
time zsh tests/unit/vde-parser.test.zsh
echo -e "\n2. Running test_vde_parser_comprehensive.zsh..."
time zsh tests/unit/test_vde_parser_comprehensive.zsh
echo -e "\n3. Checking BDD tests..."
time behave tests/features/docker-free/natural-language-parser.feature
