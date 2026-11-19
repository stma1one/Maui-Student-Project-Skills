#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-Project}"
PROJECT_PATH="${2:-.}"
UPGRADE=false
INSTALL_LEARNING_BOOK_DEPENDENCIES=false
SKIP_DEVFLOW=false
SKIP_CLI=false

for arg in "${@:3}"; do
  case "$arg" in
    --upgrade)
      UPGRADE=true
      ;;
    --install-learning-book-dependencies)
      INSTALL_LEARNING_BOOK_DEPENDENCIES=true
      ;;
    --skip-devflow|--no-devflow)
      SKIP_DEVFLOW=true
      ;;
    --skip-cli|--no-cli|--skip-devflow-cli)
      SKIP_CLI=true
      ;;
    *)
      echo "Usage: ./scripts/Install-Skill.sh [Project|Codex|ClaudeCode] [ProjectPath] [--upgrade] [--install-learning-book-dependencies] [--skip-devflow] [--skip-cli]" >&2
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(dirname "$SCRIPT_DIR")"
SKILL_SOURCE="$PACKAGE_ROOT/skills/maui-k12-baton-workflow"
TEMPLATE_ROOT="$PACKAGE_ROOT/project-template"
COMPANION_SOURCE="$PACKAGE_ROOT/companion-skills/maui-step-guide-author/skills/maui-step-guide-author"

if [ ! -d "$SKILL_SOURCE" ]; then
  echo "Error: Cannot find skill source: $SKILL_SOURCE" >&2
  exit 1
fi

replace_dir_clean() {
  local src="$1"
  local dest="$2"
  local exclude_evals="${3:-false}"
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

copy_file_if_missing() {
  local src="$1"
  local dest="$2"
  if [ -f "$dest" ]; then
    echo "Preserved existing file: $dest"
  else
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    echo "Created: $dest"
  fi
}

install_or_upgrade_agents_md() {
  local src="$1"
  local dest="$2"
  if [ ! -f "$dest" ]; then
    cp "$src" "$dest"
    echo "Created: $dest"
    return
  fi

  if cmp -s "$src" "$dest"; then
    echo "AGENTS.md is already up to date."
  else
    cp "$src" "$dest.new"
    echo "NOTICE: Existing AGENTS.md differs from package template. Wrote updated template to: $dest.new"
  fi
}

copy_companion_skill() {
  local destination="$1"
  local exclude_evals="${2:-false}"
  if [ -d "$COMPANION_SOURCE" ]; then
    replace_dir_clean "$COMPANION_SOURCE" "$destination" "$exclude_evals"
    echo "Installed companion skill: maui-step-guide-author"
  fi
}

case "$TARGET" in
  Project)
    mkdir -p "$PROJECT_PATH"
    RESOLVED_PROJECT="$(cd "$PROJECT_PATH" && pwd)"

    install_or_upgrade_agents_md "$TEMPLATE_ROOT/AGENTS.md" "$RESOLVED_PROJECT/AGENTS.md"

    PROJECT_AGENTS="$RESOLVED_PROJECT/.agents"
    PROJECT_SKILL_DEST="$PROJECT_AGENTS/skills/maui-k12-baton-workflow"
    PROJECT_TEMPLATE_DEST="$PROJECT_AGENTS/templates"
    PROJECT_LEARNING_DEST="$RESOLVED_PROJECT/Learning"
    PROJECT_SCRIPTS_DEST="$RESOLVED_PROJECT/Scripts"

    replace_dir_clean "$SKILL_SOURCE" "$PROJECT_SKILL_DEST" true
    copy_companion_skill "$PROJECT_AGENTS/skills/maui-step-guide-author" true
    replace_dir_clean "$TEMPLATE_ROOT/.agents/templates" "$PROJECT_TEMPLATE_DEST"

    mkdir -p "$PROJECT_SCRIPTS_DEST"
    for script in "$TEMPLATE_ROOT/Scripts/"*; do
      if [ -f "$script" ]; then
        dest_script="$PROJECT_SCRIPTS_DEST/$(basename "$script")"
        if [ ! -f "$dest_script" ]; then
          cp "$script" "$dest_script"
          echo "Installed script: $dest_script"
        elif [ "$UPGRADE" = true ]; then
          cp "$script" "$dest_script"
          echo "Upgraded script: $dest_script"
        elif ! cmp -s "$script" "$dest_script"; then
          echo "NOTICE: Script '$(basename "$script")' differs from package version. Re-run with --upgrade to overwrite."
        fi
      fi
    done

    # Sync canonical Python tools from companion skill when missing or upgrading
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
      src_tool="$COMPANION_SOURCE/scripts/$source_name"
      dst_tool="$PROJECT_SCRIPTS_DEST/$target_name"
      if [ -f "$src_tool" ] && { [ "$UPGRADE" = true ] || [ ! -f "$dst_tool" ]; }; then
        cp "$src_tool" "$dst_tool"
      fi
    done

    chmod +x "$PROJECT_SCRIPTS_DEST/"*.sh 2>/dev/null || true

    mkdir -p "$PROJECT_AGENTS"
    copy_file_if_missing "$TEMPLATE_ROOT/.agents/MAUI-Agent-Mode.json" "$PROJECT_AGENTS/MAUI-Agent-Mode.json"

    mkdir -p "$PROJECT_LEARNING_DEST/Guides" "$PROJECT_LEARNING_DEST/Mockups" "$PROJECT_LEARNING_DEST/Images" "$PROJECT_LEARNING_DEST/Diagrams"
    copy_file_if_missing "$TEMPLATE_ROOT/Learning/Current-Phase.md" "$PROJECT_LEARNING_DEST/Current-Phase.md"
    copy_file_if_missing "$TEMPLATE_ROOT/Learning/Student-Mastery.md" "$PROJECT_LEARNING_DEST/Student-Mastery.md"
    copy_file_if_missing "$TEMPLATE_ROOT/Learning/MAUI-Learning-Book.md" "$PROJECT_LEARNING_DEST/MAUI-Learning-Book.md"
    copy_file_if_missing "$TEMPLATE_ROOT/Learning/Bagrut-Compliance.md" "$PROJECT_LEARNING_DEST/Bagrut-Compliance.md"
    copy_file_if_missing "$TEMPLATE_ROOT/Learning/AI-And-External-Code-Attribution.md" "$PROJECT_LEARNING_DEST/AI-And-External-Code-Attribution.md"
    copy_file_if_missing "$TEMPLATE_ROOT/Learning/Test-Documentation.md" "$PROJECT_LEARNING_DEST/Test-Documentation.md"

    if [ -f "$PROJECT_SCRIPTS_DEST/Ensure-Test-Project.sh" ]; then
      bash "$PROJECT_SCRIPTS_DEST/Ensure-Test-Project.sh" "$RESOLVED_PROJECT"
    fi

    if [ "$INSTALL_LEARNING_BOOK_DEPENDENCIES" = true ]; then
      bash "$PROJECT_SCRIPTS_DEST/Setup-Learning-Book.sh" "$RESOLVED_PROJECT" --install-missing
    else
      bash "$PROJECT_SCRIPTS_DEST/Setup-Learning-Book.sh" "$RESOLVED_PROJECT"
    fi

    if [ "$SKIP_DEVFLOW" = true ]; then
      echo "[SKIP] MAUI DevFlow automatic injection skipped (--skip-devflow)."
    elif [ -f "$PROJECT_SCRIPTS_DEST/Ensure-Maui-DevFlow.sh" ]; then
      DEVFLOW_ARGS=("$RESOLVED_PROJECT")
      if [ "$UPGRADE" = true ]; then
        DEVFLOW_ARGS+=("--upgrade")
      fi
      if [ "$SKIP_CLI" = true ]; then
        DEVFLOW_ARGS+=("--skip-cli")
      fi
      bash "$PROJECT_SCRIPTS_DEST/Ensure-Maui-DevFlow.sh" "${DEVFLOW_ARGS[@]}"
    fi

    echo "Installed MAUI K12 Baton Workflow into project: $RESOLVED_PROJECT"
    ;;
  Codex)
    DEST="$HOME/.codex/skills/maui-k12-baton-workflow"
    replace_dir_clean "$SKILL_SOURCE" "$DEST"
    copy_companion_skill "$HOME/.codex/skills/maui-step-guide-author"
    echo "Installed Codex skill: $DEST"
    ;;
  ClaudeCode)
    DEST="$HOME/.claude/skills/maui-k12-baton-workflow"
    replace_dir_clean "$SKILL_SOURCE" "$DEST"
    copy_companion_skill "$HOME/.claude/skills/maui-step-guide-author"
    echo "Installed Claude Code skill: $DEST"
    echo "Also copy CLAUDE.md or project-template/AGENTS.md into the target project root."
    ;;
  *)
    echo "Usage: ./scripts/Install-Skill.sh [Project|Codex|ClaudeCode] [ProjectPath] [--upgrade] [--install-learning-book-dependencies] [--skip-devflow]" >&2
    exit 1
    ;;
esac
