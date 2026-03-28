#!/usr/bin/env bash
set -euo pipefail

# Install codebase-docs-expert command and agent into the current project.
#
# Assumes this script lives at:
#   ~/.claude/skills/codebase-docs-expert/scripts/install.sh
#   OR
#   .claude/skills/codebase-docs-expert/scripts/install.sh
#
# Usage:
#   bash ~/.claude/skills/codebase-docs-expert/scripts/install.sh [target-dir]
#
# If target-dir is omitted, installs to the current working directory.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET_DIR="${1:-.}"

echo "Installing codebase-docs-expert artifacts..."
echo "  Skill directory: $SKILL_DIR"
echo "  Target project:  $(cd "$TARGET_DIR" && pwd)"

# Create target directories
mkdir -p "$TARGET_DIR/.claude/commands"
mkdir -p "$TARGET_DIR/.claude/agents"

# Install the orchestrator command
if [ -f "$SKILL_DIR/assets/commands/analyze-codebase.md" ]; then
    cp "$SKILL_DIR/assets/commands/analyze-codebase.md" "$TARGET_DIR/.claude/commands/analyze-codebase.md"
    echo "  Installed: .claude/commands/analyze-codebase.md"
else
    echo "  ERROR: analyze-codebase.md not found in $SKILL_DIR/assets/commands/"
    exit 1
fi

# Install the analysis worker agent
if [ -f "$SKILL_DIR/assets/agents/codebase-analyzer.md" ]; then
    cp "$SKILL_DIR/assets/agents/codebase-analyzer.md" "$TARGET_DIR/.claude/agents/codebase-analyzer.md"
    echo "  Installed: .claude/agents/codebase-analyzer.md"
else
    echo "  ERROR: codebase-analyzer.md not found in $SKILL_DIR/assets/agents/"
    exit 1
fi

echo ""
echo "Installation complete. You can now run:"
echo "  /analyze-codebase"
echo ""
echo "This will create .claude/skills/site-context/ with 14 analysis reference files."
