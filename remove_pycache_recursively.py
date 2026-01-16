#!/usr/binc/env python3
"""
Recursively find and delete all __pycache__ directories.

Usage:
    python remove_pycache_recursively.py
    python remove_pycache_recursively.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

# Directories to skip when searching for __pycache__
SKIP_DIRS = {
    ".venv",
    "venv",
    "env",
    ".git",
    "node_modules",
    "build",
    "dist",
    ".eggs",
    "*.egg-info",
}


def find_pycache_dirs(root_dir: Path) -> list[Path]:
    """Find all __pycache__ directories under root_dir."""
    pycache_dirs = []

    for dirpath, dirnames, _ in os.walk(root_dir):
        # Convert to Path for easier manipulation
        current_path = Path(dirpath)

        # Skip certain directories by modifying dirnames in-place
        # This prevents os.walk from descending into them
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not d.startswith(".")
        ]

        # Check if __pycache__ is in the current directory's subdirectories
        if "__pycache__" in dirnames:
            pycache_path = current_path / "__pycache__"
            pycache_dirs.append(pycache_path)

    return pycache_dirs


def format_size(path: Path) -> str:
    """Get human-readable size of a directory."""
    total_size = 0
    try:
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                if filepath.exists():
                    total_size += filepath.stat().st_size
    except (OSError, PermissionError):
        return "N/A"
    return _human_readable_size(total_size)


def _human_readable_size(size: int) -> str:
    """Convert bytes to human-readable format."""
    if size == 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recursively find and delete __pycache__ directories."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List directories without deleting them",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory to search (default: current working directory)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show all directories (not just count)",
    )
    args = parser.parse_args()

    root_dir = args.root.resolve()
    print(f"Searching for __pycache__ directories under: {root_dir}")
    print(f"(Skipping: {', '.join(sorted(SKIP_DIRS))})")
    print()

    pycache_dirs = find_pycache_dirs(root_dir)

    if not pycache_dirs:
        print("No __pycache__ directories found.")
        return

    # Make paths relative to root for cleaner display
    relative_dirs = [d.relative_to(root_dir) for d in pycache_dirs]

    print(f"Found {len(relative_dirs)} __pycache__ directory(ies):\n")

    for i, rel_path in enumerate(relative_dirs, 1):
        full_path = root_dir / rel_path
        size_str = format_size(full_path)
        if args.verbose:
            print(f"  [{i:3d}] {rel_path}/  ({size_str})")
        else:
            print(f"  {rel_path}/  ({size_str})")

    if args.dry_run:
        print("\n[Dry run] No directories were deleted.")
    else:
        print("\nDeleting...")
        deleted = 0
        for pycache_dir in pycache_dirs:
            try:
                shutil.rmtree(pycache_dir)
                deleted += 1
            except (OSError, PermissionError) as e:
                print(f"  Warning: Could not delete {pycache_dir}: {e}")
        print(f"Successfully deleted {deleted}/{len(pycache_dirs)} directory(ies).")


if __name__ == "__main__":
    main()
