# Interactive Testing Environment Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| Upload rejected | Unsupported extension or empty file. | Use `.mp4`, `.mov`, or `.avi` and confirm the file is nonempty. |
| Analysis fails | Existing video loading, MediaPipe inference, or annotation export failed. | Open `metadata.json`, the app log, and the testing manifest. |
| No per-frame measurements | Landmarks were unavailable or analysis failed before joint-angle calculation. | Check landmark CSV/JSON and metadata. |
| Viewer opens but browser cannot preview video | Browser codec support varies for `.avi`. | Open/download the annotated video artifact locally. |
| Measurements show NaN | Required landmarks were missing or nonfinite in that selected frame. | Treat as unavailable data; do not infer or fill values. |
| Timeline and graph selection feel offset | Browser video seeking uses timestamps and codec decoding. | Use the frame slider for exact processed-frame selection. |
| Delta value is NaN | The selected frame is the first processed frame or the current/previous signal is unavailable. | Select another frame or inspect landmark availability. |
| Symmetry value is NaN | One or both side-specific joint angles are unavailable for the selected frame. | Inspect landmark confidence and frame visibility. |

## Log Locations

- App logs: `logs/testing_environment/`
- Interactive metadata: `exports/testing_environment/runs/<run_id>/metadata.json`
- Testing manifest: `exports/testing_environment/runs/<run_id>/testing_environment_manifest.json`
