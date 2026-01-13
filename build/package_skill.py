#!/usr/bin/env python3
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""
Skill Packager - Copies skill folder to dist directory with exclusions

Usage:
    uv run build/package_skill.py <skill-folder>

Example:
    uv run build/package_skill.py skill-name
"""

import argparse
import fnmatch
import re
import shutil
import sys
from pathlib import Path

# Ensure we can import from the same directory
if str(Path(__file__).parent) not in sys.path:
    sys.path.append(str(Path(__file__).parent))

from quick_validate import validate_skill

# Output directory configuration
OUTPUT_DIR = "skill-test/.claude/skills/"

# Files and directories to exclude from packaging
EXCLUDE_PATTERNS = {
    # Environment files
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    ".env.test",
    # Version control
    ".git",
    ".gitignore",
    ".gitattributes",
    # Python
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    "venv",
    "env",
    ".venv",
    "pyproject.toml",
    "uv.lock",
    ".python-version",
    # Node.js
    "node_modules",
    "package-lock.json",
    "yarn.lock",
    # IDE and editors
    ".vscode",
    ".idea",
    ".DS_Store",
    "*.swp",
    "*.swo",
    "*~",
    # Build artifacts
    "dist",
    "build",
    "*.egg-info",
    # Logs
    "*.log",
    "logs",
    # Temporary files
    ".tmp",
    "tmp",
    "*.tmp",
    "*.bak",
    "*.cache",
    # Documentation
    "AGENTS.md",
    "README.md",
    "readme.md",
    "INDEX.md",
}

# Pre-compile wildcard patterns for better performance
WILDCARD_PATTERNS = [
    re.compile(fnmatch.translate(pattern))
    for pattern in EXCLUDE_PATTERNS
    if "*" in pattern
]

EXACT_PATTERNS = {pattern for pattern in EXCLUDE_PATTERNS if "*" not in pattern}


def should_exclude(file_path, skill_root):
    """
    Check if a file should be excluded from packaging.

    Args:
        file_path: Path object of the file to check
        skill_root: Path object of the skill root directory

    Returns:
        True if file should be excluded, False otherwise
    """
    # Get relative path parts
    rel_path = file_path.relative_to(skill_root)
    path_parts = rel_path.parts

    # Check each part of the path against exact patterns
    for part in path_parts:
        if part in EXACT_PATTERNS:
            return True
        # Check wildcard patterns using pre-compiled regex
        for pattern in WILDCARD_PATTERNS:
            if pattern.match(part):
                return True

    # Check the full relative path against wildcard patterns
    rel_path_str = str(rel_path)
    for pattern in WILDCARD_PATTERNS:
        if pattern.match(rel_path_str):
            return True

    return False


def package_skill(skill_path, output_dir=None, verbose=False):
    """
    Package a skill folder to output directory.

    Args:
        skill_path: Path to the skill folder
        output_dir: Output directory (defaults to OUTPUT_DIR constant)
        verbose: If True, print detailed file operations

    Returns:
        Path to the created skill folder, or None if error
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"❌ Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return None

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        return None

    # Run validation before packaging
    print("🔍 Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"✅ {message}\n")

    # Determine output location
    if output_dir is None:
        output_dir = OUTPUT_DIR
    skill_name = skill_path.name
    output_path = Path(output_dir).resolve()
    skill_output = output_path / skill_name

    # Remove existing output if it exists
    if skill_output.exists():
        print(f"🗑️  Removing existing output: {skill_output}")
        shutil.rmtree(skill_output)

    # Create output directory
    skill_output.mkdir(parents=True, exist_ok=True)

    # Copy files
    try:
        files_added = 0
        files_excluded = 0

        print(f"📦 Copying files to {skill_output}\n")

        # Walk through the skill directory
        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                # Check if file should be excluded
                if should_exclude(file_path, skill_path):
                    files_excluded += 1
                    if verbose:
                        print(f"  ⊘ Excluded: {file_path.relative_to(skill_path)}")
                    continue

                # Calculate the relative path and destination
                rel_path = file_path.relative_to(skill_path)
                dest_path = skill_output / rel_path

                # Create parent directories if needed
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                # Copy file
                shutil.copy2(file_path, dest_path)

                files_added += 1
                if verbose:
                    print(f"  ✓ Copied: {rel_path}")

        print("\n📊 Summary:")
        print(f"   Files copied: {files_added}")
        print(f"   Files excluded: {files_excluded}")
        print(f"\n✅ Successfully packaged skill to: {skill_output}")
        return skill_output

    except Exception as e:
        print(f"❌ Error copying files: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Package a skill folder to output directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run build/package_skill.py stock-analysis
  uv run build/package_skill.py stock-analysis -v
        """,
    )

    parser.add_argument("skill_path", help="Path to the skill folder to package")

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed output for each file operation",
    )

    args = parser.parse_args()

    print(f"📦 Packaging skill to ./{OUTPUT_DIR}")
    print(f"   Source: {args.skill_path}\n")

    result = package_skill(args.skill_path, verbose=args.verbose)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
