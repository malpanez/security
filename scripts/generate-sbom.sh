#!/bin/bash
set -euo pipefail

echo "[generate-sbom] Generating SBOM with syft"
if command -v syft >/dev/null 2>&1; then
  syft dir:. -o cyclonedx-json > sbom.cyclonedx.json
  echo "[generate-sbom] SBOM written to sbom.cyclonedx.json"
else
  echo "[generate-sbom] syft not installed; skipping"
fi
