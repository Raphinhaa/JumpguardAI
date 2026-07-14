# Standards Matrix

| Feature | Literature definition | JumpGuard formula | Match status | Confidence | References |
|---|---|---|---|---|---|
| `hip_flexion_right_mean` | Average full-recording joint-angle magnitude. | `Σx / N` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `hip_flexion_right_median` | Median full-recording joint-angle magnitude. | `median(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `hip_flexion_right_std` | Full-recording angular variability as population standard deviation. | `sqrt(Σ(x-mean)² / N)` | Verified Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; Atkinson and Nevill 1998 |
| `hip_flexion_right_variance` | Full-recording angular variability as population variance. | `Σ(x-mean)² / N` | Verified Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; Atkinson and Nevill 1998 |
| `hip_flexion_right_maximum` | Maximum full-recording joint-angle value. | `max(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `hip_flexion_right_minimum` | Minimum full-recording joint-angle value. | `min(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `hip_flexion_right_rom` | Full-recording angular excursion computed as maximum minus minimum. | `max(x) - min(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `hip_flexion_right_time_to_peak` | Elapsed time from recording start to first maximum; event-relative meaning is inconclusive. | `time[argmax(x)] - time[0]` | Partial Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; event-specific interpretation inconclusive |
| `hip_flexion_left_mean` | Average full-recording joint-angle magnitude. | `Σx / N` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `hip_flexion_left_median` | Median full-recording joint-angle magnitude. | `median(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `hip_flexion_left_std` | Full-recording angular variability as population standard deviation. | `sqrt(Σ(x-mean)² / N)` | Verified Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; Atkinson and Nevill 1998 |
| `hip_flexion_left_variance` | Full-recording angular variability as population variance. | `Σ(x-mean)² / N` | Verified Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; Atkinson and Nevill 1998 |
| `hip_flexion_left_maximum` | Maximum full-recording joint-angle value. | `max(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `hip_flexion_left_minimum` | Minimum full-recording joint-angle value. | `min(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `hip_flexion_left_rom` | Full-recording angular excursion computed as maximum minus minimum. | `max(x) - min(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `hip_flexion_left_time_to_peak` | Elapsed time from recording start to first maximum; event-relative meaning is inconclusive. | `time[argmax(x)] - time[0]` | Partial Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; event-specific interpretation inconclusive |
| `knee_flexion_right_mean` | Average full-recording joint-angle magnitude. | `Σx / N` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `knee_flexion_right_median` | Median full-recording joint-angle magnitude. | `median(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `knee_flexion_right_std` | Full-recording angular variability as population standard deviation. | `sqrt(Σ(x-mean)² / N)` | Verified Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; Atkinson and Nevill 1998 |
| `knee_flexion_right_variance` | Full-recording angular variability as population variance. | `Σ(x-mean)² / N` | Verified Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; Atkinson and Nevill 1998 |
| `knee_flexion_right_maximum` | Maximum full-recording joint-angle value. | `max(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `knee_flexion_right_minimum` | Minimum full-recording joint-angle value. | `min(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `knee_flexion_right_rom` | Full-recording angular excursion computed as maximum minus minimum. | `max(x) - min(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `knee_flexion_right_time_to_peak` | Elapsed time from recording start to first maximum; event-relative meaning is inconclusive. | `time[argmax(x)] - time[0]` | Partial Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; event-specific interpretation inconclusive |
| `knee_flexion_left_mean` | Average full-recording joint-angle magnitude. | `Σx / N` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `knee_flexion_left_median` | Median full-recording joint-angle magnitude. | `median(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `knee_flexion_left_std` | Full-recording angular variability as population standard deviation. | `sqrt(Σ(x-mean)² / N)` | Verified Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; Atkinson and Nevill 1998 |
| `knee_flexion_left_variance` | Full-recording angular variability as population variance. | `Σ(x-mean)² / N` | Verified Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; Atkinson and Nevill 1998 |
| `knee_flexion_left_maximum` | Maximum full-recording joint-angle value. | `max(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `knee_flexion_left_minimum` | Minimum full-recording joint-angle value. | `min(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `knee_flexion_left_rom` | Full-recording angular excursion computed as maximum minus minimum. | `max(x) - min(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `knee_flexion_left_time_to_peak` | Elapsed time from recording start to first maximum; event-relative meaning is inconclusive. | `time[argmax(x)] - time[0]` | Partial Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; event-specific interpretation inconclusive |
| `ankle_angle_right_mean` | Average full-recording joint-angle magnitude. | `Σx / N` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `ankle_angle_right_median` | Median full-recording joint-angle magnitude. | `median(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `ankle_angle_right_std` | Full-recording angular variability as population standard deviation. | `sqrt(Σ(x-mean)² / N)` | Verified Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; Atkinson and Nevill 1998 |
| `ankle_angle_right_variance` | Full-recording angular variability as population variance. | `Σ(x-mean)² / N` | Verified Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; Atkinson and Nevill 1998 |
| `ankle_angle_right_maximum` | Maximum full-recording joint-angle value. | `max(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `ankle_angle_right_minimum` | Minimum full-recording joint-angle value. | `min(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `ankle_angle_right_rom` | Full-recording angular excursion computed as maximum minus minimum. | `max(x) - min(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `ankle_angle_right_time_to_peak` | Elapsed time from recording start to first maximum; event-relative meaning is inconclusive. | `time[argmax(x)] - time[0]` | Partial Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; event-specific interpretation inconclusive |
| `ankle_angle_left_mean` | Average full-recording joint-angle magnitude. | `Σx / N` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `ankle_angle_left_median` | Median full-recording joint-angle magnitude. | `median(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `ankle_angle_left_std` | Full-recording angular variability as population standard deviation. | `sqrt(Σ(x-mean)² / N)` | Verified Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; Atkinson and Nevill 1998 |
| `ankle_angle_left_variance` | Full-recording angular variability as population variance. | `Σ(x-mean)² / N` | Verified Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; Atkinson and Nevill 1998 |
| `ankle_angle_left_maximum` | Maximum full-recording joint-angle value. | `max(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `ankle_angle_left_minimum` | Minimum full-recording joint-angle value. | `min(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `ankle_angle_left_rom` | Full-recording angular excursion computed as maximum minus minimum. | `max(x) - min(x)` | Verified Match | Moderate-to-high | Grood 1983; Wu 2002; Padua 2009; Hewett 2005 |
| `ankle_angle_left_time_to_peak` | Elapsed time from recording start to first maximum; event-relative meaning is inconclusive. | `time[argmax(x)] - time[0]` | Partial Match | Moderate | Grood 1983; Wu 2002; Padua 2009; Hewett 2005; event-specific interpretation inconclusive |
| `hip_flexion_rom_absolute_difference` | Unsigned bilateral ROM difference as a side-to-side symmetry descriptor. | `|ROM_L - ROM_R|` | Verified Match | Moderate | Soudan 1982; McCaw 1992; Atkinson and Nevill 1998 |
| `hip_flexion_rom_percent_difference` | Bilateral ROM asymmetry normalized to average side magnitude; formula conventions vary. | `100 × |ROM_L-ROM_R| / ((|ROM_L|+|ROM_R|)/2)` | Partial Match | Moderate | Soudan 1982; McCaw 1992; Atkinson and Nevill 1998 |
| `hip_flexion_rom_symmetry_index` | Signed bilateral ROM symmetry index; formula conventions vary. | `100 × (ROM_L-ROM_R) / ((|ROM_L|+|ROM_R|)/2)` | Partial Match | Moderate | Soudan 1982; McCaw 1992; Atkinson and Nevill 1998 |
| `knee_flexion_rom_absolute_difference` | Unsigned bilateral ROM difference as a side-to-side symmetry descriptor. | `|ROM_L - ROM_R|` | Verified Match | Moderate | Soudan 1982; McCaw 1992; Atkinson and Nevill 1998 |
| `knee_flexion_rom_percent_difference` | Bilateral ROM asymmetry normalized to average side magnitude; formula conventions vary. | `100 × |ROM_L-ROM_R| / ((|ROM_L|+|ROM_R|)/2)` | Partial Match | Moderate | Soudan 1982; McCaw 1992; Atkinson and Nevill 1998 |
| `knee_flexion_rom_symmetry_index` | Signed bilateral ROM symmetry index; formula conventions vary. | `100 × (ROM_L-ROM_R) / ((|ROM_L|+|ROM_R|)/2)` | Partial Match | Moderate | Soudan 1982; McCaw 1992; Atkinson and Nevill 1998 |
| `ankle_angle_rom_absolute_difference` | Unsigned bilateral ROM difference as a side-to-side symmetry descriptor. | `|ROM_L - ROM_R|` | Verified Match | Moderate | Soudan 1982; McCaw 1992; Atkinson and Nevill 1998 |
| `ankle_angle_rom_percent_difference` | Bilateral ROM asymmetry normalized to average side magnitude; formula conventions vary. | `100 × |ROM_L-ROM_R| / ((|ROM_L|+|ROM_R|)/2)` | Partial Match | Moderate | Soudan 1982; McCaw 1992; Atkinson and Nevill 1998 |
| `ankle_angle_rom_symmetry_index` | Signed bilateral ROM symmetry index; formula conventions vary. | `100 × (ROM_L-ROM_R) / ((|ROM_L|+|ROM_R|)/2)` | Partial Match | Moderate | Soudan 1982; McCaw 1992; Atkinson and Nevill 1998 |
