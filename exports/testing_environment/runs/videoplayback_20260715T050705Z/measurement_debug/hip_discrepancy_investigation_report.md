# Hip Discrepancy Investigation

Developer-only Prompt 25 investigation generated from existing Measurement Debug Mode records.
No MediaPipe extraction, landmark generation, angle mathematics, feature extraction, graphs, schemas, clinician workstation behavior, or numerical outputs are modified by this report.

## Origin Assessment

- **Overall origin:** landmark estimation
- **Evidence standard:** Classification is based only on existing measurements, landmark coordinates, visibility, confidence, and documented angle definitions; no thresholds beyond MediaPipe-style visibility/confidence quality flags are used for clinical interpretation.
- **Summary:** Ranked discrepancy frames contain low visibility or confidence on landmarks used directly in the hip-angle triplets.

| Candidate Origin | Status | Evidence |
|---|---|---|
| landmark estimation | evidence present | frame 50: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry; frame 51: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry; frame 46: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry; frame 47: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry; frame 52: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry; frame 48: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry; frame 42: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry; frame 45: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry; frame 49: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry; frame 53: left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| occlusion | insufficient evidence | No ranked finite hip-pair frame shows missing or nonfinite hip-triplet landmarks in the available records. |
| camera perspective | insufficient evidence | No camera calibration, view label, synchronized multi-view data, or external ground-truth video annotation is present in the frame database. |
| angle-definition limitations | documented limitation, not proven frame-specific cause | Hip flexion is represented as an unsigned internal shoulder-hip-knee vector angle from MediaPipe landmarks; this is a documented geometric definition, not laboratory inverse kinematics. |

## Ranked Frame Investigations

Frames are ranked by the existing computed absolute left/right hip angle difference. Confidence rank is informational only and does not change measurements.

| Rank | Frame | Timestamp | Left Hip | Right Hip | Abs Diff | Confidence Rank | Origin Evidence |
|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 50 | 1.67381 | 81.5886 | 10.3666 | 71.2221 | 7 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 2 | 51 | 1.70728 | 79.9974 | 8.93441 | 71.063 | 9 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 3 | 46 | 1.5399 | 80.7731 | 14.7637 | 66.0094 | 1 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 4 | 47 | 1.57338 | 83.9576 | 18.333 | 65.6246 | 3 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 5 | 52 | 1.74076 | 76.3622 | 12.9647 | 63.3975 | 8 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 6 | 48 | 1.60686 | 73.7286 | 16.2062 | 57.5224 | 5 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 7 | 42 | 1.406 | 77.4264 | 22.6857 | 54.7406 | 4 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 8 | 45 | 1.50643 | 73.4514 | 19.0498 | 54.4016 | 2 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 9 | 49 | 1.64033 | 73.9303 | 20.2513 | 53.679 | 6 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |
| 10 | 53 | 1.77424 | 71.0792 | 19.0475 | 52.0317 | 10 | left hip triplet visibility below 0.5; camera perspective cannot be determined from available single-view debug records; hip angle uses documented unsigned shoulder-hip-knee vector geometry |

## Per-Frame Landmark And Vector Evidence

### Rank 1 - Frame 50

- Timestamp: 1.67381 seconds
- Existing left hip angle: 81.5886 degrees
- Existing right hip angle: 10.3666 degrees
- Existing absolute difference: 71.2221 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.278165, right hip-triplet mean z=-0.244142. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (-0.00610477, -0.141432, 0.0681273) | (-0.00900707, 0.0979889, 0.143832) | 0.390461 | 0.997503 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.0132163, -0.148086, -0.218085) | (-0.00281507, 0.104846, 0.107087) | 0.959549 | 0.997981 | None | None |

### Rank 2 - Frame 51

- Timestamp: 1.70728 seconds
- Existing left hip angle: 79.9974 degrees
- Existing right hip angle: 8.93441 degrees
- Existing absolute difference: 71.063 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.277115, right hip-triplet mean z=-0.241566. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (-0.0107546, -0.142555, 0.0720473) | (-0.00896585, 0.0989408, 0.130982) | 0.432884 | 0.997262 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.00995624, -0.148604, -0.201867) | (-0.00495604, 0.105488, 0.10442) | 0.970254 | 0.997806 | None | None |

### Rank 3 - Frame 46

- Timestamp: 1.5399 seconds
- Existing left hip angle: 80.7731 degrees
- Existing right hip angle: 14.7637 degrees
- Existing absolute difference: 66.0094 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.268499, right hip-triplet mean z=-0.240496. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (-0.00181243, -0.135432, 0.0463686) | (-0.00790733, 0.0886614, 0.165583) | 0.234487 | 0.996995 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.00732681, -0.142286, -0.223051) | (0.00462615, 0.100335, 0.0939702) | 0.902834 | 0.997195 | None | None |

### Rank 4 - Frame 47

- Timestamp: 1.57338 seconds
- Existing left hip angle: 83.9576 degrees
- Existing right hip angle: 18.333 degrees
- Existing absolute difference: 65.6246 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.282763, right hip-triplet mean z=-0.249102. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (-0.0147325, -0.133878, 0.0473884) | (-0.00908059, 0.092408, 0.19091) | 0.270222 | 0.997332 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.0167307, -0.144564, -0.218566) | (0.00252301, 0.0994084, 0.0799603) | 0.935947 | 0.997508 | None | None |

### Rank 5 - Frame 52

- Timestamp: 1.74076 seconds
- Existing left hip angle: 76.3622 degrees
- Existing right hip angle: 12.9647 degrees
- Existing absolute difference: 63.3975 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.268067, right hip-triplet mean z=-0.236636. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (-0.00930834, -0.141614, 0.0895761) | (-0.00990021, 0.102131, 0.0978115) | 0.415826 | 0.997482 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.00975317, -0.149216, -0.174711) | (-0.00760296, 0.10893, 0.0807304) | 0.970341 | 0.998128 | None | None |

### Rank 6 - Frame 48

- Timestamp: 1.60686 seconds
- Existing left hip angle: 73.7286 degrees
- Existing right hip angle: 16.2062 degrees
- Existing absolute difference: 57.5224 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.265929, right hip-triplet mean z=-0.253489. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (0.00198364, -0.136239, 0.0422786) | (-0.0148552, 0.09376, 0.14163) | 0.334835 | 0.996892 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.00775492, -0.143674, -0.24591) | (0.00253743, 0.102759, 0.0982111) | 0.93834 | 0.997227 | None | None |

### Rank 7 - Frame 42

- Timestamp: 1.406 seconds
- Existing left hip angle: 77.4264 degrees
- Existing right hip angle: 22.6857 degrees
- Existing absolute difference: 54.7406 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.282032, right hip-triplet mean z=-0.260499. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (-0.000229061, -0.136785, 0.0273643) | (-0.00807825, 0.0876035, 0.197697) | 0.284211 | 0.998931 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.00752902, -0.139173, -0.232334) | (0.00486246, 0.0936481, 0.0698989) | 0.92524 | 0.999004 | None | None |

### Rank 8 - Frame 45

- Timestamp: 1.50643 seconds
- Existing left hip angle: 73.4514 degrees
- Existing right hip angle: 19.0498 degrees
- Existing absolute difference: 54.4016 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.253902, right hip-triplet mean z=-0.236806. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (-0.00227255, -0.133659, 0.0281844) | (-0.0103196, 0.0893419, 0.164279) | 0.242333 | 0.998496 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.00464299, -0.14089, -0.21975) | (0.00516194, 0.096803, 0.0772424) | 0.912514 | 0.998256 | None | None |

### Rank 9 - Frame 49

- Timestamp: 1.64033 seconds
- Existing left hip angle: 73.9303 degrees
- Existing right hip angle: 20.2513 degrees
- Existing absolute difference: 53.679 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.259455, right hip-triplet mean z=-0.248372. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (0.0051589, -0.139629, 0.0591109) | (-0.0104131, 0.097284, 0.120457) | 0.389042 | 0.997038 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.00791538, -0.144397, -0.228266) | (0.00176689, 0.105291, 0.0810188) | 0.944083 | 0.997257 | None | None |

### Rank 10 - Frame 53

- Timestamp: 1.77424 seconds
- Existing left hip angle: 71.0792 degrees
- Existing right hip angle: 19.0475 degrees
- Existing absolute difference: 52.0317 degrees
- Near/far-side inference: Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.
- Z geometry evidence: left hip-triplet mean z=0.26612, right hip-triplet mean z=-0.244897. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone.

| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |
|---|---|---|---|---:|---:|---|---|
| left | left_shoulder -> left_hip -> left_knee | (-0.00719884, -0.139406, 0.0920892) | (-0.00911522, 0.101655, 0.077656) | 0.466066 | 0.998496 | None | None |
| right | right_shoulder -> right_hip -> right_knee | (0.00833699, -0.148612, -0.168963) | (-0.00821239, 0.109054, 0.0621089) | 0.977528 | 0.999081 | None | None |
