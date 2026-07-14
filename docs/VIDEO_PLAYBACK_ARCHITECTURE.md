# Video Playback Architecture

Prompt 21 keeps video playback in the UI layer. The scientific pipeline remains unchanged.

## Processing Boundary

The existing pipeline still generates:

- annotated video,
- landmark CSV/JSON,
- per-frame measurement CSV/JSON,
- time-series JSON,
- metadata, and
- logs.

The workstation consumes those outputs. It does not regenerate landmarks, recompute joint angles, recalculate features, modify deltas, modify symmetry, or alter exported numerical files.

## Playback Controls

The generated viewer uses standard browser video APIs for:

- play,
- pause,
- `currentTime` seeking,
- `playbackRate`, and
- fullscreen requests.

Frame selection is mapped to the nearest processed timestamp already present in the frame database.

## Responsiveness

Measurements and graphs are precomputed before the viewer opens. UI updates use the embedded frame database, which avoids reprocessing the video during clinician review.

## Failure Mode

If a measurement is unavailable for a frame, the existing `NaN`/null display behavior is preserved. The UI does not estimate missing values.

