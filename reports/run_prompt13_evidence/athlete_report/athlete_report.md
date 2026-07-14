# JumpGuard Uploaded Video Report

This report is descriptive. It does not diagnose injury, estimate risk, or introduce clinical interpretation.

## Summary

Run-local uploaded-video report generated from existing pipeline outputs.

## Annotated Video

reports/run_prompt13_evidence/video/jump_annotated.avi

## Evidence-Based ACL Biomechanical Observations

```json
[
  {
    "comparison_performed": "10 supporting feature(s) fell outside the reference dataset's central 90% interval (2 low-tail, 8 high-tail). This is a dataset-relative comparison, not a clinical threshold.",
    "evidence_based_explanation": "Sagittal-plane knee flexion is commonly evaluated in jump-landing ACL biomechanics. Prospective and clinical jump-landing studies discuss knee mechanics as part of neuromuscular-control assessment.",
    "evidence_strength": "Moderate for movement-context interpretation; not sufficient for diagnosis or prediction from this feature alone.",
    "features_used": [
      "knee_flexion_left_maximum",
      "knee_flexion_left_mean",
      "knee_flexion_left_median",
      "knee_flexion_left_minimum",
      "knee_flexion_left_rom",
      "knee_flexion_right_maximum",
      "knee_flexion_right_mean",
      "knee_flexion_right_median",
      "knee_flexion_right_minimum",
      "knee_flexion_right_rom"
    ],
    "limitation": "This observation is descriptive and dataset-relative. It is not diagnostic, does not predict ACL injury, and does not establish tissue status or ligament integrity.",
    "literature_sources": [
      {
        "citation": "Hewett TE, Myer GD, Ford KR, Heidt RS Jr, Colosimo AJ, McLean SG, van den Bogert AJ, Paterno MV, Succop P. Biomechanical measures of neuromuscular control and valgus loading of the knee predict anterior cruciate ligament injury risk in female athletes: a prospective study. Am J Sports Med. 2005;33(4):492-501.",
        "doi": "10.1177/0363546504269591",
        "pmid": "15722287",
        "url": "https://doi.org/10.1177/0363546504269591"
      },
      {
        "citation": "Padua DA, Marshall SW, Boling MC, Thigpen CA, Garrett WE Jr, Beutler AI. The Landing Error Scoring System (LESS) is a valid and reliable clinical assessment tool of jump-landing biomechanics: The JUMP-ACL study. Am J Sports Med. 2009;37(10):1996-2002.",
        "doi": "10.1177/0363546509343200",
        "pmid": "19726623",
        "url": "https://doi.org/10.1177/0363546509343200"
      }
    ],
    "observation_id": "participant_1_sagittal_knee_flexion",
    "participant_id": 1,
    "safety_label": "context_only_not_diagnosis_not_prediction",
    "suggested_clinical_consideration": "Consider reviewing the landing video and full lower-extremity movement pattern with a qualified clinician or biomechanist.",
    "supporting_features": [
      {
        "feature": "knee_flexion_left_maximum",
        "measured_value": 176.18723618264826,
        "reference_mean": 100.95998812240963,
        "reference_p05": 83.435707002,
        "reference_p95": 116.22981573999999,
        "reference_percentile": 100.0,
        "reference_std": 9.820271463544282,
        "reference_tail": "high_reference_tail",
        "z_score": 7.660404128287509
      },
      {
        "feature": "knee_flexion_left_mean",
        "measured_value": 147.33696204653626,
        "reference_mean": 48.542095818875495,
        "reference_p05": 33.655246988,
        "reference_p95": 67.662938466,
        "reference_percentile": 100.0,
        "reference_std": 9.546288192022617,
        "reference_tail": "high_reference_tail",
        "z_score": 10.34903453996067
      },
      {
        "feature": "knee_flexion_left_median",
        "measured_value": 150.15560911273576,
        "reference_mean": 48.26871747903614,
        "reference_p05": 14.755523938,
        "reference_p95": 86.859009556,
        "reference_percentile": 100.0,
        "reference_std": 22.261912350681865,
        "reference_tail": "high_reference_tail",
        "z_score": 4.576735818051988
      },
      {
        "feature": "knee_flexion_left_minimum",
        "measured_value": 98.01706481004888,
        "reference_mean": 2.6245320226907634,
        "reference_p05": 0.19690704,
        "reference_p95": 8.654981135999998,
        "reference_percentile": 100.0,
        "reference_std": 3.347066678793443,
        "reference_tail": "high_reference_tail",
        "z_score": 28.50033833856737
      },
      {
        "feature": "knee_flexion_left_rom",
        "measured_value": 78.17017137259938,
        "reference_mean": 98.33545610405622,
        "reference_p05": 79.005932786,
        "reference_p95": 115.18618144,
        "reference_percentile": 4.016064257028113,
        "reference_std": 11.147902824350393,
        "reference_tail": "low_reference_tail",
        "z_score": -1.8088859446648344
      },
      {
        "feature": "knee_flexion_right_maximum",
        "measured_value": 161.09189308968956,
        "reference_mean": 101.01146130746987,
        "reference_p05": 85.005155064,
        "reference_p95": 116.47119564,
        "reference_percentile": 100.0,
        "reference_std": 9.428262502841024,
        "reference_tail": "high_reference_tail",
        "z_score": 6.372375797143494
      },
      {
        "feature": "knee_flexion_right_mean",
        "measured_value": 132.23071564016576,
        "reference_mean": 48.48859166618474,
        "reference_p05": 34.159126884,
        "reference_p95": 67.44640889799999,
        "reference_percentile": 100.0,
        "reference_std": 9.572527316686884,
        "reference_tail": "high_reference_tail",
        "z_score": 8.748172891395283
      },
      {
        "feature": "knee_flexion_right_median",
        "measured_value": 140.38244810457712,
        "reference_mean": 48.06461292879517,
        "reference_p05": 14.240514150000001,
        "reference_p95": 88.954418568,
        "reference_percentile": 100.0,
        "reference_std": 22.422563407474847,
        "reference_tail": "high_reference_tail",
        "z_score": 4.117184708016329
      },
      {
        "feature": "knee_flexion_right_minimum",
        "measured_value": 82.25714233575171,
        "reference_mean": 2.552388808594378,
        "reference_p05": 0.162458002,
        "reference_p95": 9.274697382,
        "reference_percentile": 100.0,
        "reference_std": 3.491542063413932,
        "reference_tail": "high_reference_tail",
        "z_score": 22.827951684255027
      },
      {
        "feature": "knee_flexion_right_rom",
        "measured_value": 78.83475075393785,
        "reference_mean": 98.45907250004015,
        "reference_p05": 80.18034017000001,
        "reference_p95": 115.79147006,
        "reference_percentile": 4.016064257028113,
        "reference_std": 10.838632661766553,
        "reference_tail": "low_reference_tail",
        "z_score": -1.8105901693049715
      }
    ],
    "title": "Knee sagittal-plane flexion features from Prompt 11."
  },
  {
    "comparison_performed": "6 supporting feature(s) fell outside the reference dataset's central 90% interval (0 low-tail, 6 high-tail). This is a dataset-relative comparison, not a clinical threshold.",
    "evidence_based_explanation": "Hip flexion is part of sagittal-plane landing strategy and is considered alongside trunk, knee, and ankle mechanics in jump-landing assessment research.",
    "evidence_strength": "Limited-to-moderate for movement-context interpretation; this project does not measure trunk motion or joint moments.",
    "features_used": [
      "hip_flexion_left_maximum",
      "hip_flexion_left_rom",
      "hip_flexion_right_maximum",
      "hip_flexion_rom_absolute_difference",
      "hip_flexion_rom_percent_difference",
      "hip_flexion_rom_symmetry_index"
    ],
    "limitation": "This observation is descriptive and dataset-relative. It is not diagnostic, does not predict ACL injury, and does not establish tissue status or ligament integrity.",
    "literature_sources": [
      {
        "citation": "Padua DA, Marshall SW, Boling MC, Thigpen CA, Garrett WE Jr, Beutler AI. The Landing Error Scoring System (LESS) is a valid and reliable clinical assessment tool of jump-landing biomechanics: The JUMP-ACL study. Am J Sports Med. 2009;37(10):1996-2002.",
        "doi": "10.1177/0363546509343200",
        "pmid": "19726623",
        "url": "https://doi.org/10.1177/0363546509343200"
      }
    ],
    "observation_id": "participant_1_sagittal_hip_strategy",
    "participant_id": 1,
    "safety_label": "context_only_not_diagnosis_not_prediction",
    "suggested_clinical_consideration": "Consider reviewing whether the observed hip strategy is consistent across trials and with the athlete's task context.",
    "supporting_features": [
      {
        "feature": "hip_flexion_left_maximum",
        "measured_value": 124.06814800640889,
        "reference_mean": 91.50879386706828,
        "reference_p05": 70.889016946,
        "reference_p95": 111.5754404,
        "reference_percentile": 100.0,
        "reference_std": 11.826983218031588,
        "reference_tail": "high_reference_tail",
        "z_score": 2.752972041906693
      },
      {
        "feature": "hip_flexion_left_rom",
        "measured_value": 116.48552077495113,
        "reference_mean": 87.18351043080321,
        "reference_p05": 57.705056646,
        "reference_p95": 115.834384,
        "reference_percentile": 95.58232931726907,
        "reference_std": 19.166444211332593,
        "reference_tail": "high_reference_tail",
        "z_score": 1.5288182837180848
      },
      {
        "feature": "hip_flexion_right_maximum",
        "measured_value": 117.22206249273226,
        "reference_mean": 92.06944754602411,
        "reference_p05": 72.331205506,
        "reference_p95": 111.52517806,
        "reference_percentile": 99.19678714859438,
        "reference_std": 11.730542255969286,
        "reference_tail": "high_reference_tail",
        "z_score": 2.1441988271180574
      },
      {
        "feature": "hip_flexion_rom_absolute_difference",
        "measured_value": 17.570111463554,
        "reference_mean": 2.6317642214056227,
        "reference_p05": 0.216232544,
        "reference_p95": 6.347048854,
        "reference_percentile": 99.59839357429718,
        "reference_std": 2.1686027513053947,
        "reference_tail": "high_reference_tail",
        "z_score": 6.888466425285225
      },
      {
        "feature": "hip_flexion_rom_percent_difference",
        "measured_value": 16.31386777811092,
        "reference_mean": 3.1858494657454215,
        "reference_p05": 0.2968869241,
        "reference_p95": 8.3423260752,
        "reference_percentile": 99.59839357429718,
        "reference_std": 2.859468135729925,
        "reference_tail": "high_reference_tail",
        "z_score": 4.591069978478484
      },
      {
        "feature": "hip_flexion_rom_symmetry_index",
        "measured_value": 16.31386777811092,
        "reference_mean": -0.8390409840618873,
        "reference_p05": -7.6244369832,
        "reference_p95": 5.4695670774,
        "reference_percentile": 100.0,
        "reference_std": 4.197881020790087,
        "reference_tail": "high_reference_tail",
        "z_score": 4.086087403912283
      }
    ],
    "title": "Hip sagittal-plane flexion features from Prompt 11."
  },
  {
    "comparison_performed": "13 supporting feature(s) fell outside the reference dataset's central 90% interval (1 low-tail, 12 high-tail). This is a dataset-relative comparison, not a clinical threshold.",
    "evidence_based_explanation": "Ankle position is one component of lower-extremity jump-landing assessment. This interpretation is limited to descriptive sagittal-plane movement context.",
    "evidence_strength": "Limited for ACL-specific interpretation from ankle angle alone.",
    "features_used": [
      "ankle_angle_left_maximum",
      "ankle_angle_left_mean",
      "ankle_angle_left_median",
      "ankle_angle_left_minimum",
      "ankle_angle_left_rom",
      "ankle_angle_right_maximum",
      "ankle_angle_right_mean",
      "ankle_angle_right_median",
      "ankle_angle_right_minimum",
      "ankle_angle_right_rom",
      "ankle_angle_rom_absolute_difference",
      "ankle_angle_rom_percent_difference",
      "ankle_angle_rom_symmetry_index"
    ],
    "limitation": "This observation is descriptive and dataset-relative. It is not diagnostic, does not predict ACL injury, and does not establish tissue status or ligament integrity.",
    "literature_sources": [
      {
        "citation": "Padua DA, Marshall SW, Boling MC, Thigpen CA, Garrett WE Jr, Beutler AI. The Landing Error Scoring System (LESS) is a valid and reliable clinical assessment tool of jump-landing biomechanics: The JUMP-ACL study. Am J Sports Med. 2009;37(10):1996-2002.",
        "doi": "10.1177/0363546509343200",
        "pmid": "19726623",
        "url": "https://doi.org/10.1177/0363546509343200"
      }
    ],
    "observation_id": "participant_1_sagittal_ankle_strategy",
    "participant_id": 1,
    "safety_label": "context_only_not_diagnosis_not_prediction",
    "suggested_clinical_consideration": "Consider ankle observations only in combination with the full landing pattern and source video review.",
    "supporting_features": [
      {
        "feature": "ankle_angle_left_maximum",
        "measured_value": 150.529009126214,
        "reference_mean": 35.08933530236948,
        "reference_p05": 29.07888074,
        "reference_p95": 39.617591302,
        "reference_percentile": 100.0,
        "reference_std": 3.4398764656741387,
        "reference_tail": "high_reference_tail",
        "z_score": 33.55924986719572
      },
      {
        "feature": "ankle_angle_left_mean",
        "measured_value": 126.54317967055776,
        "reference_mean": 10.918687330655823,
        "reference_p05": 3.2505212686,
        "reference_p95": 19.821048806,
        "reference_percentile": 100.0,
        "reference_std": 5.095012992055711,
        "reference_tail": "high_reference_tail",
        "z_score": 22.69365996125759
      },
      {
        "feature": "ankle_angle_left_median",
        "measured_value": 132.58053212136224,
        "reference_mean": 14.338309453935745,
        "reference_p05": -1.445005774,
        "reference_p95": 31.269156927999997,
        "reference_percentile": 100.0,
        "reference_std": 10.942110723849094,
        "reference_tail": "high_reference_tail",
        "z_score": 10.806162142895275
      },
      {
        "feature": "ankle_angle_left_minimum",
        "measured_value": 72.19981007013389,
        "reference_mean": -36.93045488706827,
        "reference_p05": -39.599868838,
        "reference_p95": -28.453265222,
        "reference_percentile": 100.0,
        "reference_std": 4.189993350039785,
        "reference_tail": "high_reference_tail",
        "z_score": 26.045450634466032
      },
      {
        "feature": "ankle_angle_left_rom",
        "measured_value": 78.3291990560801,
        "reference_mean": 72.01979018943776,
        "reference_p05": 63.598887896,
        "reference_p95": 77.967289974,
        "reference_percentile": 97.59036144578313,
        "reference_std": 4.408677461558661,
        "reference_tail": "high_reference_tail",
        "z_score": 1.4311341488818488
      },
      {
        "feature": "ankle_angle_right_maximum",
        "measured_value": 144.21801748767453,
        "reference_mean": 35.59689316582329,
        "reference_p05": 29.51882292,
        "reference_p95": 39.56227811,
        "reference_percentile": 100.0,
        "reference_std": 3.167733952918059,
        "reference_tail": "high_reference_tail",
        "z_score": 34.28985070598856
      },
      {
        "feature": "ankle_angle_right_mean",
        "measured_value": 131.81505316996308,
        "reference_mean": 11.371296263393575,
        "reference_p05": 3.955152163,
        "reference_p95": 20.278966464,
        "reference_percentile": 100.0,
        "reference_std": 4.756889211448827,
        "reference_tail": "high_reference_tail",
        "z_score": 25.319857485157915
      },
      {
        "feature": "ankle_angle_right_median",
        "measured_value": 134.39072634236015,
        "reference_mean": 14.840188950963853,
        "reference_p05": -0.2886826629999997,
        "reference_p95": 32.30770468,
        "reference_percentile": 100.0,
        "reference_std": 10.921406898000894,
        "reference_tail": "high_reference_tail",
        "z_score": 10.94644110487994
      },
      {
        "feature": "ankle_angle_right_minimum",
        "measured_value": 98.3313135812712,
        "reference_mean": -36.46039515349398,
        "reference_p05": -39.622029788,
        "reference_p95": -25.282335668,
        "reference_percentile": 100.0,
        "reference_std": 4.816798897283524,
        "reference_tail": "high_reference_tail",
        "z_score": 27.983669571669708
      },
      {
        "feature": "ankle_angle_right_rom",
        "measured_value": 45.886703906403326,
        "reference_mean": 72.05728831931728,
        "reference_p05": 60.916638074,
        "reference_p95": 78.12079428599999,
        "reference_percentile": 0.0,
        "reference_std": 5.166876800240897,
        "reference_tail": "low_reference_tail",
        "z_score": -5.065068401029766
      },
      {
        "feature": "ankle_angle_rom_absolute_difference",
        "measured_value": 32.44249514967677,
        "reference_mean": 2.588520820481927,
        "reference_p05": 0.13366976600000002,
        "reference_p95": 6.821447549999998,
        "reference_percentile": 100.0,
        "reference_std": 2.263827388017835,
        "reference_tail": "high_reference_tail",
        "z_score": 13.187389854548243
      },
      {
        "feature": "ankle_angle_rom_percent_difference",
        "measured_value": 52.23565481704108,
        "reference_mean": 3.6862605144716465,
        "reference_p05": 0.18949107773999999,
        "reference_p95": 9.877225196399998,
        "reference_percentile": 100.0,
        "reference_std": 3.362342378025142,
        "reference_tail": "high_reference_tail",
        "z_score": 14.43915843308162
      },
      {
        "feature": "ankle_angle_rom_symmetry_index",
        "measured_value": 52.23565481704108,
        "reference_mean": 0.024873448313975845,
        "reference_p05": -6.786905694,
        "reference_p95": 9.0840742392,
        "reference_percentile": 100.0,
        "reference_std": 4.989312994710344,
        "reference_tail": "high_reference_tail",
        "z_score": 10.464523156611106
      }
    ],
    "title": "Ankle sagittal-plane angle features from Prompt 11."
  },
  {
    "comparison_performed": "6 supporting feature(s) fell outside the reference dataset's central 90% interval (0 low-tail, 6 high-tail). This is a dataset-relative comparison, not a clinical threshold.",
    "evidence_based_explanation": "Bilateral movement asymmetry is commonly examined in ACL rehabilitation and return-to-sport biomechanics. Prompt 11 symmetry features describe joint-angle ROM symmetry only and are not equivalent to hop-test or kinetic limb-symmetry criteria.",
    "evidence_strength": "Moderate for general asymmetry context; limited for ROM-only MediaPipe-derived symmetry interpretation.",
    "features_used": [
      "ankle_angle_rom_absolute_difference",
      "ankle_angle_rom_percent_difference",
      "ankle_angle_rom_symmetry_index",
      "hip_flexion_rom_absolute_difference",
      "hip_flexion_rom_percent_difference",
      "hip_flexion_rom_symmetry_index"
    ],
    "limitation": "This observation is descriptive and dataset-relative. It is not diagnostic, does not predict ACL injury, and does not establish tissue status or ligament integrity.",
    "literature_sources": [
      {
        "citation": "Paterno MV, Schmitt LC, Ford KR, Rauh MJ, Myer GD, Huang B, Hewett TE. Biomechanical measures during landing and postural stability predict second anterior cruciate ligament injury after anterior cruciate ligament reconstruction and return to sport. Am J Sports Med. 2010;38(10):1968-1978.",
        "doi": "10.1177/0363546510376053",
        "pmid": "20702858",
        "url": "https://doi.org/10.1177/0363546510376053"
      }
    ],
    "observation_id": "participant_1_bilateral_rom_symmetry",
    "participant_id": 1,
    "safety_label": "context_only_not_diagnosis_not_prediction",
    "suggested_clinical_consideration": "Consider comparing the symmetry observation with video review, task consistency, and any clinician-collected strength or functional tests when available.",
    "supporting_features": [
      {
        "feature": "ankle_angle_rom_absolute_difference",
        "measured_value": 32.44249514967677,
        "reference_mean": 2.588520820481927,
        "reference_p05": 0.13366976600000002,
        "reference_p95": 6.821447549999998,
        "reference_percentile": 100.0,
        "reference_std": 2.263827388017835,
        "reference_tail": "high_reference_tail",
        "z_score": 13.187389854548243
      },
      {
        "feature": "ankle_angle_rom_percent_difference",
        "measured_value": 52.23565481704108,
        "reference_mean": 3.6862605144716465,
        "reference_p05": 0.18949107773999999,
        "reference_p95": 9.877225196399998,
        "reference_percentile": 100.0,
        "reference_std": 3.362342378025142,
        "reference_tail": "high_reference_tail",
        "z_score": 14.43915843308162
      },
      {
        "feature": "ankle_angle_rom_symmetry_index",
        "measured_value": 52.23565481704108,
        "reference_mean": 0.024873448313975845,
        "reference_p05": -6.786905694,
        "reference_p95": 9.0840742392,
        "reference_percentile": 100.0,
        "reference_std": 4.989312994710344,
        "reference_tail": "high_reference_tail",
        "z_score": 10.464523156611106
      },
      {
        "feature": "hip_flexion_rom_absolute_difference",
        "measured_value": 17.570111463554,
        "reference_mean": 2.6317642214056227,
        "reference_p05": 0.216232544,
        "reference_p95": 6.347048854,
        "reference_percentile": 99.59839357429718,
        "reference_std": 2.1686027513053947,
        "reference_tail": "high_reference_tail",
        "z_score": 6.888466425285225
      },
      {
        "feature": "hip_flexion_rom_percent_difference",
        "measured_value": 16.31386777811092,
        "reference_mean": 3.1858494657454215,
        "reference_p05": 0.2968869241,
        "reference_p95": 8.3423260752,
        "reference_percentile": 99.59839357429718,
        "reference_std": 2.859468135729925,
        "reference_tail": "high_reference_tail",
        "z_score": 4.591069978478484
      },
      {
        "feature": "hip_flexion_rom_symmetry_index",
        "measured_value": 16.31386777811092,
        "reference_mean": -0.8390409840618873,
        "reference_p05": -7.6244369832,
        "reference_p95": 5.4695670774,
        "reference_percentile": 100.0,
        "reference_std": 4.197881020790087,
        "reference_tail": "high_reference_tail",
        "z_score": 4.086087403912283
      }
    ],
    "title": "Bilateral ROM symmetry features from Prompt 11."
  }
]
```

## Feature Table

```json
[
  {
    "ankle_angle_left_maximum": 150.529009126214,
    "ankle_angle_left_mean": 126.54317967055776,
    "ankle_angle_left_median": 132.58053212136224,
    "ankle_angle_left_minimum": 72.19981007013389,
    "ankle_angle_left_rom": 78.3291990560801,
    "ankle_angle_left_std": 14.068765882597658,
    "ankle_angle_left_time_to_peak": 1.7666666666666666,
    "ankle_angle_left_variance": 197.93017345934388,
    "ankle_angle_right_maximum": 144.21801748767453,
    "ankle_angle_right_mean": 131.81505316996308,
    "ankle_angle_right_median": 134.39072634236015,
    "ankle_angle_right_minimum": 98.3313135812712,
    "ankle_angle_right_rom": 45.886703906403326,
    "ankle_angle_right_std": 9.462210118808866,
    "ankle_angle_right_time_to_peak": 2.1333333333333333,
    "ankle_angle_right_variance": 89.53342033248889,
    "ankle_angle_rom_absolute_difference": 32.44249514967677,
    "ankle_angle_rom_percent_difference": 52.23565481704108,
    "ankle_angle_rom_symmetry_index": 52.23565481704108,
    "condition": "uploaded",
    "hip_flexion_left_maximum": 124.06814800640889,
    "hip_flexion_left_mean": 57.27976787841774,
    "hip_flexion_left_median": 43.94372065874492,
    "hip_flexion_left_minimum": 7.582627231457762,
    "hip_flexion_left_rom": 116.48552077495113,
    "hip_flexion_left_std": 34.408855576462464,
    "hip_flexion_left_time_to_peak": 0.8333333333333334,
    "hip_flexion_left_variance": 1183.969342081852,
    "hip_flexion_right_maximum": 117.22206249273226,
    "hip_flexion_right_mean": 59.58495220507899,
    "hip_flexion_right_median": 46.852711516154386,
    "hip_flexion_right_minimum": 18.306653181335143,
    "hip_flexion_right_rom": 98.91540931139713,
    "hip_flexion_right_std": 31.54999937926808,
    "hip_flexion_right_time_to_peak": 0.7333333333333333,
    "hip_flexion_right_variance": 995.4024608318161,
    "hip_flexion_rom_absolute_difference": 17.570111463554,
    "hip_flexion_rom_percent_difference": 16.31386777811092,
    "hip_flexion_rom_symmetry_index": 16.31386777811092,
    "is_empty": false,
    "knee_flexion_left_maximum": 176.18723618264826,
    "knee_flexion_left_mean": 147.33696204653626,
    "knee_flexion_left_median": 150.15560911273576,
    "knee_flexion_left_minimum": 98.01706481004888,
    "knee_flexion_left_rom": 78.17017137259938,
    "knee_flexion_left_std": 22.307654332537986,
    "knee_flexion_left_time_to_peak": 0.06666666666666667,
    "knee_flexion_left_variance": 497.63144182000076,
    "knee_flexion_right_maximum": 161.09189308968956,
    "knee_flexion_right_mean": 132.23071564016576,
    "knee_flexion_right_median": 140.38244810457712,
    "knee_flexion_right_minimum": 82.25714233575171,
    "knee_flexion_right_rom": 78.83475075393785,
    "knee_flexion_right_std": 22.394912005183826,
    "knee_flexion_right_time_to_peak": 0.3333333333333333,
    "knee_flexion_right_variance": 501.53208371992673,
    "knee_flexion_rom_absolute_difference": 0.6645793813384699,
    "knee_flexion_rom_percent_difference": 0.8465713970455728,
    "knee_flexion_rom_symmetry_index": -0.8465713970455728,
    "participant_id": null,
    "trial_name": "jump.mp4",
    "trial_slot": 1
  }
]
```
