#!/bin/bash

# Exit on error
set -e

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="${REPO_ROOT}/ci/config"

echo "Running from repository root: ${REPO_ROOT}"

# Remove unused imports with autoflake
echo "Removing unused imports with autoflake..."
find "${REPO_ROOT}" -name "*.py" ! -path "*/\.*" -exec autoflake --in-place --remove-all-unused-imports {} +

# Fix imports with isort
echo -e "\nFixing imports with isort..."
isort --settings-path="${CONFIG_DIR}/.isort.cfg" "${REPO_ROOT}"

# Format code with black
echo -e "\nFormatting code with black..."
find "${REPO_ROOT}" -name "*.py" ! -path "*/\.*" -exec black --line-length=88 {} +

# Run the checks to verify everything is formatted
echo -e "\nVerifying formatting..."
"${REPO_ROOT}/ci/check_imports.sh"
