# Event Methods

## Dataset Event Fields

| Stored field | Recovered status | Algorithm | Frame selection | Threshold | Timing definition | Evidence |
|---|---|---|---|---|---|---|
| `IC_first_K` | Present as scalar frame index in valid trials | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` |
| `IC_second_K` | Present as scalar frame index in valid trials | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` |
| `IC_first_A` | Present as scalar frame index in valid trials | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` |
| `IC_second_A` | Present as scalar frame index in valid trials | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` |

## Requested Biomechanical Events

| Event | Dataset method recovered? | JumpGuard method recovered? | Harmonization implication |
|---|---|---|---|
| Initial Contact | No. `IC_*` names may suggest initial contact, but K/A meanings and detection method are unknown. | No documented detector exists. | Blocks event-based harmonization. |
| Toe Off | No. | No. | Unknown. |
| Peak Landing | No. | No. Prompt 14 has an audit-only peak mean knee-flexion frame, not a landing detector. | Blocks landing-phase harmonization. |
| Maximum Knee Flexion | Feature-code extrema are defined; dataset event semantics are not. | Prompt 14 provenance identifies extrema frames for audit. | Comparable as an extrema feature, not as a named landing event. |
| Landing Phase | No authoritative definition. | No landing phase segmentation. | Current features remain full-recording features. |
| Propulsion | No. | No. | Unknown. |
| Stance | No. | No. | Unknown. |
| Flight | No. | No. | Unknown. |

## Safety Decision

No event field is used for feature extraction because the K/A suffixes and detection algorithms are not documented. Prompt 16 does not infer event semantics and does not introduce event detectors.
