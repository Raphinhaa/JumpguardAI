# Measurement Debug Mode

Prompt 23 adds a developer-only diagnostic viewer for scientific verification of the existing uploaded-video biomechanics pipeline.

## Scope

Measurement Debug Mode is strictly additive. It does not modify:

- MediaPipe landmark extraction,
- pose estimation,
- joint-angle mathematics,
- feature extraction algorithms,
- delta calculations,
- symmetry calculations,
- biomechanical computations,
- clinician workstation behavior,
- existing CSV/JSON schemas, or
- exported numerical values.

## Generated Artifacts

Each successful interactive analysis run now includes a separate `measurement_debug/` folder:

- `measurement_debugger.html`: standalone developer diagnostic viewer.
- `measurement_debug_raw.csv`: raw diagnostic table derived from already-computed frame records.
- `measurement_debug_raw.json`: JSON equivalent of the raw diagnostic table.

These files are additional artifacts only. The existing per-frame measurement CSV/JSON and time-series JSON are unchanged.

## Debug Viewer

The debugger displays:

- MediaPipe skeleton connections using the existing project topology,
- landmark indices,
- highlighted shoulder, hip, knee, ankle, and foot-index landmarks,
- existing landmark coordinates and visibility values,
- existing joint-angle values,
- landmark triplets from `ANGLE_SIGNAL_MAP`,
- diagnostic Vector A and Vector B components from the displayed landmark coordinates,
- confidence coloring for visibility inspection,
- optional previous-frame landmark trails,
- left/right angle and symmetry comparison panels, and
- frame-by-frame controls and zoom.

## Scientific Boundary

The debug viewer exposes the current computation path. It does not smooth, filter, interpolate, substitute landmarks, redefine angles, alter confidence values, infer events, or create clinical interpretations.

