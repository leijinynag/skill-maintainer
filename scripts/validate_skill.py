#!/usr/bin/env python3
"""Small repository-local validator for the skill package."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.path).resolve()
    skill = root / "SKILL.md"
    if not skill.exists():
        print("error: SKILL.md not found", file=sys.stderr)
        return 2
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---" not in text[4:]:
        print("error: invalid frontmatter", file=sys.stderr)
        return 1
    frontmatter = text[4 : text.find("\n---", 4)]
    fields = dict(
        match.groups()
        for match in (re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line) for line in frontmatter.splitlines())
        if match
    )
    if fields.get("name") != root.name:
        print(f"error: name {fields.get('name')!r} does not match {root.name!r}", file=sys.stderr)
        return 1
    if not fields.get("description"):
        print("error: description is missing", file=sys.stderr)
        return 1
    if not re.fullmatch(r"[a-z0-9-]{1,63}", fields["name"]):
        print("error: invalid skill name", file=sys.stderr)
        return 1
    print(f"valid: {fields['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
