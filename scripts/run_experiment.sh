#!/bin/bash
set -e

echo "=== Laws of Simplicity Experiment Runner ==="
echo ""

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

mkdir -p data/raw data/results

echo ""
echo "Starting experiment..."
uv run python -m experiment "$@"

echo ""
echo "Experiment complete. Results in data/results/"
