# Dataset Lineage

Prompt 16 reconstructs methodology from available documentation and published sources only. No code, dataset values, reports, dashboards, or evidence outputs are changed.

## Evidence Sources Used

| Source | Evidence contributed | Dataset-specific? |
|---|---|---|
| `docs/DATASET_REPORT.md` | MAT-file hierarchy, `DJ` participant/trial organization, `Joint_Angles` shape, marker/COM arrays, IK labels, event-field inventory, sampling inferred from time. | Yes |
| `docs/DATASET_SUMMARY.md` | Clean Dataset/Participant/Trial abstraction and validation summary. | Yes |
| `docs/DATASET_REVERSE_ENGINEERING.md` | Prompt 15 conclusion that feature formulas match but raw measurement equivalence is not established. | Yes |
| `data/metadata/IK_column_labels.xlsx` | OpenSim-style coordinate header with `inDegrees=yes`, `nColumns=44`, and 44 coordinate labels. | Yes |
| `data/metadata/labeling_DJ.xlsx` | Subject/trial rows, fatigue condition, missing-data flags and notes. | Yes |
| `data/metadata/participant_log.xlsx` | Participant metadata including group, gender, age, height, weight, leg dominance, fatigued leg, activity metadata, jump-height and BORG columns. | Yes |
| `data/metadata/ACL_questionnaires.xlsx` | ACL group questionnaire sheets: IKDC, ACL-RSI, Tampa. | Yes |
| OpenSim publications and documentation | General context for OpenSim modeling and inverse kinematics workflows. | No; contextual only unless local dataset files identify the same model/settings. |

## Recovered Lineage Fields

| Required field | Recovered value | Evidence and confidence |
|---|---|---|
| Dataset title | Drop Jump dataset stored as `DJ.mat`; exact public dataset title unknown. | Local filename and metadata support Drop Jump/DJ. Publication title unknown. |
| Original publication | Unknown from available evidence. | No DOI, PMID, manuscript title, author list, or citation appears in local files. Web searches using local filenames/column names did not identify a unique publication. |
| DOI / PMID | Unknown from available evidence. | No dataset-specific DOI/PMID recovered. |
| Authors / institution | Unknown from available evidence. | No author or institutional metadata found. |
| Repository / version / licence | Unknown from available evidence. | Local repository contains copied dataset files but no source repository, version, or licence metadata for the reference dataset. |
| Participant population | 43 metadata-backed subjects, IDs 1-4 and 6-44. Metadata contains control/ACL group coding, gender, anthropometrics, leg dominance, fatigued leg, and ACL injured leg. | High confidence from `labeling_DJ.xlsx`, `participant_log.xlsx`, and `docs/DATASET_REPORT.md`; clinical recruitment criteria unknown. |
| Movement task | Six Drop Jump slots per metadata subject: three nonfatigued and three fatigued trials where available. | High confidence from `.File` values, `labeling_DJ.xlsx`, and parser constants. |
| Hardware | Unknown from available evidence. | Marker arrays imply motion capture, but camera system, force plates, analog devices, and lab hardware are not documented. |
| Marker set | 59 named markers plus marker `time`; names include pelvis, thigh, tibia, foot, trunk, head, and upper-limb markers. | High confidence for marker names and dimensions from `docs/DATASET_REPORT.md`; marker-placement protocol unknown. |
| Sampling frequency | 250 Hz inferred from median `Joint_Angles` time step of 0.004 s. | Moderate confidence; derived from data, not an explicit metadata field. |
| Force plates | Unknown from available evidence. | No force-plate channels or GRF arrays were found. Event fields may have used force or kinematic criteria, but that is not documented. |
| Software | OpenSim-compatible evidence exists: `IK_column_labels.xlsx` has a `Coordinates` header, `inDegrees=yes`, and OpenSim-like coordinate labels. Exact software and version remain unknown. | Moderate for OpenSim-compatible coordinate export; unknown for exact software/version. |
| OpenSim model | Unknown from available evidence. | Coordinate names resemble common OpenSim lower-extremity/full-body coordinate names, but no `.osim` model, scale file, setup file, or model name is present. |

## Published Context, Not Dataset-Specific Proof

- Delp et al. describe OpenSim as open-source software for creating and analyzing dynamic simulations of movement: https://doi.org/10.1109/TBME.2007.901024
- Seth et al. describe OpenSim for musculoskeletal dynamics and neuromuscular-control simulations: https://doi.org/10.1371/journal.pcbi.1006223
- OpenSim documentation describes inverse kinematics as a tool-driven process using a model, marker trajectories, and setup choices. Because the dataset-specific setup files are absent, these sources cannot recover this dataset's exact model or settings.

## Lineage Conclusion

The local evidence supports a processed Drop Jump biomechanics dataset containing OpenSim-style inverse-kinematics coordinate outputs, 3D marker trajectories, COM arrays, participant/trial metadata, fatigue labels, and ACL questionnaires. The original publication, source repository, hardware, exact OpenSim model, IK setup, filtering, and event definitions remain unknown from available evidence.
