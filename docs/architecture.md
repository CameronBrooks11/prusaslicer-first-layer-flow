# Architecture and Behavior Contract

## Public Interface

- Filament custom parameter key: `first_layer_extrusion_multiplier`
- Expected type: number (example `1.02`)
- Placeholder used in G-code: `custom_parameter_filament_first_layer_extrusion_multiplier[...]`

## G-code Contract

1. Start stage (`gcode/start.gcode`):
- If custom parameter exists, emit `M221 S{custom * 100}`.
- If missing, emit `M221 S{extrusion_multiplier * 100}` fallback.
- Marker comment: `FIRST_LAYER_FLOW_APPLY`.

2. Before-layer-change stage (`gcode/before-layer-change.gcode`):
- When `layer_num == 1`, emit baseline restore `M221 S{extrusion_multiplier * 100}`.
- Marker comment: `FIRST_LAYER_FLOW_RESET`.

## Scope for v1

- Guaranteed: single-extruder profiles.
- Not guaranteed in v1: robust multi-tool first-layer orchestration across toolchanges.
