#!/usr/bin/env python3
"""
install.py — Install wiki:* commands into a Claude Code project.

Copies the generic wiki commands (ingest, status, consolidate) from this skill's
commands/ directory into the target project's .claude/commands/wiki/ directory,
making them available as /wiki:ingest, /wiki:status, and /wiki:consolidate.

Usage:
    python3 install.py                      # install into current directory
    python3 install.py /path/to/project     # install into specified project root
    python3 install.py --dry-run            # preview what would be copied
"""

import argparse
import shutil
import sys
from pathlib import Path

COMMANDS = ["ingest.md", "status.md", "consolidate.md"]


def main():
    parser = argparse.ArgumentParser(description="Install wiki:* commands into a Claude Code project")
    parser.add_argument("project_root", nargs="?", default=".", help="Project root directory (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without copying")
    args = parser.parse_args()

    # Resolve paths
    skill_dir = Path(__file__).parent.parent  # .claude/skills/wiki/
    commands_src = skill_dir / "commands"
    project_root = Path(args.project_root).resolve()
    commands_dst = project_root / ".claude" / "commands" / "wiki"

    # Validate source
    if not commands_src.exists():
        print(f"ERROR: commands/ directory not found at {commands_src}", file=sys.stderr)
        sys.exit(1)

    missing = [f for f in COMMANDS if not (commands_src / f).exists()]
    if missing:
        print(f"ERROR: missing command files: {missing}", file=sys.stderr)
        sys.exit(1)

    # Validate target project
    if not project_root.exists():
        print(f"ERROR: project root not found: {project_root}", file=sys.stderr)
        sys.exit(1)

    dot_claude = project_root / ".claude"
    if not dot_claude.exists():
        print(f"WARNING: no .claude/ directory found at {project_root}")
        print("         Is this a Claude Code project? Continuing anyway.")

    # Show plan
    print(f"Source : {commands_src}")
    print(f"Target : {commands_dst}")
    print()

    results = []
    for filename in COMMANDS:
        src = commands_src / filename
        dst = commands_dst / filename
        status = "overwrite" if dst.exists() else "new"
        command_name = f"/wiki:{filename.removesuffix('.md')}"
        results.append((command_name, src, dst, status))
        print(f"  {'[dry-run] ' if args.dry_run else ''}{status:9s}  {command_name}  →  {dst}")

    if args.dry_run:
        print("\nDry run — no files written.")
        return

    print()
    commands_dst.mkdir(parents=True, exist_ok=True)
    for command_name, src, dst, status in results:
        shutil.copy2(src, dst)
        print(f"  ✓ {command_name}")

    print(f"\nInstalled {len(COMMANDS)} commands into {commands_dst}")
    print("Restart Claude Code for the commands to appear.")


if __name__ == "__main__":
    main()
