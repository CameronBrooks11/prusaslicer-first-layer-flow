#!/usr/bin/env python3
"""Patch an exported PrusaSlicer config INI with first-layer flow snippets.

This script edits only `start_gcode` and `before_layer_gcode` key lines,
preserving all other machine/profile settings from the exported config.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

START_KEY_RE = re.compile(r"^(\s*start_gcode\s*=\s*)(.*)$")
BEFORE_KEY_RE = re.compile(r"^(\s*before_layer_gcode\s*=\s*)(.*)$")

START_MARKER = "FIRST_LAYER_FLOW_APPLY"
BEFORE_MARKER = "FIRST_LAYER_FLOW_RESET"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent


def escaped_snippet(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = text.strip("\n")
    return text.replace("\\", "\\\\").replace("\n", "\\n")


def patch_line(line: str, key_re: re.Pattern[str], marker: str, snippet: str) -> tuple[str, bool]:
    m = key_re.match(line)
    if not m:
        return line, False

    prefix, value = m.group(1), m.group(2)
    if marker in value:
        return line, False

    if value.strip():
        patched = f"{prefix}{value}\\n{snippet}"
    else:
        patched = f"{prefix}{snippet}"
    return patched, True


def patch_text(text: str, start_snip: str, before_snip: str) -> tuple[str, bool, bool]:
    lines = text.splitlines()

    start_found = False
    before_found = False
    start_changed = False
    before_changed = False

    out_lines: list[str] = []
    for line in lines:
        patched = line

        new_line, changed = patch_line(patched, START_KEY_RE, START_MARKER, start_snip)
        if new_line != patched:
            start_found = True
            start_changed = changed
            patched = new_line
        elif START_KEY_RE.match(patched):
            start_found = True

        new_line, changed = patch_line(patched, BEFORE_KEY_RE, BEFORE_MARKER, before_snip)
        if new_line != patched:
            before_found = True
            before_changed = changed
            patched = new_line
        elif BEFORE_KEY_RE.match(patched):
            before_found = True

        out_lines.append(patched)

    if not start_found:
        out_lines.append(f"start_gcode = {start_snip}")
        start_changed = True
    if not before_found:
        out_lines.append(f"before_layer_gcode = {before_snip}")
        before_changed = True

    trailing_nl = "\n" if text.endswith("\n") else ""
    return "\n".join(out_lines) + trailing_nl, start_changed, before_changed


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="patch-config",
        description="Patch exported PrusaSlicer config with first-layer flow snippets safely.",
    )
    parser.add_argument("--input", required=True, help="Path to exported PrusaSlicer config INI")
    parser.add_argument("--output", help="Output path (omit with --in-place)")
    parser.add_argument("--in-place", action="store_true", help="Modify input file in place")
    args = parser.parse_args()

    if args.in_place and args.output:
        print("ERROR: use either --output or --in-place, not both", file=sys.stderr)
        return 2
    if not args.in_place and not args.output:
        print("ERROR: provide --output or use --in-place", file=sys.stderr)
        return 2

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        return 2

    start_path = REPO_ROOT / "gcode" / "start.gcode"
    before_path = REPO_ROOT / "gcode" / "before-layer-change.gcode"
    if not start_path.is_file() or not before_path.is_file():
        print(
            f"ERROR: expected snippet files not found at {start_path} and/or {before_path}",
            file=sys.stderr,
        )
        return 2

    start_snip = escaped_snippet(start_path)
    before_snip = escaped_snippet(before_path)

    original = input_path.read_text(encoding="utf-8", errors="replace")
    patched, start_changed, before_changed = patch_text(original, start_snip, before_snip)

    out_path = input_path if args.in_place else Path(args.output)
    out_path.write_text(patched, encoding="utf-8")

    print(
        f"OK: wrote {out_path} (start_gcode {'patched' if start_changed else 'already had marker'}, "
        f"before_layer_gcode {'patched' if before_changed else 'already had marker'})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
