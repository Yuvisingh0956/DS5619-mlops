# Week 6 — Containerize and Serve a Detector

## Objective

The objective of this assignment was to containerize a Flask-based vehicle detection API and verify that it works correctly inside a Docker container. A lightweight mock detector was used instead of a real deep-learning checkpoint to keep the application dependency-light and suitable for testing.

## Setup

Create and activate a virtual environment, then install the required dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Generate the personalized synthetic dataset using the student ID:

```bash
python generate_for_student.py --student-id 142602024
```

## Usage

### Run Locally

Start the Flask application:

```bash
python src/app.py
```

In another terminal, verify the API:

```bash
curl http://localhost:8080/health
```

```bash
curl -F "image=@data/fixtures/camera_A_daylight/000.jpg" \
     http://localhost:8080/detect
```

### Run with Docker

Build the Docker image:

```bash
docker build -t week6-detector .
```

Run the container:

```bash
docker run --rm -p 8080:8080 week6-detector
```

Verify the endpoints:

```bash
curl http://localhost:8080/health
```

```bash
curl -F "image=@data/fixtures/camera_A_daylight/000.jpg" \
     http://localhost:8080/detect
```

Run the tests:

```bash
pytest tests/ -q
```

## Process Followed

1. Generated personalized synthetic CCTV images using student ID `142602024`.
2. Implemented the image upload, detection, and `/detect` API functionality.
3. Created a Docker image using `python:3.11-slim` and installed the required dependencies.
4. Tested the Flask application locally.
5. Ran the automated tests.
6. Built and ran the Docker container.
7. Verified both API endpoints against the running container.
8. Recorded the Docker verification details and image size.

## Results

* Personalized dataset: **6 images across 2 camera profiles**
* Generated annotations: **18**
* Pytest result: **4 passed**
* Docker build: **Successful**
* Docker image size: **166 MB**
* `/health`: **HTTP 200**, returned `{"status":"ok"}`
* `/detect`: **HTTP 200**, returned **2 detections** for the test image
* Docker container: **Successfully served both endpoints**

The complete Docker build, run, and API verification results are documented in `DOCKER_VERIFICATION.md`.
