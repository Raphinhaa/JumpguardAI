# Event Definition Audit

## Event Fields Present In The Reference Dataset

| Field | Present? | Observed properties | Detection algorithm | Frame selection | Timing definition | Evidence source | Classification |
|---|---|---|---|---|---|---|---|
| `IC_first_K` | Yes | Scalar integer per valid trial; in frame range; first <= second for K fields. | Unknown from available evidence. | Unknown from available evidence. | Unknown from available evidence. | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` | Semantics unknown |
| `IC_second_K` | Yes | Scalar integer per valid trial; in frame range. | Unknown from available evidence. | Unknown from available evidence. | Unknown from available evidence. | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` | Semantics unknown |
| `IC_first_A` | Yes | Scalar integer per valid trial; in frame range; first <= second for A fields. | Unknown from available evidence. | Unknown from available evidence. | Unknown from available evidence. | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` | Semantics unknown |
| `IC_second_A` | Yes | Scalar integer per valid trial; in frame range. | Unknown from available evidence. | Unknown from available evidence. | Unknown from available evidence. | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` | Semantics unknown |

## Requested Event Concepts

| Event concept | Reference dataset status | JumpGuard status | Prompt 15 conclusion |
|---|---|---|---|
| Initial Contact | The `IC_*` prefix may suggest initial contact, but K/A suffix meaning and detection algorithm are not documented. | No initial-contact detector exists; Prompt 14 marks it unavailable. | Unknown from available evidence. Do not use for harmonization without external documentation. |
| Peak Landing | No explicit peak-landing field or algorithm found. | No documented peak-landing detector exists. | Unknown from available evidence. |
| Maximum Knee Flexion | Can be computed by feature code as the first maximum of `knee_angle_*` or `knee_flexion_*`; not a stored dataset event field. | Prompt 14 computes extrema provenance for first maximum frame of each source signal and a peak mean knee-flexion frame for audit only. | Feature-derived extrema are documented; event semantics are not equivalent to a landing event. |
| Takeoff | No takeoff field or algorithm found. | No takeoff detector exists. | Unknown from available evidence. |
| Landing Phase | Four `IC_*` fields exist but are not used because their semantics are not defined. | No landing phase segmentation exists. | Unknown from available evidence; current features are full-recording features. |

## Decision Boundary

Prompt 15 does not infer `K` or `A`, does not convert one-based event indices, and does not introduce event detectors. Any future use of these event fields requires authoritative documentation or a validated algorithm.
