**Student ID used with `generate_for_student.py`:**
student_id: 142602024  
seed: 2929705198

## pruned_dense_fp32 vs. pruned_sparse_coo

Both variants use the same weights after 70% pruning and achieve the same accuracy of **99.67%**. However, `pruned_dense_fp32` occupies **1024 bytes**, while `pruned_sparse_coo` occupies only **616 bytes**.

The dense model stores all 256 weights, including the zeroed weights, so pruning does not reduce its storage size. The sparse COO representation stores only the 77 non-zero weights, with 4 bytes for each value and 4 bytes for its index. Therefore, it requires only 616 bytes.

This demonstrates the pruning pitfall discussed in the lecture: **pruning alone does not reduce model storage unless a sparse-aware representation is used.**

## The 0.95-sparsity experiment

At 95% sparsity, 243 of the 256 weights are set to zero, leaving only 13 non-zero weights. Since only 40 weights are informative, this aggressive pruning removes many informative weights along with the unimportant noise weights.

As a result, the model's accuracy is expected to decrease significantly compared with the 70%-sparsity experiment. This illustrates the trade-off between model compression and predictive performance.

**Note:** The exact accuracy at 95% sparsity must be obtained by setting `PRUNE_SPARSITY = 0.95` in `src/run_pipeline.py` and rerunning the pipeline.