#!/usr/bin/env python3
"""Validate FIRST_LAYER_FLOW_APPLY / FIRST_LAYER_FLOW_RESET M221 values in G-code."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

M221_RE = re.compile(r"\bM221\b[^;\n]*\bS(-?\d+(?:\.\d+)?)", re.IGNORECASE)
APPLY_MARKER = "FIRST_LAYER_FLOW_APPLY"
RESET_MARKER = "FIRST_LAYER_FLOW_RESET"


def parse_m221(line: str) -> int | None:
    match = M221_RE.search(line)
    if not match:
        return None
    value = float(match.group(1))
    return int(round(value))


def find_next_m221(lines: list[str], start_idx: int) -> int | None:
    for idx in range(start_idx + 1, len(lines)):
        value = parse_m221(lines[idx])
        if value is not None:
            return value
    return None


def detect_values(lines: list[str]) -> tuple[int | None, int | None, list[int]]:
    m221_values: list[int] = []
    marker_apply: int | None = None
    marker_reset: int | None = None

    for i, line in enumerate(lines):
        value = parse_m221(line)
        if value is not None:
            m221_values.append(value)

        if APPLY_MARKER in line:
            marker_apply = find_next_m221(lines, i)
        if RESET_MARKER in line:
            marker_reset = find_next_m221(lines, i)

    apply_value = marker_apply if marker_apply is not None else (m221_values[0] if len(m221_values) >= 1 else None)
    reset_value = marker_reset if marker_reset is not None else (m221_values[1] if len(m221_values) >= 2 else None)

    return apply_value, reset_value, m221_values


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="validate-gcode",
        description="Validate first-layer flow M221 apply/reset values.",
    )
    parser.add_argument("file", help="Path to G-code file")
    parser.add_argument("--expect-first-layer", type=int, required=True, help="Expected M221 S value at apply")
    parser.add_argument("--expect-reset", type=int, required=True, help="Expected M221 S value at reset")
    parser.add_argument(
        "--allow-missing-reset",
        action="store_true",
        help="Allow missing reset command (intended for one-layer prints).",
    )
    parser.add_argument("--verbose", action="store_true", help="Print parsed values for debugging")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    apply_value, reset_value, all_values = detect_values(lines)

    if args.verbose:
        print(f"Parsed M221 values: {all_values}")
        print(f"Detected apply value: {apply_value}")
        print(f"Detected reset value: {reset_value}")

    if apply_value is None:
        print("ERROR: could not detect FIRST_LAYER_FLOW apply M221 command", file=sys.stderr)
        return 1

    if apply_value != args.expect_first_layer:
        print(
            f"ERROR: apply mismatch (expected {args.expect_first_layer}, got {apply_value})",
            file=sys.stderr,
        )
        return 1

    if reset_value is None:
        if args.allow_missing_reset:
            print(
                f"OK: apply={apply_value}, reset=<missing allowed>, expected reset={args.expect_reset}"
            )
            return 0
        print("ERROR: could not detect FIRST_LAYER_FLOW reset M221 command", file=sys.stderr)
        return 1

    if reset_value != args.expect_reset:
        print(
            f"ERROR: reset mismatch (expected {args.expect_reset}, got {reset_value})",
            file=sys.stderr,
        )
        return 1

    print(f"OK: apply={apply_value}, reset={reset_value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
