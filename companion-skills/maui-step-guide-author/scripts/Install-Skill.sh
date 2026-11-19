#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-Project}"
PROJECT_PATH="${2:-.}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "$SCRIPT_DIR/skills/maui-step-guide-author" ]; then
  PACKAGE_ROOT="$SCRIPT_DIR"
else
  PACKAGE_ROOT="$(dirname "$SCRIPT_DIR")"
fi
SKILL_SOURCE="$PACKAGE_ROOT/skills/maui-step-guide-author"

if [ ! -d "$SKILL_SOURCE" ]; then
  echo "Error: Cannot find skill source: $SKILL_SOURCE" >&2
  exit 1
fi

install_skill_files() {
  local src="$1"
  local dest="$2"
  local exclude_evals="$3"
  rm -rf "$dest"
  mkdir -p "$dest"
  for item in "$src/"*; do
    local base_name
    base_name="$(basename "$item")"
    if [ "$exclude_evals" = true ] && [ "$base_name" = "evals" ]; then
      continue
    fi
    cp -R "$item" "$dest/"
  done
}

case "$TARGET" in
  Project)
    mkdir -p "$PROJECT_PATH"
    RESOLVED_PROJECT="$(cd "$PROJECT_PATH" && pwd)"

    PROJECT_AGENTS="$RESOLVED_PROJECT/.agents"
    PROJECT_SKILL_DEST="$PROJECT_AGENTS/skills/maui-step-guide-author"
    PROJECT_LEARNING_DEST="$RESOLVED_PROJECT/Learning"
    PROJECT_SCRIPTS_DEST="$RESOLVED_PROJECT/Scripts"

    install_skill_files "$SKILL_SOURCE" "$PROJECT_SKILL_DEST" true

    mkdir -p "$PROJECT_LEARNING_DEST/Guides" "$PROJECT_LEARNING_DEST/Mockups" "$PROJECT_LEARNING_DEST/Images" "$PROJECT_LEARNING_DEST/Diagrams" "$PROJECT_SCRIPTS_DEST"

    for source_name in generate_book_pdf.py capture_mockup_blocks.py validate_learning_book.py validate_bagrut_compliance.py generate_architecture_diagrams.py ensure_maui_devflow.py ensure_test_project.py validate_tests.py requirements-learning-book.txt; do
      case "$source_name" in
        generate_book_pdf.py) target_name="Generate-Learning-Book-Pdf.py" ;;
        capture_mockup_blocks.py) target_name="Capture-Mockup-Blocks.py" ;;
        validate_learning_book.py) target_name="Validate-Learning-Book.py" ;;
        validate_bagrut_compliance.py) target_name="Validate-Bagrut-Compliance.py" ;;
        generate_architecture_diagrams.py) target_name="Generate-Architecture-Diagrams.py" ;;
        ensure_maui_devflow.py) target_name="Ensure-Maui-DevFlow.py" ;;
        ensure_test_project.py) target_name="Ensure-Test-Project.py" ;;
        validate_tests.py) target_name="Validate-Tests.py" ;;
        requirements-learning-book.txt) target_name="Learning-Book-Requirements.txt" ;;
      esac
      if [ -f "$SKILL_SOURCE/scripts/$source_name" ]; then
        cp "$SKILL_SOURCE/scripts/$source_name" "$PROJECT_SCRIPTS_DEST/$target_name"
      fi
    done

    echo "Installed MAUI Step Guide Author skill and Scripts tools into project: $RESOLVED_PROJECT"
    ;;
  Codex)
    DEST="$HOME/.codex/skills/maui-step-guide-author"
    install_skill_files "$SKILL_SOURCE" "$DEST" false
    echo "Installed Codex skill: $DEST"
    ;;
  ClaudeCode)
    DEST="$HOME/.claude/skills/maui-step-guide-author"
    install_skill_files "$SKILL_SOURCE" "$DEST" false
    echo "Installed Claude Code skill: $DEST"
    ;;
  *)
    echo "Usage: ./Install-Skill.sh [Project|Codex|ClaudeCode] [ProjectPath]"
    exit 1
    ;;
esac
