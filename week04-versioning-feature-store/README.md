# Week 4 — Versioning, Feature Store & Lineage

## Project Overview

This project implements a small, local, dependency-free feature store to demonstrate three important MLOps concepts:

* **Raw data versioning**
* **Feature group versioning**
* **Data lineage**

The project uses transaction data with two schema revisions (`v1` and `v2`). The v2 dataset contains a breaking upstream schema change, so the project demonstrates how to preserve the v1 history while creating new versions for v2.

All metadata is stored as JSON files under `.feature_store/`, making the versioning and lineage information transparent and easy to inspect.

## Project Workflow

The pipeline follows these main steps:

### 1. Raw Data Versioning

The transaction CSV files from `data/v1/` and `data/v2/` are registered as raw data versions.

A SHA-256 content hash is calculated for each file. If the same file content is registered again, the existing version ID is returned instead of creating a duplicate.

Each raw version stores a `manifest.json` containing information such as:

* Version ID
* Source file path
* Content hash
* Column names
* Row count
* Creation timestamp

### 2. Feature Engineering

Features are generated from the transaction records on a per-`card_id` basis.

The following features are produced:

* `txn_count`
* `avg_amount`
* `max_amount`
* `pct_card_present`
* `event_time`

The feature-building logic handles both input schemas.

For v1, the transaction amount is read from `amount`.

For v2, the amount is stored in `amount_minor_units`, so it is divided by 100 to convert it to the same unit as v1 before calculating aggregates.

The v2 schema change is therefore handled without changing the resulting feature schema.

### 3. Feature Group Registration

The generated features are registered under the feature group:

`card_activity`

Each registration creates a new version instead of overwriting an existing one.

Therefore, the pipeline maintains:

```text
card_activity/
├── v1/
└── v2/
```

Each feature-group version contains:

* `features.json` — the generated feature rows
* `manifest.json` — metadata and lineage information

### 4. Lineage Tracking

Each feature-group manifest records the raw data version from which the features were generated.

This allows the pipeline to trace:

```text
Feature Group Version
        ↓
Raw Data Version
        ↓
Original Source Data
```

The `get_lineage()` function reads both manifests and returns the complete lineage information.

### 5. Pipeline and Validation

`src/run_pipeline.py` runs the complete workflow:

1. Snapshot v1 raw data.
2. Build v1 features.
3. Register `card_activity` v1.
4. Snapshot v2 raw data.
5. Build v2 features while handling the schema change.
6. Register `card_activity` v2.
7. Re-snapshot v1 to verify idempotency.
8. Generate `lineage_report.json` containing the lineage of both feature-group versions.

## Repository Structure

```text
.
├── src/
│   ├── mini_feature_store.py
│   └── run_pipeline.py
│
├── data/
│   ├── v1/
│   │   └── transactions.csv
│   └── v2/
│       └── transactions.csv
│
├── .feature_store/
│   ├── raw_versions/
│   └── feature_groups/
│
├── lineage_report.json
├── NOTES.md
└── README.md
```

## Running the Project

Run the pipeline from the repository root:

```bash
python src/run_pipeline.py
```

Run the tests with:

```bash
pytest tests/ -q
```

## Core Idea

The main goal of the project is to make feature generation **versioned, reproducible, and traceable**.

Instead of replacing old data and features when the upstream schema changes, the project preserves history:

```text
Raw Data v1 ──→ Feature Group v1
     │
     │
Raw Data v2 ──→ Feature Group v2
```

This ensures that previous feature versions remain available and that every feature-group version can be traced back to the exact raw-data version that produced it.
