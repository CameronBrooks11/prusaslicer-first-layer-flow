# PrusaSlicer First Layer Flow

Small PrusaSlicer helper to apply extra flow on layer 1 only, then restore normal flow.

## Quick Start (Recommended)

1. In `Printer Settings -> Custom G-code -> Start G-code`, append contents of `gcode/start.gcode`.
2. In `Printer Settings -> Custom G-code -> Before layer change G-code`, append contents of `gcode/before-layer-change.gcode`.
3. In your active filament profile (`Filament Settings -> Custom G-code -> Custom parameters`), add:

```json
{
  "first_layer_extrusion_multiplier": 1.02
}
```

4. Slice and verify your output G-code contains:

- `; FIRST_LAYER_FLOW_APPLY` near start, followed by `M221 S...`
- `; FIRST_LAYER_FLOW_RESET` after first layer, followed by baseline `M221 S...`

## Validate with Script

```bash
python3 scripts/validate-gcode.py /path/to/output.gcode --expect-first-layer 102 --expect-reset 100
```

For one-layer prints:

```bash
python3 scripts/validate-gcode.py /path/to/output.gcode --expect-first-layer 102 --expect-reset 100 --allow-missing-reset
```

## Behavior Contract

- Custom parameter key: `first_layer_extrusion_multiplier`
- Start logic:
  Parameter exists -> `M221 S{custom * 100}`
  Parameter missing -> `M221 S{extrusion_multiplier * 100}`
- Before-layer-change logic:
  At `layer_num == 1` -> restore baseline `M221 S{extrusion_multiplier * 100}`

## Safe Patch Workflow (Optional)

If you prefer patching an exported config instead of manual copy/paste:

1. In PrusaSlicer: `File -> Export -> Export Config`
2. Run:

```bash
python3 scripts/patch-config.py --input /path/to/exported.ini --output /path/to/exported.patched.ini
```

3. Import the patched file.

## Advanced Artifacts (Optional)

Most users can ignore this section.

- `presets/vendor/FirstLayerFlow.ini` + `presets/vendor/FirstLayerFlow.idx`
  Vendor-bundle style packaging with a generic Marlin baseline (`250x210`).
- `presets/simple/first-layer-flow-config.ini`
  Minimal patch asset (`start_gcode` + `before_layer_gcode` only). Depending on import flow, direct import may replace active config state.

## Compatibility and Scope

- PrusaSlicer: `>= 2.9.3`
- Uses official custom parameter placeholders introduced in 2.9.3
- Assumes firmware supports `M221` (Marlin/Klipper style)
- v1 support target: single-extruder profiles

## Troubleshooting

- No apply marker in G-code: start snippet is not active on the current printer profile.
- Apply value stays baseline: custom parameter JSON missing/invalid in the active filament profile.
- Reset missing on multi-layer print: before-layer-change snippet missing/overridden.

## Upstream References

- Release notes (custom parameters): https://github.com/prusa3d/PrusaSlicer/releases
- Macro docs: https://help.prusa3d.com/article/macros_1775
- Placeholder list: https://help.prusa3d.com/article/list-of-placeholders_205643
- Vendor bundle/index semantics: https://github.com/prusa3d/PrusaSlicer/wiki/Vendor-bundles-and-updating-process
