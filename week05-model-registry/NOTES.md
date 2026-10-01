# NOTES.md — Week 5: Model Registry Governance

**Student ID used with `generate_for_student.py`: 142602024**

**seed: 2326432752**

## Which candidate reached Production, and why?

`candidate_b` reached Production as version `v2`. The registry first blocked `candidate_a` because it did not have a model card, demonstrating the governance requirement that a model must have a complete model card before Production promotion. After the model card was available, `candidate_a` was blocked again because its F1 score was `0.493`, which is below the Production threshold of `0.70`.

`candidate_b` cleared the required F1 quality threshold and had a completed model card, so both Production gates were satisfied. It was therefore successfully promoted to Production as `v2`. The registry also records the stage transition in the model's history.

## Gating stale feature data

To block promotion of a model trained on stale feature data, I would add a feature-data freshness check to `promote_model`. The model's metadata or model card would need to record the date or timestamp of the feature data used for training.

Before allowing Production promotion, `promote_model` could calculate the age of the training feature data and reject the promotion if it is older than 30 days. For example, the gate could check whether `current_time - training_data_timestamp > 30 days` and raise a `GovernanceError` explaining that the training data is stale.

This would add another independent governance condition alongside the existing model-card and F1 checks.

## Scaling the gate to 40 candidates

The basic design does not need to change to support 40 candidates. `register_model` already creates a new immutable version for each registration (`v1`, `v2`, etc.), so the same mechanism can register 40 candidates without treating them differently from two candidates.

`promote_model` also applies its governance checks to whichever specific model version is being promoted. Therefore, the same model-card and F1 gates can be applied independently to all 40 candidates. A search or AutoML system could register all 40 candidates, and only candidates satisfying the governance requirements could be promoted.

The main thing that might need to change at larger scale is the workflow around candidate selection—for example, adding automated evaluation, ranking, or batch processing so that all 40 candidates can be checked efficiently. The core registry and promotion gate itself does not need a different rule just because there are more candidates.
