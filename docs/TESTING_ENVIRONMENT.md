# JumpGuard Interactive Frame-by-Frame Analysis

Prompt 19 replaces the automatic report/comparison testing flow with a clinician-driven frame-by-frame biomechanical viewer. The clinician selects the frame or graph point of interest. JumpGuard displays only the measurements corresponding to that selected processed frame.

## Scope

This is a presentation and interaction layer only. It does not modify MediaPipe landmark extraction, joint angle calculations, feature computation algorithms, annotated video generation, reference datasets, evidence rules, machine-learning models, or numerical biomechanics.

## Run

```bash
PYTHONPATH=. .venv/bin/python -m app.ui.server
```

Open `http://127.0.0.1:7860` and upload an `.mp4`, `.mov`, or `.avi` jump-landing video.

## Outputs

Each run writes to `exports/testing_environment/runs/<run_id>/` and logs to `logs/testing_environment/<run_id>.log`.

The interactive clinical workstation exports:

- existing annotated video
- landmarks CSV/JSON
- per-frame measurement CSV/JSON, including frame index, timestamp, landmark confidence, joint angles, frame-to-frame deltas, and frame-level symmetry values
- synchronized time-series JSON for angles, deltas, and symmetry
- standalone `interactive_viewer.html`
- metadata and app manifest
- app processing log

The workflow does not generate athlete reports, evidence reports, athlete-versus-reference comparisons, automatic ACL observations, recommendations, diagnosis, risk scoring, or event detections.

## Clinician-Controlled Policy

JumpGuard never infers Initial Contact, Peak Landing, Toe Off, peak knee flexion events, ACL risk, or diagnosis in this workflow. The selected frame is clinician-controlled, and every displayed measurement, delta, symmetry value, graph cursor, and comparison chart comes directly from that selected frame.
