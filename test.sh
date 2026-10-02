#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1

echo "==> build"
make build
echo "==> unit tests"
python3 -m unittest discover -s tests/unit -v
echo "==> system tests"
python3 -m unittest discover -s tests/system -v
echo "==> all tests passed"
