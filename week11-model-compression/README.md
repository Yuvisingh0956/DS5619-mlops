# Week 11 — Model Compression Benchmark

## Objective
The objective of this assignment is to implement and benchmark model compression techniques, including magnitude-based pruning and INT8 quantization, by comparing model size, accuracy, and inference latency.

## Implementation
The assignment includes:
- **Model size calculation:** Calculates storage requirements based on bytes per weight.
- **Magnitude-based pruning:** Sets the smallest-magnitude weights to zero.
- **Sparse COO storage:** Calculates storage requirements for non-zero weights and their indices.
- **INT8 quantization:** Converts floating-point weights into signed 8-bit integers.
- **Model benchmarking:** Measures model size, classification accuracy, and average inference latency.

The benchmark compares four variants: baseline FP32, pruned dense FP32, pruned sparse COO, and INT8 quantized.

## Results
- Baseline FP32 achieved **100% accuracy** with a size of 1,024 bytes.
- Pruned dense FP32 achieved **99.67% accuracy** with a size of 1,024 bytes.
- Pruned sparse COO achieved **99.67% accuracy** with a size of 616 bytes.
- INT8 quantization achieved **100% accuracy** with a size of 256 bytes.

All **13 tests passed** successfully.

## Steps to Run

1. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Generate student-specific data:

   ```bash
   python generate_for_student.py --student-id 142602024
   ```

3. Run the benchmark pipeline:

   ```bash
   python src/run_pipeline.py
   ```

4. Run the tests:

   ```bash
   pytest tests/ -q
   ```

The pipeline generates `compression_report.json`, containing the benchmark results for all four model variants.

## Conclusion
The experiment demonstrates that pruning does not reduce dense model storage by itself, while sparse storage and INT8 quantization can significantly reduce storage requirements. Compression techniques must be evaluated in terms of both storage efficiency and predictive accuracy.