# Unknowns Register

| Unknown | Why it matters | Blocks harmonization? | Can it later be experimentally inferred? |
|---|---|---|---|
| Original publication / DOI / repository | Needed for authoritative methods and licensing. | Yes | Potentially recoverable by obtaining source dataset citation from provider. |
| Motion-capture hardware | Affects marker accuracy, sampling, event detection, and force data availability. | Partially | Could be recovered from publication or lab protocol. |
| Force-plate availability and thresholds | Required for initial contact, toe off, stance, and landing phase definitions if events were force based. | Yes for event harmonization | Could be recovered from methods or raw acquisition files. |
| OpenSim model name and version | Defines joint frames, coordinates, constraints, and anatomical zero. | Yes for angle harmonization | Could be recovered from `.osim` model or methods. |
| Static calibration and scaling workflow | Defines subject-specific segment geometry and anatomical coordinate systems. | Yes for exact IK reconstruction | Could be recovered from scale setup files or methods. |
| Marker placement protocol | Determines anatomical meaning and IK marker mapping. | Yes for exact IK reconstruction | Could be recovered from lab protocol or publication. |
| IK marker weights | Affects solved joint coordinates. | Yes for exact numerical reconstruction | Could be recovered from IK setup XML. |
| IK solver tolerances and thresholds | Affects solution quality and reproducibility. | Partially | Could be recovered from setup/log files. |
| Filtering / smoothing / interpolation | Affects extrema, variance, ROM, and time-to-peak. | Yes for numerical harmonization | Could be recovered from scripts/methods; may be experimentally approximated but not proven. |
| Event suffixes K and A | Determines whether `IC_*` fields can define landing windows. | Yes for event-based harmonization | Could be recovered from data dictionary or author clarification. |
| Angle sign and range conventions | Determines whether transformations such as sign flip or `180 - angle` are needed. | Yes | Could be recovered from model coordinate definitions and paired validation. |
| Trial trimming criteria | Defines what full recording contains and whether phases are comparable. | Partially | Could be recovered from preprocessing scripts or raw files. |

## Principle

Unknowns must remain unknown until tied to a published source, dataset documentation, setup file, raw acquisition file, or validated paired reconstruction. Experimental inference may suggest a transformation, but it does not replace documentary evidence unless validated prospectively.
