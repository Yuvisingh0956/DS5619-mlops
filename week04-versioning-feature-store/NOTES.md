# NOTES.md — Week 4: Versioning, Feature Store & Lineage

**Student ID used with `generate_for_student.py`: 142602024**

## v1 vs. v2 manifest comparison

The v1 and v2 feature groups are both named `card_activity`, but they are stored as separate feature-group versions.

The v1 feature group has:

* `feature_group_version_id`: `v1`
* `source_raw_version_id`: `v1`
* `transform_version`: `v1`
* `row_count`: `380`

The v2 feature group has:

* `feature_group_version_id`: `v2`
* `source_raw_version_id`: `v2`
* `transform_version`: `v1`
* `row_count`: `123`

The feature schema is the same for both versions:

`avg_amount`, `card_id`, `event_time`, `max_amount`, `pct_card_present`, and `txn_count`.

However, the raw source schemas are different. In v1, the transaction data contains `amount` and `country`. In v2, the upstream schema changed these to `amount_minor_units` and `country_code`, and a new `device_fingerprint` field was added.

Therefore, the breaking upstream schema change is represented by creating a new raw data version and a new feature-group version instead of overwriting the existing v1 history. The lineage also clearly connects feature-group v1 to raw v1 and feature-group v2 to raw v2.

## Why treat amount_minor_units differently from amount?

In v1, the `amount` field already contains the transaction amount in the normal unit, while v2 stores the amount in minor units such as cents using the `amount_minor_units` field.

Therefore, `build_features` divides `amount_minor_units` by 100 before calculating the aggregate features. This converts the v2 values back to the same unit used by v1.

Without this conversion, the v2 `avg_amount` and `max_amount` values would be approximately 100 times larger than the corresponding v1 values, making the features inconsistent and not directly comparable across versions.
