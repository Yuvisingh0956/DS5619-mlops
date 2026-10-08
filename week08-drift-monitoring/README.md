# Week 8 — Drift and Observability Monitoring

## Objective

The objective of this assignment is to implement **drift monitoring** for a vehicle detection system using the **Population Stability Index (PSI)**. The detector's confidence scores are treated as the monitored feature, with `camera_A_daylight` as the reference distribution and `camera_B_lowlight` as the live distribution.

## Implementation

The following four functions were implemented in `src/drift_monitor.py`:

* **`extract_confidence_scores()`**
  Loads every `.jpg` image, runs the provided mock detector, and collects the confidence score of every detection.

* **`compute_psi()`**
  Divides confidence scores into 10 equal-width bins from 0 to 1, calculates the distribution in each bin, and computes PSI:

  $$
  PSI = \sum (Live\% - Reference\%)\ln\left(\frac{Live\%}{Reference\%}\right)
  $$

* **`classify_drift()`**
  Classifies drift using the given thresholds:

  * PSI < 0.10 → `none`
  * 0.10 ≤ PSI < 0.25 → `moderate`
  * PSI ≥ 0.25 → `significant`

* **`summarize_scores()`**
  Calculates count, mean, standard deviation, minimum, and maximum confidence scores. For a single score, standard deviation is set to `0.0`.

The completed pipeline compares the two camera distributions and writes the results to `drift_report.json`.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate the personalized fixtures:

```bash
python generate_for_student.py --student-id 142602024
```

## Run the Pipeline

```bash
python src/run_pipeline.py
```

This generates:

```text
drift_report.json
```

## Testing

Run the provided tests:

```bash
pytest tests/ -q
```

## Result

For this submission:

```text
PSI = 0.13
Drift Level = moderate
```

The moderate drift indicates that the live confidence-score distribution differs from the reference distribution.

**Student ID:** `142602024`
