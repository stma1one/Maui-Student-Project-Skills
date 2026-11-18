#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-true}"
PROJECT_ROOT="${2:-}"

if [ -z "$PROJECT_ROOT" ] || { [ "$MODE" != "true" ] && [ "$MODE" != "false" ]; }; then
  echo "Usage (Instructor tool): ./scripts/Set-Maui-Agent-Mode.sh [true|false] <ProjectRoot>" >&2
  exit 1
fi

CONFIG_FILE="$PROJECT_ROOT/.agents/MAUI-Agent-Mode.json"
mkdir -p "$(dirname "$CONFIG_FILE")"
cat << EOF > "$CONFIG_FILE"
{
  "studentCapabilityMode": $MODE,
  "description": {
    "true": "MAXIMIZE STUDENT CAPABILITY: staged planning, concept gates, ownership negotiation, student practice, and verification.",
    "false": "MAXIMIZE CODE GENERATED: implement complete feature slices efficiently while preserving verification and learning documentation when configured."
  }
}
EOF

echo "Instructor set studentCapabilityMode to $MODE in $CONFIG_FILE"
