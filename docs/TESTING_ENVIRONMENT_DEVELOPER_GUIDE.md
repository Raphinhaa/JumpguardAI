# Interactive Testing Environment Developer Guide

## Design Rules

1. Reuse `InteractiveFrameAnalyzer` for frame-by-frame analysis.
2. Do not call report, evidence, reference comparison, or dashboard generation from the interactive workflow.
3. Do not add event detection, peak detection, diagnosis, recommendations, or ACL risk language unless a future validated module explicitly introduces it.
4. Every UI measurement must be keyed by selected `frame_index` and `timestamp`.
5. No interpolation, averaging, or automatic event-windowing is allowed in the live measurement panel.
6. Delta and symmetry displays must be exported from the per-frame database, not recomputed ad hoc in separate UI code paths.

## Programmatic Use

```python
from app.pipeline import TestingEnvironment, TestingEnvironmentConfig

environment = TestingEnvironment(TestingEnvironmentConfig.load())
result = environment.analyze_video("path/to/jump.mp4", run_id="manual_frame_review")
print(result.generated_files["interactive_viewer_html"])
```

## Future Extension Points

Future modules may add clinician bookmarks, manual annotations, event detectors, or exports. Those modules should consume the per-frame database rather than modifying MediaPipe extraction, joint-angle calculations, symmetry formulas, or feature algorithms.
