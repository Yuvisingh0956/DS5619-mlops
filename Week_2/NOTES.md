# NOTES.md — Week 2: Config-Driven Data Pipelines

**Student ID used with `generate_for_student.py`:**
142602024

## What was hardcoded, and what would switching it have required?

<!-- What specifically was hardcoded in the original script, and what would
     have had to happen to change the threshold or switch formats before
     your refactor? -->

The original pipeline hardcoded the input file path, input format, high-value threshold, and output file path.
It also had separate logic tied to the specific input format instead of making the format configurable.
Before the refactor, changing the high-value threshold required editing the Python source code.
Switching from CSV to JSON also required modifying the source code to change how transactions were loaded.
After the refactor, these values are controlled through the YAML configuration file.
The pipeline now supports both CSV and JSON without modifying `pipeline.py`.
For the current configuration, the high-value threshold is 1000.
