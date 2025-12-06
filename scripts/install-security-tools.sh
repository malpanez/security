#!/bin/bash
set -euo pipefail

echo "[install-security-tools] Installing pre-commit hooks and tooling"
if command -v uv >/dev/null 2>&1; then
  uv pip install --system --requirement requirements-dev.txt
else
  pip install --requirement requirements-dev.txt
fi

echo "[install-security-tools] Done"
