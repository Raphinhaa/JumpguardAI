# JumpGuard Professional Workstation UI

Prompt 21 converts the testing interface into a clinician-first interactive biomechanics workstation. This change is presentation-only: it does not modify MediaPipe extraction, landmark tracking, joint-angle mathematics, feature calculations, delta calculations, symmetry calculations, time-series generation, CSV/JSON exports, or numerical outputs.

## Primary Interface

The annotated video is the primary review surface. The standalone `interactive_viewer.html` generated for each run displays:

- the annotated video player,
- professional transport controls,
- frame and timestamp readouts,
- synchronized frame information,
- joint-angle measurements,
- frame-to-frame delta values,
- symmetry values,
- landmark confidence indicators,
- synchronized time-series graphs, and
- selected-frame left/right comparison bars.

## Clinician-Facing Controls

The workstation supports:

- play and pause,
- previous-frame and next-frame stepping,
- timeline scrubbing,
- direct timestamp jumping,
- playback-speed selection,
- fullscreen video review,
- Space for play/pause, and
- Left/Right arrows for frame stepping.

## Safety Boundary

The UI does not infer clinical events or conclusions. It does not select landing events, peak flexion frames, initial contact, risk categories, diagnoses, or recommendations. The clinician controls which frame is reviewed.

