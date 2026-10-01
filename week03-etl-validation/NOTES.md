# NOTES.md — Week 3: ETL and Data Validation

**Student ID used with `generate_for_student.py`: 142602024**
<!-- paste the --student-id value you used -->


## Quarantine count vs. the 7 known injected problems

<!-- How many rows ended up quarantined, and does that match the 7 known
     injected problems? (It won't match exactly — some rows may trip more
     than one expectation. Explain the discrepancy if there is one.) -->
The ETL pipeline quarantined 6 rows out of 600.

The validation report contains 8 individual violations:
- 2 null amount violations
- 1 null card_id violation
- 3 non-positive amount violations
- 1 invalid merchant category violation
- 1 duplicate transaction_id violation

The number of quarantined rows is 6 rather than 8 because rows 49 and 60
each violate two expectations (null amount and positive amount). Therefore,
8 individual violations occur across 6 unique rows.

The result is 594 clean rows + 6 quarantined rows = 600 total rows.