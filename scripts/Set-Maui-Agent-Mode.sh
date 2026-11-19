#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-true}"
PROJECT_ROOT="${2:-}"
INCLUDE_TESTS="${3:-true}"
TEST_MANAGEMENT_MODE="${4:-combined}"

if [ -z "$PROJECT_ROOT" ] || { [ "$MODE" != "true" ] && [ "$MODE" != "false" ]; }; then
  echo "Usage (Instructor tool): ./scripts/Set-Maui-Agent-Mode.sh [true|false] <ProjectRoot> [includeTests:true|false] [testManagementMode:combined|agent|student]" >&2
  exit 1
fi

if [ "$INCLUDE_TESTS" != "true" ] && [ "$INCLUDE_TESTS" != "false" ]; then
  echo "Error: includeTests must be 'true' or 'false'." >&2
  exit 1
fi

case "$TEST_MANAGEMENT_MODE" in
  combined|agent|student) ;;
  *)
    echo "Error: testManagementMode must be one of: combined, agent, student." >&2
    exit 1
    ;;
esac

CONFIG_FILE="$PROJECT_ROOT/.agents/MAUI-Agent-Mode.json"
mkdir -p "$(dirname "$CONFIG_FILE")"
cat << EOF > "$CONFIG_FILE"
{
  "studentCapabilityMode": $MODE,
  "includeTests": $INCLUDE_TESTS,
  "testManagementMode": "$TEST_MANAGEMENT_MODE",
  "description": {
    "true": "MAXIMIZE STUDENT CAPABILITY: staged planning, concept gates, ownership negotiation, student practice, and verification.",
    "false": "MAXIMIZE CODE GENERATED: implement complete feature slices efficiently while preserving verification and learning documentation when configured.",
    "includeTests": "Boolean (default: true). Whether the project provisions, writes, and validates xUnit tests (<AppName>.Tests). When false, testManagementMode is ignored and tests are skipped.",
    "testManagementMode": {
      "combined": "(Default) Combined: Agent creates and explains tests at the end of each stage/slice, proposes selected test cases for the student to write, and documents all tests in Learning/Test-Documentation.md.",
      "agent": "Agent: Agent independently writes and runs xUnit tests as part of the slice workflow and documents them in Learning/Test-Documentation.md.",
      "student": "Student: Agent guides the student through a Socratic dialogue to identify required test cases and coaches the student in writing the xUnit tests.",
      "maximizeCodeOverride": "When studentCapabilityMode is false (MAXIMIZE CODE GENERATED) and includeTests is true, the agent ALWAYS writes and runs all tests regardless of testManagementMode and documents them in Learning/Test-Documentation.md."
    }
  }
}
EOF

echo "Instructor set studentCapabilityMode=$MODE, includeTests=$INCLUDE_TESTS, testManagementMode=$TEST_MANAGEMENT_MODE in $CONFIG_FILE"
