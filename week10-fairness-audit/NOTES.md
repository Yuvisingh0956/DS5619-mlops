# NOTES.md — Week 10: Fairness and Robustness Audit

**Student ID used with `generate_for_student.py`:** `142602024`  
**Generated seed:** `950835326`

## Which classes got flagged?

With a recall threshold of 90%, the audit flagged **Bicycle (24/30 = 80.0%)**, **Two-wheeler (8/10 = 80.0%)**, and **Three-wheeler (12/14 = 85.7%)**. This is consistent with the fixture design: smaller vehicle classes receive smaller boxes, which are harder for the mock detector to find. The generator guarantees Bicycle and Two-wheeler fall below the threshold; Three-wheeler also falls below it for this seed. Because the class counts are small, especially Two-wheeler's 10 boxes, the measured gaps may partly reflect sampling variation and should be checked on more data.

## If the grouping variable were a protected attribute

If groups represented protected demographic attributes, recall gaps could mean that a system fails more often for some people, creating unequal safety or service outcomes. The stakes would therefore be higher than this vehicle-class exercise. I would validate the disparity on a larger, representative dataset; examine data quality and likely causes; document uncertainty and limitations; consult affected stakeholders; and monitor performance after deployment. Where the impact is consequential, mitigation and a documented risk assessment would be needed. Vehicle classes are useful for practising group-wise auditing, but they are not equivalent to protected demographic groups.

## Which attack could corrupt this audit?

A **data-poisoning attack** could alter or selectively remove ground-truth annotations for a class, making its measured recall appear artificially high or low without changing the detector. Controls include dataset provenance and integrity checks, restricted access, annotation review, and evaluation against a trusted holdout set. The pipeline should also log dataset versions so unexpected changes can be traced.

## Would SHAP or LIME explain a missed detection?

Not reliably by themselves. For example, Bicycle has **6 missed ground-truth boxes out of 30**. The report gives aggregate counts rather than the image and coordinates of a particular missed box, so that specific case would need to be selected from the annotations and inspected. In this mock detector, a miss can occur because the reddish pixels fail the rule (`r > 120`, `r - g > 40`, and `r - b > 40`) or because the connected blob contains fewer than 20 pixels. SHAP and LIME generally explain a defined model output by attributing it to input features; this detector instead returns a variable-length list of bounding boxes, category IDs, and scores, and a missed box has no corresponding detection score to explain. One could define a fixed target, such as whether a particular region produces a detection, and test pixel or region perturbations, but directly inspecting the detector's simple rule is the clearest explanation here. For a trained detector, a suitable target and careful handling of its multiple box outputs would be needed.

## What did your attack show?

The attack lowers red and raises green and blue, moving pixels away from the mock detector's reddish-colour thresholds. Recall falls as the perturbation budget increases, though individual classes can plateau between budgets.

- **Clean-audit flagged classes:** Bicycle, Two-wheeler, Three-wheeler.
- **When their recall first falls further:** Bicycle drops from 80.0% to 66.7% at `eps=10` and continues falling at 20, 30, and 40. Two-wheeler drops from 80.0% to 70.0% at `eps=10`, to 60.0% at `eps=20`, stays at 60.0% at `eps=30`, and falls to 30.0% at `eps=40`. Three-wheeler stays at 85.7% at `eps=10`, drops to 71.4% at `eps=20` and 50.0% at `eps=30`, then stays at 50.0% at `eps=40`.
- **Most fragile at `eps=20` (largest recall drop):** SUV (drop of 0.3571, or 35.71%), followed by Bicycle (0.3333, or 33.33%) and Hatchback (0.3333, or 33.33%).
- **Lowest absolute recall at `eps=20`:** Bicycle (46.7%), Two-wheeler (60.0%), and Hatchback (62.5%).

The rankings do **not** fully agree. SUV has the largest drop because its clean recall was 100%, but it is not among the three lowest-recall classes after the attack. Bicycle has both a large drop and the lowest attacked recall. The drop ranking is more useful for measuring how much the attack harmed each class relative to its baseline; absolute attacked recall is more useful for identifying which classes perform worst after the attack. Both views matter when deciding who bears the cost of a failure.

For this rule-based detector, conventional gradient-based adversarial training is not directly applicable. A practical analogue is to test with perturbed colours and threshold-boundary cases, revise the rule or replace it with a better detector, and add regression tests across multiple perturbation budgets. Input validation can check image decoding, dimensions, RGB mode, and valid pixel ranges, but it cannot stop an adversarial colour change in an otherwise valid image. This mock detector is especially brittle because it relies on fixed colour thresholds and a minimum blob size rather than richer learned features. A CNN is not automatically robust either; it can also be attacked and must be tested and monitored.
