#!/usr/bin/env bash
# Regression tests for validate-gcode.py.
#
# Plain bash on purpose: this repo ships scripts, not a package, and a test
# runner would be more infrastructure than the thing it tests.
#
# The case that matters is NOT INSTALLED. Before issue #1 the validator fell
# back to "the first M221 in the file" when the markers were absent, so a print
# without the feature reported `OK ... exit 0` -- byte-identical to a print with
# it. Everything else here is a control: without them, a validator that returned
# 2 unconditionally would pass this file.

set -uo pipefail
cd "$(dirname "$0")/.."

VALIDATE="python3 scripts/validate-gcode.py"
EXAMPLES="examples/gcode"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fails=0

expect() {
    local want="$1" desc="$2"; shift 2
    local out; out="$("$@" 2>&1)"; local got=$?
    if [ "$got" = "$want" ]; then
        printf '  ok    exit %s  %s\n' "$got" "$desc"
    else
        printf '  FAIL  exit %s, wanted %s  %s\n    %s\n' "$got" "$want" "$desc" "${out%%$'\n'*}"
        fails=$((fails + 1))
    fi
}

# The defect: markers absent, but two ordinary M221s that happen to match.
cat > "$TMP/nofeature.gcode" <<'GCODE'
; START
M221 S102
G28
G1 X10 Y10 Z0.2 F1800
;LAYER_CHANGE
M221 S100
G1 X20 Y20 E1.2
GCODE

# Markers absent and no M221 at all -- must give the same answer, for the same reason.
printf '; START\nG28\nG1 X10 Y10 Z0.2 F1800\n' > "$TMP/bare.gcode"

# The apply marker with nothing following it: installed, and broken.
printf '; START\n; FIRST_LAYER_FLOW_APPLY\nG28\n' > "$TMP/marker-no-m221.gcode"

echo "not installed (2)"
expect 2 "markers absent, two coincidental M221s" \
    $VALIDATE "$TMP/nofeature.gcode" --expect-first-layer 102 --expect-reset 100
expect 2 "markers absent, no M221 at all" \
    $VALIDATE "$TMP/bare.gcode" --expect-first-layer 102 --expect-reset 100

echo "installed and wrong (1)"
expect 1 "apply marker present, no M221 follows it" \
    $VALIDATE "$TMP/marker-no-m221.gcode" --expect-first-layer 102 --expect-reset 100
expect 1 "no param set, so apply is the baseline" \
    $VALIDATE "$EXAMPLES/case-01-no-param-baseline-100.gcode" --expect-first-layer 102 --expect-reset 100
expect 1 "values present but not the expected ones" \
    $VALIDATE "$EXAMPLES/case-02-param-102-baseline-100.gcode" --expect-first-layer 95 --expect-reset 98

echo "verified (0)"
expect 0 "param 102, baseline 100" \
    $VALIDATE "$EXAMPLES/case-02-param-102-baseline-100.gcode" --expect-first-layer 102 --expect-reset 100
expect 0 "param 95, baseline 98" \
    $VALIDATE "$EXAMPLES/case-03-param-95-baseline-98.gcode" --expect-first-layer 95 --expect-reset 98
expect 0 "one-layer print, reset legitimately absent" \
    $VALIDATE "$EXAMPLES/case-04-one-layer-param-102.gcode" --expect-first-layer 102 --expect-reset 100 --allow-missing-reset

# 4, not 2, and this assertion is why: the first version of this fix returned 2 for
# both, so a caller could not tell "the feature never ran" from "you gave me a bad
# path". One code, two meanings, found by running this file.
echo "could not read the input (4)"
expect 4 "file that does not exist" \
    $VALIDATE "$TMP/nope.gcode" --expect-first-layer 102 --expect-reset 100

if [ "$fails" -eq 0 ]; then echo "all passed"; else echo "$fails failed"; fi
exit $((fails > 0))
