# PrusaSlicer First Layer Flow

First-layer-only flow override for PrusaSlicer using filament custom parameters and G-code.

## Baseline and Scope

- PrusaSlicer: `>= 2.9.3`
- Canonical custom parameter key: `first_layer_extrusion_multiplier`
- Firmware expectation: supports `M221` (Marlin/Klipper style)
- v1 guaranteed scope: single-extruder profiles

## Public Interface

- Filament custom parameter key: `first_layer_extrusion_multiplier`
- Type: numeric (example `1.05`)
- Placeholder form: `custom_parameter_filament_first_layer_extrusion_multiplier[...]`

## G-code Contract

1. Start stage (`gcode/start.gcode`)

- If custom parameter exists: emit `M221 S{custom * 100}`
- If missing: emit `M221 S{extrusion_multiplier * 100}`
- Marker: `FIRST_LAYER_FLOW_APPLY`

2. Before layer change stage (`gcode/before-layer-change.gcode`)

- At `layer_num == 1`: emit baseline restore `M221 S{extrusion_multiplier * 100}`
- Marker: `FIRST_LAYER_FLOW_RESET`

## Installation

### Option A (Recommended): Manual snippet copy

1. Append `gcode/start.gcode` to `Printers -> Custom G-code -> Start G-code`.
2. Append `gcode/before-layer-change.gcode` to `Printers -> Custom G-code -> Before layer change G-code`.
3. In your active filament profile (`Filament Settings -> Custom G-code -> Custom parameters`), insert:

```json
{
  "first_layer_extrusion_multiplier": 1.05
}
```

### Option B: Patch your exported config safely

This avoids replacing your machine/profile config.

1. In PrusaSlicer, export your current config (`File -> Export -> Export Config`).
2. Patch it:

```bash
python3 scripts/patch-config.py --input /path/to/exported.ini --output /path/to/exported.patched.ini
```

3. Import the patched file in PrusaSlicer.
4. Add filament custom parameter JSON (above) in your active filament profile.

## Preset Artifacts (Advanced/Integrators)

- `presets/vendor/FirstLayerFlow.ini` + `presets/vendor/FirstLayerFlow.idx`
  Vendor-bundle style packaging. Generic Marlin-style baseline (`250x210` bed); copy flow logic into your real machine profile before production.
- `presets/simple/first-layer-flow-config.ini`
  Minimal patch asset (only `start_gcode` + `before_layer_gcode`). Direct import may replace active config state depending on import flow.

For normal use, prefer Installation Option A or B.

## Validation

### Validator CLI

```bash
python3 scripts/validate-gcode.py <file> --expect-first-layer <int> --expect-reset <int> [--allow-missing-reset]
```

### Functional Matrix

1. No custom parameter, baseline `1.00` -> apply `100`, reset `100`

```bash
python3 scripts/validate-gcode.py examples/gcode/case-01-no-param-baseline-100.gcode --expect-first-layer 100 --expect-reset 100
```

2. Custom `1.05`, baseline `1.00` -> apply `102`, reset `100`

```bash
python3 scripts/validate-gcode.py examples/gcode/case-02-param-102-baseline-100.gcode --expect-first-layer 102 --expect-reset 100
```

3. Custom `0.95`, baseline `0.98` -> apply `95`, reset `98`

```bash
python3 scripts/validate-gcode.py examples/gcode/case-03-param-95-baseline-98.gcode --expect-first-layer 95 --expect-reset 98
```

4. One-layer print -> apply present, reset may be absent

```bash
python3 scripts/validate-gcode.py examples/gcode/case-04-one-layer-param-102.gcode --expect-first-layer 102 --expect-reset 100 --allow-missing-reset
```

### Manual G-code Checks

- `; FIRST_LAYER_FLOW_APPLY` appears near print start, followed by `M221 S...`
- `; FIRST_LAYER_FLOW_RESET` appears after first layer on multi-layer prints, followed by baseline `M221 S...`

### Troubleshooting

- No apply marker: start snippet not active on current printer profile.
- Apply always baseline: custom parameter JSON missing/invalid in current filament profile.
- Reset missing on multi-layer print: before-layer-change snippet missing/overridden.

## Compatibility, Non-Goals, Future Work

### Compatibility

- PrusaSlicer `2.9.3+`
- Uses official custom parameter placeholders from 2.9.3 release line
- Assumes firmware supports `M221`

### Upstream References

- Custom parameters in 2.9.3 release notes: https://github.com/prusa3d/PrusaSlicer/releases
- Prusa macro language / placeholders: https://help.prusa3d.com/article/macros_1775
- Placeholder availability (`layer_num`, etc.): https://help.prusa3d.com/article/list-of-placeholders_205643
- Vendor bundle and index semantics: https://github.com/prusa3d/PrusaSlicer/wiki/Vendor-bundles-and-updating-process

### Non-Goals (v1)

- Full multi-tool state machine across complex toolchanges
- Automatic profile injection utility
- Support guarantees for firmware stacks that ignore/reinterpret `M221`

### Future Work

- Explicit multi-tool handling semantics
- CI validation wiring for fixture matrix
- Bulk profile patch helper improvements
