# Hip Discrepancy Investigation

Developer-only Prompt 25 investigation generated from existing Measurement Debug Mode records.
No MediaPipe extraction, landmark generation, angle mathematics, feature extraction, graphs, schemas, clinician workstation behavior, or numerical outputs are modified by this report.

## Origin Assessment

- **Overall origin:** landmark estimation
- **Evidence standard:** Classification is based only on existing measurements, landmark coordinates, visibility, confidence, and documented angle definitions; no thresholds beyond MediaPipe-style visibility/confidence quality flags are used for clinical interpretation.
- **Summary:** Ranked discrepancy frames contain low visibility or confidence on landmarks used directly in the hip-angle triplets.

| Candidate Origin | Status | Evidence |
|---|---|---|
| landmark estimation | evidence present | frame 90: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry; frame 61: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry; frame 91: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry; frame 89: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry; frame 67: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| occlusion | insufficient evidence | No ranked finite hip-pair frame shows missing or nonfinite hip-triplet landmarks in the available records. |
| camera perspective | insufficient evidence | No camera calibration, view label, synchronized multi-view data, or external ground-truth video annotation is present in the frame database. |
| angle-definition limitations | documented limitation, not proven frame-specific cause | Hip flexion is represented as an unsigned internal shoulder-hip-knee vector angle from MediaPipe landmarks; this is a documented geometric definition, not laboratory inverse kinematics. |

## Ranked Frame Investigations

Frames are ranked by the existing computed absolute left/right hip angle difference. Confidence rank is informational only and does not change measurements.

| Rank | Frame | Timestamp | Left Hip | Right Hip | Abs Diff | Confidence Rank | Origin Evidence |
|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 62 | 2.06667 | 30.9417 | 97.8726 | 66.931 | 6 | camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 2 | 58 | 1.93333 | 18.937 | 83.0473 | 64.1103 | 9 | camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 3 | 90 | 3 | 18.1174 | 80.1287 | 62.0112 | 2 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 4 | 56 | 1.86667 | 11.1157 | 63.4009 | 52.2851 | 10 | camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 5 | 61 | 2.03333 | 69.8625 | 111.854 | 41.9912 | 4 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 6 | 55 | 1.83333 | 17.4503 | 50.2638 | 32.8135 | 8 | camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 7 | 43 | 1.43333 | 9.02798 | 40.7243 | 31.6963 | 7 | camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 8 | 91 | 3.03333 | 28.7464 | 59.0574 | 30.311 | 1 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 9 | 89 | 2.96667 | 28.6271 | 57.6302 | 29.0031 | 5 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 10 | 67 | 2.23333 | 27.2686 | 54.8459 | 27.5773 | 3 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |

## Per-Frame Landmark And Vector Evidence

### Rank 1 - Frame 62

- Timestamp: 2.06667 seconds
- Existing left hip angle: 30.9417 degrees
- Existing right hip angle: 97.8726 degrees
- Existing absolute difference: 66.931 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.155923, right hip-triplet mean z=-0.194021. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (0.014713, -0.097541, 0.0815996) | (0.0224085, 0.0630193, -0.0246101) | 0.505037 | 0.998007 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.0256327, -0.095587, -0.0990293) | (0.0401431, 0.0652654, -0.0731148) | 0.942807 | 0.999489 | None | None |

### Rank 2 - Frame 58

- Timestamp: 1.93333 seconds
- Existing left hip angle: 18.937 degrees
- Existing right hip angle: 83.0473 degrees
- Existing absolute difference: 64.1103 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.129802, right hip-triplet mean z=-0.153705. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (0.0217369, -0.0980702, 0.107966) | (0.00260603, 0.0709516, -0.0439697) | 0.751912 | 0.998614 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.0257273, -0.102797, -0.0811153) | (0.015918, 0.0599785, -0.0545125) | 0.942265 | 0.99843 | None | None |

### Rank 3 - Frame 90

- Timestamp: 3 seconds
- Existing left hip angle: 18.1174 degrees
- Existing right hip angle: 80.1287 degrees
- Existing absolute difference: 62.0112 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.147259, right hip-triplet mean z=-0.21171. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (0.00745398, -0.0906735, -0.0484489) | (-0.00602797, 0.0719108, 0.0751294) | 0.370074 | 0.99943 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.00874624, -0.0928531, -0.201628) | (0.0070985, 0.0756196, -0.0196953) | 0.959706 | 0.999548 | None | None |

### Rank 4 - Frame 56

- Timestamp: 1.86667 seconds
- Existing left hip angle: 11.1157 degrees
- Existing right hip angle: 63.4009 degrees
- Existing absolute difference: 52.2851 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.119783, right hip-triplet mean z=-0.159322. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (0.0175712, -0.101744, 0.0439875) | (-0.0152498, 0.0736605, -0.0161363) | 0.794 | 0.997309 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.0238312, -0.105275, -0.132058) | (0.00495505, 0.0741566, -0.0144398) | 0.979272 | 0.99599 | None | None |

### Rank 5 - Frame 61

- Timestamp: 2.03333 seconds
- Existing left hip angle: 69.8625 degrees
- Existing right hip angle: 111.854 degrees
- Existing absolute difference: 41.9912 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.174892, right hip-triplet mean z=-0.217511. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (0.0303656, -0.100123, 0.0492127) | (0.0250596, 0.0652129, 0.0484466) | 0.408537 | 0.998609 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.0335345, -0.0951752, -0.115733) | (0.0415076, 0.0675458, -0.110809) | 0.934921 | 0.997522 | None | None |

### Rank 6 - Frame 55

- Timestamp: 1.83333 seconds
- Existing left hip angle: 17.4503 degrees
- Existing right hip angle: 50.2638 degrees
- Existing absolute difference: 32.8135 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.132209, right hip-triplet mean z=-0.160455. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (0.0146964, -0.100717, 0.0467732) | (-0.00686824, 0.0752547, -0.00992435) | 0.679767 | 0.99745 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.0247997, -0.101171, -0.123578) | (0.00181004, 0.0792281, 0.00177385) | 0.97595 | 0.997144 | None | None |

### Rank 7 - Frame 43

- Timestamp: 1.43333 seconds
- Existing left hip angle: 9.02798 degrees
- Existing right hip angle: 40.7243 degrees
- Existing absolute difference: 31.6963 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.122388, right hip-triplet mean z=-0.155592. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (-0.0312612, 0.0944087, -0.00851112) | (0.0372276, -0.0737899, 0.0119331) | 0.564429 | 0.986711 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (-0.0411617, 0.100121, -0.111422) | (0.038003, -0.0767787, 0.00787188) | 0.976029 | 0.993345 | None | None |

### Rank 8 - Frame 91

- Timestamp: 3.03333 seconds
- Existing left hip angle: 28.7464 degrees
- Existing right hip angle: 59.0574 degrees
- Existing absolute difference: 30.311 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.159232, right hip-triplet mean z=-0.204793. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (0.00841299, -0.0927262, -0.0455808) | (-0.00343591, 0.0699518, 0.0992003) | 0.278874 | 0.999442 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.00625217, -0.0942091, -0.199206) | (0.00524473, 0.0736948, 0.00757186) | 0.944547 | 0.999559 | None | None |

### Rank 9 - Frame 89

- Timestamp: 2.96667 seconds
- Existing left hip angle: 28.6271 degrees
- Existing right hip angle: 57.6302 degrees
- Existing absolute difference: 29.0031 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.1545, right hip-triplet mean z=-0.199746. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (0.00758103, -0.0919349, -0.020728) | (-0.00633121, 0.0676332, 0.0596471) | 0.448548 | 0.999354 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.0086517, -0.0941692, -0.18301) | (0.00234312, 0.0761113, 0.00703117) | 0.974905 | 0.999621 | None | None |

### Rank 10 - Frame 67

- Timestamp: 2.23333 seconds
- Existing left hip angle: 27.2686 degrees
- Existing right hip angle: 54.8459 degrees
- Existing absolute difference: 27.5773 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.171901, right hip-triplet mean z=-0.214804. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (0.0056679, -0.0979457, -0.0791484) | (-0.00355878, 0.067417, 0.152796) | 0.382486 | 0.999619 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.0201751, -0.0942329, -0.219529) | (-0.000449538, 0.0742604, 0.0158279) | 0.971809 | 0.999808 | None | None |
