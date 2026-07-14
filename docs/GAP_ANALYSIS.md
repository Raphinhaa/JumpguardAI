# Gap Analysis

Prompt 17 identifies gaps without changing algorithms or introducing replacement methods.

## Strongly Supported

| Area | Finding | Future work |
|---|---|---|
| Explicit vector-angle definitions | JumpGuard's uploaded-video hip, knee, and ankle angles are mathematically transparent. | Validate against laboratory motion capture before making equivalence claims. |
| Full-recording descriptors | Mean, median, extrema, ROM, variance, standard deviation, and time-to-peak are implementation-verified. | Add test-retest reliability and sensitivity analyses for MediaPipe-derived signals. |
| Non-diagnostic reporting | Current documentation consistently avoids risk scores and diagnosis. | Preserve this boundary in future reports. |

## Partial Or Inconclusive Support

| Area | Gap | Evidence needed before upgrade |
|---|---|---|
| ISB equivalence | MediaPipe vector angles do not reconstruct ISB segment coordinate systems. | Calibration, segment frames, coordinate axes, and validation against marker-based IK. |
| Reference dataset harmonization | Original dataset's OpenSim model, marker weights, filtering, event methods, and coordinate conventions remain unknown. | Dataset publication, `.osim` model, setup XML files, preprocessing methods, and raw marker/force data. |
| Landing phase | No robust initial-contact or landing-window detector is defined. | Force plate, validated kinematic event detector, or documented video event protocol. |
| Symmetry thresholds | Bilateral symmetry formulas are defined, but clinical thresholds are not established for these MediaPipe-derived ROM values. | Prospective validation and task-specific reliability/meaningful-change studies. |
| Time-to-peak clinical meaning | Current time-to-peak is recording-relative, not event-relative. | Validated event timing and task-window definitions. |

## Measurements Requiring Additional Sensing

| Measurement | Required sensing or method | Current status |
|---|---|---|
| Ground-reaction force | Force plates or validated force estimation. | Not measured. |
| Joint moments | Kinetics plus inverse dynamics. | Not measured. |
| Knee abduction moment | 3D kinematics, kinetics, body-segment parameters, inverse dynamics. | Not measured. |
| EMG / muscle activation | Surface or intramuscular EMG. | Not measured. |
| Trunk kinematics as anatomical segment angles | Explicit trunk and pelvis segment coordinate systems. | Not measured as laboratory trunk kinematics. |
| LESS score | Full LESS item scoring protocol and trained scoring workflow. | Not computed. |
| ACL injury probability | Prospective model with validated predictors and calibration. | Not computed and not authorized by this project stage. |
