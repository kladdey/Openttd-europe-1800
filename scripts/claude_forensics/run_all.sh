#!/usr/bin/env bash
# Re-run every Claude reinvestigation analysis from committed evidence only.
# No game, GRF or network access is needed. Outputs: docs/research/claude_forensics/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
for s in infer_cost_factors cost_curve_analysis fleet_era_comparison train_physics_model ledger_analysis heavy_freight_te; do
  echo "=== $s"; python3 -I "$ROOT/scripts/claude_forensics/$s.py" "$ROOT" > /dev/null
done
python3 -I "$ROOT/scripts/claude_forensics/verify_claims.py" "$ROOT"
