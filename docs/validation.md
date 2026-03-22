# Validation

## Validator CLI

```bash
python3 scripts/validate-gcode.py <file> --expect-first-layer <int> --expect-reset <int> [--allow-missing-reset]
```

## Functional Matrix

1. Parameter absent, baseline 1.00 -> apply `100`, reset `100`.

```bash
python3 scripts/validate-gcode.py examples/gcode/case-01-no-param-baseline-100.gcode --expect-first-layer 100 --expect-reset 100
```

2. Parameter 1.02, baseline 1.00 -> apply `102`, reset `100`.

```bash
python3 scripts/validate-gcode.py examples/gcode/case-02-param-102-baseline-100.gcode --expect-first-layer 102 --expect-reset 100
```

3. Parameter 0.95, baseline 0.98 -> apply `95`, reset `98`.

```bash
python3 scripts/validate-gcode.py examples/gcode/case-03-param-95-baseline-98.gcode --expect-first-layer 95 --expect-reset 98
```

4. One-layer print -> apply present, reset may be absent.

```bash
python3 scripts/validate-gcode.py examples/gcode/case-04-one-layer-param-102.gcode --expect-first-layer 102 --expect-reset 100 --allow-missing-reset
```

## Manual G-code Inspection

Look for:

- `; FIRST_LAYER_FLOW_APPLY` followed by `M221 S...` near print start.
- `; FIRST_LAYER_FLOW_RESET` followed by baseline `M221 S...` after the first layer transition.

## Troubleshooting

- If no apply marker exists in output G-code, confirm Start G-code snippet was appended to the active printer profile.
- If apply value is always baseline, confirm filament custom parameter JSON is valid and in the active filament profile.
- If reset is missing on multi-layer prints, confirm the Before layer change snippet is active and not overridden by another profile.
