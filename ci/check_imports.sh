#!/bin/bash

# Exit on error
set -e

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="${REPO_ROOT}/ci/config"

echo "Running from repository root: ${REPO_ROOT}"

# Run isort check
echo "Running isort check..."
isort --check-only --diff --settings-path="${CONFIG_DIR}/.isort.cfg" "${REPO_ROOT}"

# Run flake8 import checks
echo -e "\nRunning flake8 import checks..."
flake8 --config="${CONFIG_DIR}/.flake8" --select=F4,I,E,W "${REPO_ROOT}"

# If we get here, all checks passed
echo -e "\nAll import checks passed! ✨"
