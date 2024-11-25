#!/bin/bash

# Exit on error
set -e

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Running all checks..."

echo -e "\n1. Running format checks..."
"${REPO_ROOT}/ci/format.sh"

echo -e "\n2. Running type checks..."
"${REPO_ROOT}/ci/check_types.sh"

echo -e "\n3. Running tests..."
"${REPO_ROOT}/ci/test.sh"

echo -e "\nAll checks passed! ✨"
