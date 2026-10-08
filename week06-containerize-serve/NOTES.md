# NOTES.md — Week 6: Containerize and Serve a Detector

**Student ID used with `generate_for_student.py`: 142602024**
<!-- paste the --student-id value you used -->


## Built image size

<!-- What image size did `docker images` report for week6-detector? -->
student_id: 142602024
seed: 1222374546
Wrote 6 images across 2 camera profiles
Wrote 18 annotations

The docker images week6-detector command reported: 166MB

## Swapping in a real checkpoint

<!-- What's the single biggest thing you'd change about this Dockerfile if
     src/mock_detector.py were swapped for a real torch-based checkpoint?
     (Think about what that does to build time and image size.) -->
The biggest change I would make if src/mock_detector.py were swapped for a real
torch-based checkpoint would be to use a PyTorch/CUDA-appropriate base image and
install the required Torch and model dependencies.

A real Torch-based checkpoint would significantly increase both Docker build
time and final image size compared with the current lightweight mock detector.
Therefore, the Dockerfile would need to be designed around those heavier runtime
dependencies, particularly if GPU inference were required.