# NOTES.md — Week 9: Orchestrated Batch Scoring

**Student ID used with `generate_for_student.py`:**  
student_id: 142602024  
seed: 1366403000  
Wrote 40 images across 2 camera profiles.  
Wrote 174 annotations.

## notify retry count

The `notify` task took **3 attempts** in total.

It failed on the first two attempts because it is intentionally designed to simulate transient failures. The third attempt succeeded because `max_retries=3` allows additional attempts after the initial failure.

Execution result:

- extract: success, 1 attempt
- score: success, 1 attempt
- load: success, 1 attempt
- notify: success, 3 attempts

## Branch independence

`load` and `notify` are sibling tasks because both depend directly on `score`, but neither depends on the other.

Therefore, when `notify` failed on its first two attempts, `load` was still able to execute successfully because `score` had already completed successfully and `load` had no dependency on `notify`.

This shows that a failure in one branch of a DAG should not automatically affect an unrelated sibling branch. Tasks should be blocked only when one of their own required upstream dependencies fails. This allows independent branches to continue executing and prevents an unnecessary failure in one part of the DAG from stopping unrelated work.

## Retry cost under FinOps

If `notify` were a metered API call and we were charged for every attempt, I would avoid blindly retrying every failure with the same retry policy.

I would first distinguish between **transient errors** and **permanent errors**. Transient errors such as temporary network failures or rate limits can be retried, preferably with exponential backoff. Permanent errors such as invalid credentials or malformed requests should fail immediately instead of repeatedly making paid API calls.

I would also set a reasonable maximum retry limit and use backoff to reduce unnecessary calls. For expensive or high-volume APIs, retries should be based on the expected benefit of recovery versus the additional cost.

Therefore, "retry every failed task the same way" is risky because different tasks have different failure characteristics and costs. A uniform retry policy can waste money by repeatedly calling expensive APIs even when another attempt is unlikely to succeed.