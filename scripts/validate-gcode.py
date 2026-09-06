#!/usr/bin/env python3
"""Validate FIRST_LAYER_FLOW_APPLY / FIRST_LAYER_FLOW_RESET M221 values in G-code.

Exit codes:

    0   verified -- the markers are present and the values are the expected ones
    1   wrong    -- the markers are present and a value is not what was expected
    2   could not tell -- no FIRST_LAYER_FLOW_APPLY marker, so the feature never ran
                       and there was nothing to validate
    4   could not read the file named on the command line

2 is the one that exists because of issue #1: it used to be reported as 0, by falling
back to positional M221 matching when the markers were absent. 2 is not a finding about
the print, and a caller must not treat it as one -- the remedy is to fix the printer
profile and re-slice, not to change a flow value.
"""

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


def detect_values(lines: list[str]) -> tuple[int | None, int | None, list[int], bool]:
    """Values that follow the markers, and whether the apply marker was there at all.

    Marker-derived only. An earlier version fell back to "the first M221 in the file"
    and "the second M221" when the markers were absent, which made a print WITHOUT the
    feature installed indistinguishable from one with it: M221 appears routinely in
    ordinary G-code -- filament profiles, purge and prime macros, per-object flow
    tweaks -- so the fallback matched by coincidence and reported OK at exit 0.

    The markers are the contract (README, "Behavior Contract"), every example emits
    them, and no documented case produces G-code without them. So their absence is not
    a gap to paper over with a guess: it is the answer.
    """
    m221_values: list[int] = []
    marker_apply: int | None = None
    marker_reset: int | None = None
    saw_apply_marker = False

    for i, line in enumerate(lines):
        value = parse_m221(line)
        if value is not None:
            m221_values.append(value)

        if APPLY_MARKER in line:
            saw_apply_marker = True
            marker_apply = find_next_m221(lines, i)
        if RESET_MARKER in line:
            marker_reset = find_next_m221(lines, i)

    return marker_apply, marker_reset, m221_values, saw_apply_marker


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
        # 4, not 2. Exit 2 means "the feature was not installed, so nothing was
        # validated" -- a statement about the G-code. A path that is not there is a
        # statement about the invocation, and one code cannot carry both without a
        # caller having to guess which it got.
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 4

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    apply_value, reset_value, all_values, saw_apply_marker = detect_values(lines)

    if args.verbose:
        print(f"Parsed M221 values: {all_values}")
        print(f"Detected apply marker: {saw_apply_marker}")
        print(f"Detected apply value: {apply_value}")
        print(f"Detected reset value: {reset_value}")

    if not saw_apply_marker:
        # Not a finding about the flow values -- there is nothing to find. The feature
        # was never installed in this G-code, so the question this script asks cannot
        # be answered, and saying OK would answer it wrongly in the one direction that
        # matters. Its own exit code, so a caller can tell "not installed" from "installed
        # and wrong": 0 verified, 1 wrong, 2 could not tell.
        print(
            f"NOT INSTALLED: no {APPLY_MARKER} marker in {path.name}; "
            f"the first-layer-flow custom G-code did not run for this print",
            file=sys.stderr,
        )
        print(
            "  hint: check the printer profile's Custom G-code, then re-slice. "
            "This is not a flow-value mismatch -- nothing was validated.",
            file=sys.stderr,
        )
        return 2

    if apply_value is None:
        print(
            f"ERROR: {APPLY_MARKER} marker found, but no M221 follows it",
            file=sys.stderr,
        )
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
