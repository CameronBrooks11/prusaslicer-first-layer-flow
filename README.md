# PrusaSlicer First Layer Flow

Importable PrusaSlicer extension that applies a first-layer-only flow override using filament custom parameters and restores baseline flow after layer 1.

## Baseline

- PrusaSlicer: `>= 2.9.3`
- Canonical custom parameter key: `first_layer_extrusion_multiplier`
- Firmware expectation: supports `M221` (Marlin/Klipper style)
- v1 official scope: single-extruder profiles

## Quick Install

### Option A (Primary): simple config import

1. Open PrusaSlicer.
2. Use `File -> Import -> Import Config`.
3. Import `presets/simple/first-layer-flow-config.ini`.
4. Add filament custom parameter JSON from `presets/filament-custom-parameters.example.json` in Filament Settings -> Custom G-code -> Custom parameters.

### Option B (Secondary): vendor bundle files

Use `presets/vendor/FirstLayerFlow.ini` and `presets/vendor/FirstLayerFlow.idx` as a vendor bundle pair.
The bundled printer profile uses a generic Marlin-style baseline (`250x210` bed), so copy the first-layer flow logic into your real machine profile before production prints.

See `docs/installation.md` for exact steps.

### Option C: manual snippet copy

- Start G-code snippet: `gcode/start.gcode`
- Before layer change snippet: `gcode/before-layer-change.gcode`

## Validation Quick Check

Run the validator script on sample fixtures:

```bash
python3 scripts/validate-gcode.py examples/gcode/case-02-param-102-baseline-100.gcode --expect-first-layer 102 --expect-reset 100
```

Full matrix and troubleshooting: `docs/validation.md`.

## Docs

- `docs/architecture.md`
- `docs/installation.md`
- `docs/validation.md`
- `docs/compatibility.md`
