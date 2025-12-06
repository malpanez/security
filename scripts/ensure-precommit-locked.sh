#!/bin/bash
set -euo pipefail

echo "[ensure-precommit-locked] Updating pre-commit hooks to locked versions"
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit install --install-hooks
  pre-commit autoupdate --freeze
else
  echo "[ensure-precommit-locked] pre-commit not found; skipping"
fi
