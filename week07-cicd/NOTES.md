# NOTES.md — Week 7: CI/CD Integration Testing

**Student ID used with `generate_for_student.py`:**
142602024

**Generated seed:**
1975192383


## Why gate integration-test on needs: [lint, unit-test]?

The integration-test job builds a Docker image, starts a container, waits for
the application to become healthy, and then performs HTTP integration tests.
These steps consume additional CI time and resources.

Using `needs: ["lint", "unit-test"]` ensures that the Docker build and
integration test only run after both linting and unit tests have passed.
Otherwise, CI could waste time building and running a container when the
code has already failed an earlier check.