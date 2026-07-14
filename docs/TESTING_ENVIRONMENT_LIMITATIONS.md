# Interactive Testing Environment Known Limitations

- The viewer reports frame-level MediaPipe-derived geometric measurements only.
- The app does not infer landing events, initial contact, toe off, peak landing, or peak knee flexion events.
- The app does not generate athlete reports, evidence observations, reference comparisons, ACL predictions, diagnosis, or recommendations.
- Frame-level symmetry values are transparent left/right scalar comparisons for the selected frame; they are not clinical asymmetry thresholds.
- Frame-to-frame delta values describe change from the previous processed frame; the first processed frame has no previous-frame delta.
- Browser video seeking can be codec-dependent. The measurement panel remains tied to the selected processed frame index.
- The annotated video uses the existing annotation exporter; additional angle text is presented in the synchronized HTML overlay.
- Missing landmarks and NaN measurements are preserved rather than estimated.
- Processing speed depends on local hardware and video length.
- Future config fields for model selection or confidence thresholds remain placeholders until validated modules wire them in.
