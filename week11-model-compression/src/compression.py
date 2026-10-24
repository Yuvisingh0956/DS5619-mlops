
"""
A tiny, dependency-free model-compression benchmark.

Implements magnitude-based pruning, INT8 quantization, and benchmarking
of model size, accuracy, and latency.
"""

import time
import sys
import ctypes

# ---------------------------------------------------------------------------
# Given: prediction and dequantization
# ---------------------------------------------------------------------------

def predict(weights, features):
    """Predict 1 if the weighted sum is positive, otherwise 0."""
    score = sum(w * x for w, x in zip(weights, features))
    return 1 if score > 0 else 0


def dequantize_int8(quantized_weights, scale):
    """Convert quantized integer weights back to approximate floats."""
    return [q * scale for q in quantized_weights]


# ---------------------------------------------------------------------------
# Part 1 — Model size in bytes
# ---------------------------------------------------------------------------

def model_size_bytes(weights, dtype_bytes):
    """
    Return storage size in bytes for a dense model.

    Parameters:
        weights: List of model weights.
        dtype_bytes: Bytes used to store each weight.
                     FP32 = 4, FP16 = 2, INT8 = 1.
    """
    if dtype_bytes < 0:
        raise ValueError("dtype_bytes must be non-negative")

    return len(weights) * dtype_bytes


# ---------------------------------------------------------------------------
# Part 2 — Magnitude-based unstructured pruning
# ---------------------------------------------------------------------------

def prune_weights(weights, sparsity):
    """
    Return a NEW list in which the smallest-magnitude weights are zeroed.

    Example:
        sparsity = 0.7 means int(0.7 * len(weights)) weights are pruned.

    The input list is not modified.
    """
    if not 0.0 <= sparsity <= 1.0:
        raise ValueError("sparsity must be between 0.0 and 1.0")

    n_prune = int(sparsity * len(weights))

    # Identify indices of weights with the smallest absolute values.
    prune_indices = sorted(
        range(len(weights)),
        key=lambda i: abs(weights[i])
    )[:n_prune]

    # Make a copy so that the original list remains unchanged.
    pruned_weights = list(weights)

    for index in prune_indices:
        pruned_weights[index] = 0.0

    return pruned_weights


# ---------------------------------------------------------------------------
# Part 2b — Sparse COO storage size
# ---------------------------------------------------------------------------

def sparse_coo_size_bytes(weights, value_bytes=4, index_bytes=4):
    """
    Calculate storage required by a COO-style sparse representation.

    Each non-zero weight requires:
        value_bytes + index_bytes

    Zero weights are not stored.
    """
    if value_bytes < 0 or index_bytes < 0:
        raise ValueError("Storage byte sizes must be non-negative")

    nonzero_count = sum(1 for weight in weights if weight != 0.0)

    return nonzero_count * (value_bytes + index_bytes)


# ---------------------------------------------------------------------------
# Part 3 — Symmetric INT8 quantization
# ---------------------------------------------------------------------------

def quantize_int8(weights):
    """
    Quantize floating-point weights to signed 8-bit integer values.

    Uses symmetric quantization:
        scale = max(abs(weight)) / 127
        quantized_weight = round(weight / scale)

    Quantized values are clamped to [-127, 127].

    Returns:
        (quantized_weights, scale)

    For an all-zero input, returns zero integers and scale = 1.0.
    """
    max_abs = max((abs(weight) for weight in weights), default=0.0)

    # Handle empty or all-zero weights.
    if max_abs == 0.0:
        return [0 for _ in weights], 1.0

    scale = max_abs / 127.0

    quantized_weights = []

    for weight in weights:
        quantized_value = int(round(weight / scale))

        # Protect against floating-point boundary errors.
        quantized_value = max(-127, min(127, quantized_value))

        quantized_weights.append(quantized_value)

    return quantized_weights, scale


# ---------------------------------------------------------------------------
# Part 4 — Benchmark model size, accuracy, and latency
# ---------------------------------------------------------------------------



def benchmark_model(
    label,
    weights,
    eval_examples,
    dtype_bytes,
    n_latency_reps=50
):
    """Measure model size, accuracy, and average inference latency."""

    if n_latency_reps <= 0:
        raise ValueError("n_latency_reps must be positive")

    # Calculate accuracy outside the timed section.
    if eval_examples:
        correct = sum(
            predict(weights, example["features"]) == example["label"]
            for example in eval_examples
        )
        accuracy = correct / len(eval_examples)
    else:
        accuracy = 0.0

    # Improve short sleep/timing resolution on Windows.
    timer_adjusted = False
    if sys.platform == "win32":
        try:
            timer_adjusted = (
                ctypes.WinDLL("winmm").timeBeginPeriod(1) == 0
            )
        except (AttributeError, OSError):
            timer_adjusted = False

    try:
        total_elapsed_seconds = 0.0

        for _ in range(n_latency_reps):
            start_time = time.perf_counter()

            for example in eval_examples:
                predict(weights, example["features"])

            total_elapsed_seconds += time.perf_counter() - start_time

    finally:
        if timer_adjusted:
            ctypes.WinDLL("winmm").timeEndPeriod(1)

    latency_ms_per_pass = (
        total_elapsed_seconds / n_latency_reps
    ) * 1000.0

    return {
        "label": label,
        "size_bytes": model_size_bytes(weights, dtype_bytes),
        "accuracy": round(accuracy, 4),
        "latency_ms_per_pass": round(latency_ms_per_pass, 4),
    }
