#!/usr/bin/env zsh

# Run vde-parser tests
cd /Users/dderyldowney/dev || exit

echo "Running vde-parser.test.sh..."
echo "----------------------------"
./tests/unit/vde-parser.test.sh
echo "----------------------------"

echo -e "\nRunning test_vde_parser_comprehensive.sh..."
echo "----------------------------------------"
./tests/unit/test_vde_parser_comprehensive.sh
