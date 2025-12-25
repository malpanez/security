#!/bin/bash
set -euo pipefail

echo "[install-security-tools] Installing pre-commit hooks and tooling"
if command -v uv >/dev/null 2>&1; then
  uv pip install --system -e ".[dev]"
else
  pip install -e ".[dev]"
fi

echo "[install-security-tools] Done"
