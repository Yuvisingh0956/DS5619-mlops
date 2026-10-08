# Week 7 — CI/CD Integration Testing

## Objective

The objective of this assignment is to implement a **CI/CD pipeline** that automatically verifies the vehicle detection application before changes are accepted. The pipeline performs:

1. **Linting** using Flake8.
2. **Unit testing** using Pytest.
3. **Integration testing** using the actual Docker container.

The integration test runs only after linting and unit tests pass.

## Steps Followed

1. Generated student-specific test fixtures:

   ```bash
   python3 generate_for_student.py --student-id 142602024
   ```

2. Implemented the GitHub Actions workflow in `.github/workflows/ci.yml`.

3. Implemented `scripts/integration_test.sh` to:

   * Build the Docker image.
   * Start the container.
   * Check the `/health` endpoint.
   * Send a sample image to `/detect`.
   * Verify that detections are returned.
   * Clean up the container.

4. Ran the tests locally:

   ```bash
   flake8 src/
   pytest tests/ -q
   ./scripts/integration_test.sh
   ```

5. Configured GitHub Actions with three jobs:

   ```yaml
   lint
   unit-test
   integration-test
   ```

6. The integration job is gated using:

   ```yaml
   needs: ["lint", "unit-test"]
   ```

## Implementation

The main CI configuration runs:

```yaml
- name: Lint
  run: flake8 src/

- name: Run unit tests
  run: pytest tests/ -q

- name: Run integration test
  run: |
    chmod +x scripts/integration_test.sh
    ./scripts/integration_test.sh
```

The integration script builds and tests the real application container:

```bash
docker build -t week7-detector .
docker run -d -p 8080:8080 --name week7-detector-ci week7-detector

curl -sf http://localhost:8080/health

curl -sf \
  -F "image=@data/fixtures/camera_A_daylight/000.jpg" \
  http://localhost:8080/detect
```

## Result

Local validation completed successfully:

* **Flake8:** Passed
* **Pytest:** 12/12 tests passed
* **Docker integration test:** Passed
* **GitHub Actions:** `lint`, `unit-test`, and `integration-test` passed successfully.
