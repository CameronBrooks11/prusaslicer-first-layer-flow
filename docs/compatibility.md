# Compatibility and Non-Goals

## Compatibility

- PrusaSlicer baseline: `2.9.3+`.
- Uses official custom parameter placeholders introduced in the 2.9.3 release line.
- Expected firmware behavior: `M221` support (common in Marlin/Klipper ecosystems).
- Vendor bundle includes a generic FFF machine baseline and should be adapted to the target printer profile before production use.

## Non-Goals for v1

- No full multi-tool state machine for first-layer flow across complex toolchanges.
- No automatic profile injection utility yet.
- No guarantee for firmware stacks that ignore or reinterpret `M221`.

## Future Work

- Add explicit multi-tool handling semantics.
- Add CI wiring for fixture validation.
- Add optional profile patching helper for bulk rollout.
