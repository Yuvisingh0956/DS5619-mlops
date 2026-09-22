# CI verification

The CI pipeline was successfully verified on a real GitHub Actions runner.
All three required jobs passed successfully.

## Workflow run

Successful GitHub Actions run:

https://github.com/Yuvisingh0956/DS5619-mlops/actions/runs/35697124687

## Job summary

- `lint`: PASS
- `unit-test`: PASS
- `integration-test`: PASS

## What broke on the way there

The first GitHub Actions run failed because the Week 7 project is located
inside the `week07-cicd/` directory while the workflow initially looked for
`requirements.txt` from the repository root.

The workflow was fixed by setting `working-directory: week07-cicd` for the
Week 7 commands. After this change, all three CI jobs completed successfully.