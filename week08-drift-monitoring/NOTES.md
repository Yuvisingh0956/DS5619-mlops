# NOTES.md — Week 8: Drift and Observability Monitoring

**Student ID used with `generate_for_student.py`: 142602024**

seed: 3203669310

Wrote 40 images across 2 camera profiles -> `data/fixtures`

Wrote 151 annotations -> `data/fixtures/_annotations.coco.json`

Sanity-checked PSI (using the mock detector, not `drift_monitor.py`): 0.1300

## Drift level vs. expectation

The report showed a **PSI of 0.13**, which corresponds to **moderate drift**.

The reference camera (`camera_A_daylight`) produced 79 confidence scores with a mean of 0.9759 and a standard deviation of 0.0367. The live camera (`camera_B_lowlight`) produced 71 confidence scores with a mean of 0.9788 and a standard deviation of 0.01.

Although the means are relatively close, the distributions are different, particularly in their spread and lower confidence values. The reference distribution has a minimum confidence of 0.654, while the live distribution has a minimum of 0.896.

A PSI of 0.13 falls between the moderate and significant thresholds, so the reported **moderate drift** is consistent with the expectation that the two cameras were deliberately constructed with different visual statistics.

## What confidence-score-only monitoring misses

Confidence-score monitoring can detect changes in the distribution of the detector's predictions, but it cannot directly tell us whether the detector's predictions are actually correct.

If ground-truth labels become available a day later, I would additionally monitor **performance drift**, such as changes in detection accuracy, precision, recall, and mAP.

This is important because confidence-score-only monitoring mainly captures changes in the model's prediction/feature distribution. It can indicate that the live data differs from the reference distribution, but it cannot reliably detect **concept drift** where the relationship between the input data and the correct target changes while the confidence-score distribution remains similar.

Therefore, with delayed ground-truth labels, I would monitor both:

1. **Prediction/feature drift** using confidence-score distributions and PSI.
2. **Model performance drift** using ground-truth-based metrics such as precision, recall, and mAP.

This provides a more complete view of whether the deployed detector is continuing to perform correctly on live traffic.
