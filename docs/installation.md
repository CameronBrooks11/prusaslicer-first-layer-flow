# Installation

## Option A: Import Config (Primary)

1. Open PrusaSlicer.
2. Go to `File -> Import -> Import Config`.
3. Import `presets/simple/first-layer-flow-config.ini`.
4. Open your filament profile:
- `Filament Settings -> Custom G-code -> Custom parameters`
- Insert JSON from `presets/filament-custom-parameters.example.json`.
5. Save profile.

## Option B: Vendor Bundle Pair (Secondary)

1. Copy both files to your PrusaSlicer vendor directory:
- `presets/vendor/FirstLayerFlow.ini`
- `presets/vendor/FirstLayerFlow.idx`
2. Restart PrusaSlicer.
3. Install/select the profile through the configuration workflow for vendor profiles.
4. Copy the `start_gcode` and `before_layer_gcode` logic into your actual printer preset if your machine geometry/limits differ.

## Option C: Manual fallback

1. Append `gcode/start.gcode` to `Printer Settings -> Custom G-code -> Start G-code`.
2. Append `gcode/before-layer-change.gcode` to `Printer Settings -> Custom G-code -> Before layer change G-code`.
3. Add custom parameter JSON from `presets/filament-custom-parameters.example.json` to filament custom parameters.

## Notes

- Keep the parameter key exactly: `first_layer_extrusion_multiplier`.
- Do not rename marker comments unless you also update `scripts/validate-gcode.py`.
- The vendor bundle ships with a generic Marlin-style machine baseline for portability, not a tuned machine-specific profile.
