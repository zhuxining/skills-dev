#!/usr/bin/env python3
"""
Skill Packager - Copies skill folder to dist directory with exclusions

Usage:
    python build/package_skill.py <skill-folder>

Example:
    python build/package_skill.py skill-name
"""

import sys
import shutil
import re
import fnmatch
from pathlib import Path


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
}


def validate_skill(skill_path):
    """
    Basic validation of a skill (simplified, no YAML parsing).

    Args:
        skill_path: Path to the skill folder

    Returns:
        Tuple of (bool, str) - (is_valid, message)
    """
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Simple check for required fields (without full YAML parsing)
    has_name = re.search(r"^\s*name\s*:", frontmatter_text, re.MULTILINE)
    has_description = re.search(r"^\s*description\s*:", frontmatter_text, re.MULTILINE)

    if not has_name:
        return False, "Missing 'name' in frontmatter"
    if not has_description:
        return False, "Missing 'description' in frontmatter"

    return True, "Skill is valid!"


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

    # Check each part of the path
    for part in path_parts:
        if part in EXCLUDE_PATTERNS:
            return True
        # Check wildcard patterns
        for pattern in EXCLUDE_PATTERNS:
            if "*" in pattern:
                if fnmatch.fnmatch(part, pattern):
                    return True

    # Check the full relative path
    rel_path_str = str(rel_path)
    for pattern in EXCLUDE_PATTERNS:
        if "*" in pattern:
            if fnmatch.fnmatch(rel_path_str, pattern):
                return True

    return False


def package_skill(skill_path, output_dir="dist"):
    """
    Package a skill folder to output directory.

    Args:
        skill_path: Path to the skill folder
        output_dir: Output directory (defaults to 'dist')

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
                print(f"  ✓ Copied: {rel_path}")

        print(f"\n📊 Summary:")
        print(f"   Files copied: {files_added}")
        print(f"   Files excluded: {files_excluded}")
        print(f"\n✅ Successfully packaged skill to: {skill_output}")
        return skill_output

    except Exception as e:
        print(f"❌ Error copying files: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python build/package_skill.py <skill-folder>")
        print("\nExample:")
        print("  python build/package_skill.py skill-name")
        sys.exit(1)

    skill_path = sys.argv[1]

    print(f"📦 Packaging skill to ./dist/")
    print(f"   Source: {skill_path}\n")

    result = package_skill(skill_path)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
