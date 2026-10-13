# Week 10 — Fairness and Robustness Audit

## Objective
Audit the mock vehicle detector for per-class recall disparities, then test how small adversarial colour perturbations affect each class.

## Implementation
- Implemented IoU and ground-truth matching to determine whether each annotated vehicle was detected.
- Calculated recall for each vehicle class and flagged classes below the 90% threshold.
- Applied FGSM-style colour perturbations (`eps = 0, 10, 20, 30, 40`) and compared recall drops.
- Saved the results to `fairness_report.json` and documented findings in `NOTES.md`.

## Results
Using student ID `142602024` (seed `950835326`), the clean audit flagged:
- Bicycle: **80.0%**
- Two-wheeler: **80.0%**
- Three-wheeler: **85.7%**

At `eps = 20`, **SUV** had the largest recall drop (**35.71%**). **Bicycle** had the lowest recall under attack (**46.7%**), followed by Two-wheeler (**60.0%**) and Hatchback (**62.5%**).

## How to Run
Run these commands from the project root:

```bash
python -m venv .venv
# Activate the environment:
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
python generate_for_student.py --student-id 142602024
python src/run_pipeline.py
pytest tests/ -q
```

The generator creates the personalized fixtures, the pipeline writes `fairness_report.json`, and pytest runs the available checks.
