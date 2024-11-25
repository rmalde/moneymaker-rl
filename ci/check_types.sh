#!/bin/bash

# Exit on error
set -e

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Running type checks..."
mypy "${REPO_ROOT}/moneymaker_rl" --ignore-missing-imports
