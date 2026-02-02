#!/usr/bin/env zsh
echo "Running vde-parser unit tests..."
cd /Users/dderyldowney/dev || exit
echo "1. Running vde-parser.test.sh..."
time tests/unit/vde-parser.test.sh
echo -e "\n2. Running test_vde_parser_comprehensive.sh..."
time tests/unit/test_vde_parser_comprehensive.sh
echo -e "\n3. Checking BDD tests..."
time python3 -m pytest tests/features/docker-free/natural-language-parser.feature -v 2>&1
