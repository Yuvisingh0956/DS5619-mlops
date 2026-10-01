# Lab 5 — Model Registry Governance

**Track A — Tabular Fraud Detection**
**Course:** DS5619 Machine Learning Systems Operations
**Week:** 5
**Student ID:** 142602024

---

## 1. Overview

This lab implements a **minimal local model registry** for a fraud-detection system.

The purpose of the lab is to demonstrate how a model registry can act as both:

1. An **artifact store** for trained model versions.
2. A **governance system** that controls which model versions are allowed to reach Production.

The registry implemented in this assignment does not require MLflow, Weights & Biases, or another external model-management server. Everything is stored locally as JSON files and directories.

The registry enforces two important Production governance rules:

* A model must have a **complete model card** before it can be promoted to Production.
* The model must have an **F1 score of at least 0.70** before it can be promoted to Production.

The lab also demonstrates model versioning, stage transitions, audit history, automatic archiving of previous Production models, and lookup of the model currently running in Production.

---

# 2. Learning Objective

The main objective is to understand that a model registry is more than a place to store model files.

The registry provides a controlled answer to:

> **"Which model is actually in Production right now?"**

It also ensures that a model cannot be promoted simply because someone decided it should be deployed.

The registry implemented here enforces governance rules as code.

The main concepts demonstrated are:

* Model artifact storage
* Model versioning
* Model cards
* Quality gates
* Production promotion
* Stage transitions
* Audit history
* Automatic archiving
* Production model lookup

The lab follows the idea that model development or hyperparameter search may produce many candidate models, but the registry is responsible for controlling what happens **after candidate generation**.

---

# 3. Assignment Structure

The assignment contains two personalized candidate models:

```text
candidate_a
candidate_b
```

Both candidates are already trained models for a simple fraud-detection problem.

The models use a deliberately simple **transaction amount threshold** approach.

One candidate is designed to fail the Production F1 requirement, while the other clears it.

The candidates and their metrics are generated deterministically from the student's ID using:

```bash
python generate_for_student.py --student-id <student-id>
```

For this submission, the student ID used was:

```text
142602024
```

The generated candidate data should not be manually modified.

---

# 4. Project Files

The important files in the project are:

```text
week05-model-registry/
│
├── src/
│   ├── mini_model_registry.py
│   └── run_pipeline.py
│
├── data/
│   ├── candidate_a/
│   │   ├── model.json
│   │   └── metrics.json
│   │
│   └── candidate_b/
│       ├── model.json
│       └── metrics.json
│
├── model_card_fields.json
├── registry_summary.json
├── NOTES.md
├── tests/
│   └── test_smoke.py
│
└── .model_registry/
```

---

# 5. Candidate Models

The lab provides two candidate fraud-detection models.

Each candidate contains:

```text
model.json
metrics.json
```

The model itself is intentionally simple: it uses a transaction amount threshold to classify transactions.

The two candidates have different thresholds and metric values because the data is generated from the student's student ID.

For this submission:

```text
candidate_a F1 = 0.493
candidate_b = clears the 0.70 Production F1 threshold
```

Therefore, candidate A cannot reach Production, while candidate B can.

---

# 6. Model Registry

The core implementation is located in:

```text
src/mini_model_registry.py
```

The registry provides four main functions:

```python
register_model()
generate_model_card()
promote_model()
get_production_model()
```

These functions represent the four major responsibilities of the local registry.

---

# 7. `register_model()`

## Purpose

`register_model()` acts as the **artifact store**.

It takes:

```python
register_model(
    name,
    model_path,
    metrics,
    registry_dir
)
```

and creates a new immutable version of the model.

For example:

```text
candidate_a → v1
candidate_b → v2
```

The next registration of the same model would become:

```text
v3
```

and then:

```text
v4
```

This ensures that previous model versions are not overwritten.

---

## Versioning

The helper function:

```python
_next_version_id()
```

looks at existing version directories and determines the next available version.

For example:

```text
v1
v2
v3
```

results in the next version:

```text
v4
```

This allows the registry to maintain an immutable history of registered models.

---

## Registry Version Structure

A registered model has a structure similar to:

```text
.model_registry/
└── models/
    └── fraud-detector/
        ├── v1/
        │   ├── model.json
        │   ├── metrics.json
        │   └── manifest.json
        │
        └── v2/
            ├── model.json
            ├── metrics.json
            └── manifest.json
```

Each version is independent.

---

# 8. Manifest

Every registered version receives a:

```text
manifest.json
```

The manifest stores important registry metadata.

It includes information such as:

```json
{
  "version_id": "v2",
  "name": "fraud-detector",
  "metrics": {
    "f1": 0.8
  },
  "stage": "None",
  "created_at": "..."
}
```

The initial stage is:

```text
None
```

because registering a model does not automatically mean that the model is ready for deployment.

---

# 9. `generate_model_card()`

## Purpose

The model card is the **governance record** associated with a model version.

The function:

```python
generate_model_card()
```

creates:

```text
model_card.json
```

for a registered model version.

The registry requires four fields:

```text
intended_use
training_data
limitations
ethical_considerations
```

---

## Model Card Validation

The function does not simply check whether a model card file exists.

It verifies that every required field:

* exists,
* is a string,
* is not empty,
* does not contain `TODO`.

Therefore, an incomplete card is rejected.

For example:

```json
{
  "intended_use": "TODO: explain the model"
}
```

is not considered a valid model card.

This implements the governance principle:

> A model card must actually be filled in rather than merely being present.

---

# 10. Model Card Content

The completed model card describes:

### Intended Use

The model is intended to flag potentially fraudulent card transactions based primarily on transaction amount.

It supports a fraud-detection system and should assist with review rather than being treated as the sole decision-maker.

### Training Data

The model is associated with the Week 4 `card_activity` feature group.

The model's coverage is limited to the transaction activity represented by that feature group.

### Limitations

The model is a simple amount-threshold classifier.

It cannot reliably detect fraud patterns based on factors such as:

* location,
* transaction sequence,
* account takeover behavior,
* sophisticated low-value fraud.

### Ethical Considerations

A false positive can cause a legitimate transaction to be blocked or reviewed.

A false negative can allow fraudulent activity to proceed and cause financial loss.

Therefore, both types of errors need to be considered.

---

# 11. `promote_model()`

## Purpose

`promote_model()` is the main **governance gate**.

It moves a model version between stages:

```text
None
Staging
Production
Archived
```

The function is:

```python
promote_model(
    name,
    version_id,
    target_stage,
    registry_dir
)
```

---

# 12. Production Governance Gates

Promotion to Production requires **both** conditions to be satisfied.

## Gate 1 — Model Card

The model must have:

```text
model_card.json
```

If it does not, promotion is blocked.

For example:

```text
Promotion blocked: fraud-detector/v1 does not have a model card.
```

---

## Gate 2 — F1 Score

The model's F1 score must satisfy:

```text
F1 >= 0.70
```

The threshold is defined as:

```python
PRODUCTION_F1_THRESHOLD = 0.70
```

If the F1 score is below the threshold, Production promotion is rejected.

For candidate A:

```text
F1 = 0.493
```

Therefore:

```text
0.493 < 0.70
```

and the model is rejected.

---

# 13. Independent Governance Checks

The two Production gates are checked independently.

This is important because:

* A model with a good F1 score but no model card must still be blocked.
* A model with a complete model card but insufficient F1 must also be blocked.

The registry therefore prevents both governance failures.

---

# 14. Production Archiving

The registry guarantees that there is only one current Production version for a model.

When a new version is successfully promoted to Production, the registry scans other versions.

If another version currently has:

```text
stage = Production
```

that version is changed to:

```text
stage = Archived
```

This prevents multiple versions of the same model from simultaneously being considered the current Production model.

---

# 15. Audit History

Every successful stage transition is recorded in:

```text
manifest["history"]
```

For example:

```json
"history": [
  {
    "from_stage": "None",
    "to_stage": "Production",
    "at": "2026-09-01T05:12:59+00:00"
  }
]
```

This provides an audit trail showing how the model moved through the registry.

If a Production model is later archived, that transition is also recorded.

---

# 16. `get_production_model()`

The function:

```python
get_production_model()
```

answers:

> Which model version is actually in Production right now?

It scans all registered versions and checks their manifests.

If it finds:

```text
stage = Production
```

it returns that version's manifest.

If there is no Production model, it returns:

```python
None
```

This means Production status is determined from registry artifacts rather than from memory, a Slack message, or an external informal record.

---

# 17. Model Card Input File

The file:

```text
model_card_fields.json
```

contains the content used to generate the model card.

All `TODO` placeholders were replaced with actual answers.

The pipeline refuses to run while placeholders remain, ensuring that the governance requirement is enforced before the model reaches the registry pipeline.

---

# 18. Pipeline

The complete workflow is handled by:

```text
src/run_pipeline.py
```

The pipeline:

1. Loads candidate A.
2. Loads candidate B.
3. Registers both candidates.
4. Attempts to promote candidate A without a model card.
5. Demonstrates that the first governance gate blocks it.
6. Creates the required model card.
7. Attempts to promote candidate A again.
8. Demonstrates that its F1 score is below the Production threshold.
9. Creates the model card for candidate B.
10. Promotes candidate B to Production.
11. Writes the final `registry_summary.json`.

The pipeline therefore demonstrates both successful and unsuccessful governance decisions.

---

# 19. Actual Pipeline Result

The successful pipeline run produced:

```text
Registered candidate_a as v1, candidate_b as v2
```

Candidate A was first rejected because it did not have a model card:

```text
[expected] promoting v1 with no card was blocked:
Promotion blocked: fraud-detector/v1 does not have a model card.
```

Candidate A was then rejected because its F1 score was too low:

```text
[expected] promoting v1 with f1 below threshold was blocked:
Promotion blocked: f1=0.493 is below production threshold 0.70.
```

Candidate B successfully passed the Production gates:

```text
Promoted v2 to Production.
```

The registry recorded the transition:

```text
from_stage: None
to_stage: Production
```

Finally:

```text
registry_summary.json
```

was generated with:

```text
production version is v2
```

Therefore, the final Production model is:

```text
fraud-detector v2
```

---

# 20. Registry Summary

The pipeline generates:

```text
registry_summary.json
```

This file provides a concise summary of the model currently in Production.

It is useful because it provides a machine-readable record of the Production state.

The important result for this submission is:

```text
Production model: v2
```

---

# 21. Testing

The assignment includes automated smoke tests.

They are run using:

```bash
pytest tests/ -q
```

The tests verify important registry behavior including:

* Model registration
* Versioning
* Model-card generation
* Model-card validation
* Production governance
* F1 threshold enforcement
* Production lookup
* Archiving behavior

After fixing the model-card structure, the implementation should be validated with the complete test suite before submission.

---

# 22. Handling Stale Feature Data

An additional governance rule that could be added is a **feature-data freshness gate**.

For example, the model metadata could store:

```text
training_data_timestamp
```

When Production promotion is attempted, `promote_model()` could calculate:

```text
current_time - training_data_timestamp
```

If the training data is older than 30 days, promotion could be rejected.

Conceptually:

```text
If training data age > 30 days:
    block Production promotion
```

This would become another independent Production governance condition alongside:

```text
Complete model card
F1 >= 0.70
Fresh training data
```

---

# 23. Scaling to 40 Candidates

The registry design does not fundamentally need to change if an AutoML or hyperparameter search produces 40 candidates instead of 2.

`register_model()` already creates independent versions:

```text
v1
v2
v3
...
v40
```

Each candidate can therefore be registered independently.

`promote_model()` operates on a particular model version and applies the same governance rules.

Therefore, the same gates can be applied to all 40 candidates.

The main improvement that may be useful at larger scale is automation around candidate evaluation and selection.

For example:

```text
40 candidates
      ↓
Register all versions
      ↓
Evaluate metrics
      ↓
Generate/validate model cards
      ↓
Apply governance gates
      ↓
Promote only qualifying candidates
```

The core registry logic itself does not need a separate implementation for 40 candidates.

---

# 24. Key Design Principles Demonstrated

This lab demonstrates several important MLOps principles.

## Immutable Versioning

Every registration receives a new version rather than overwriting an existing model.

```text
v1 → v2 → v3 → ...
```

## Governance as Code

Production requirements are enforced programmatically rather than relying only on documentation or manual decisions.

## Model Cards as Governance Records

A model card documents:

* intended use,
* training data,
* limitations,
* ethical considerations.

## Quality Gates

A model cannot reach Production unless it meets the required F1 threshold.

## Single Production Answer

The registry automatically archives the previous Production version when a new one is promoted.

Therefore, there is always a clear answer to:

> What model is currently in Production?

## Auditability

Stage transitions are stored in the manifest history.

---

# 25. Final Workflow

The complete workflow can be summarized as:

```text
Student ID
    ↓
generate_for_student.py
    ↓
Personalized candidate models
    ↓
candidate_a + candidate_b
    ↓
register_model()
    ↓
Immutable registry versions
    ↓
Generate model cards
    ↓
promote_model()
    ↓
 ┌───────────────────────────────┐
 │ Production governance gates   │
 │                               │
 │ Complete model card?          │
 │ F1 >= 0.70?                   │
 └───────────────────────────────┘
       ↓                 ↓
     FAIL              PASS
       ↓                 ↓
    Block          Production
                         ↓
                  Archive old
                  Production
                         ↓
                Update history
                         ↓
             registry_summary.json
```

---

# 26. Final Result

For this submission:

| Candidate        |            F1 Result | Model Card                | Production   |
| ---------------- | -------------------: | ------------------------- | ------------ |
| candidate_a / v1 |                0.493 | Required before promotion | ❌ Rejected   |
| candidate_b / v2 | Above 0.70 threshold | Complete                  | ✅ Production |

The final Production model is:

```text
fraud-detector / v2
```

The assignment therefore demonstrates that the registry does not simply store models—it **controls their movement into Production using explicit governance rules**.

---

# 27. How to Run

Activate the virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate the personalized candidate data:

```bash
python generate_for_student.py --student-id 142602024
```

Run the registry pipeline:

```bash
python src/run_pipeline.py
```

Run the tests:

```bash
pytest tests/ -q
```

---

# 28. Submission

The required submission artifacts are:

```text
src/mini_model_registry.py
model_card_fields.json
.model_registry/
registry_summary.json
NOTES.md
README.md
```

The final submission can be committed using:

```bash
git add -A
git commit -m "Week 5: model registry governance"
git tag week05-submit
git push origin main --tags
```

---

# 29. Conclusion

This lab implements a small but functional model registry that demonstrates the core governance concepts required for deploying machine-learning models responsibly.

The most important idea is that **registration and deployment are separate operations**.

A candidate can be registered without being Production-ready. Promotion is controlled by explicit governance gates.

In this assignment:

* Candidate A was registered but rejected because its F1 score was below the Production threshold.
* Candidate B satisfied the required governance conditions and was promoted.
* The previous Production version would automatically be archived whenever a new version is promoted.
* Model-card information and promotion history are stored as registry artifacts.
* `get_production_model()` provides a reliable programmatic answer to what is currently in Production.

Thus, the registry acts as both an **artifact store and a governance control system**, providing a reproducible and auditable path from trained model candidate to Production deployment.
