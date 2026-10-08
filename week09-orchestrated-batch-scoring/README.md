# Week 9 — Orchestrated Batch Scoring

## Objective

Implement a lightweight DAG orchestrator to demonstrate:

- **Task dependency management** using topological ordering.
- **Per-task retry handling** for transient failures.
- **Shared context** between dependent tasks.

The DAG used in this assignment is:

```text
extract → score → load
              ↘ notify
```

## Implementation

Implemented the three functions in `src/mini_orchestrator.py`:

- `topological_order()` — uses Kahn's algorithm and detects cycles/missing dependencies.
- `run_task_with_retry()` — retries failed tasks up to the configured retry limit.
- `run_dag()` — executes tasks in dependency order, shares context, records results, and stops after an unrecoverable failure.

The `notify` task intentionally fails twice and succeeds on the third attempt, demonstrating the retry mechanism. The pipeline execution completed successfully with `notify` taking **3 attempts**.

## Commands

### 1. Create environment

```bash
python -m venv .venv
```

Activate:

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate personalized fixtures

```bash
python generate_for_student.py --student-id 142602024
```

### 4. Run the pipeline

```bash
python src/run_pipeline.py
```

### 5. Run tests

```bash
pytest tests/ -q
```

## Output

The pipeline generates:

- `batch_report.json`
- `dag_run_summary.json`

The successful run produced:

```text
extract: success — 1 attempt
score:   success — 1 attempt
load:    success — 1 attempt
notify:  success — 3 attempts
```