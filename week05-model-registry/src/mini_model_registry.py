"""
A tiny local model registry — enough to demonstrate the governance ideas from
this week's lecture without needing an MLflow/W&B server:

  1. The registry as an artifact store (register_model) — one immutable,
     named version per trained model, not forty nearly-identical runs.
  2. The model card as the governance control (generate_model_card) — must
     actually be filled in, not just present.
  3. Promotion between stages (promote_model) as a GATE, not a rename — you
     cannot reach Production without a complete card and metrics that clear
     the bar. Promoting a new model to Production auto-archives whichever
     version was there before, so "what's in production" always has exactly
     one answer.

Fill in the four functions marked # TODO. Helpers/constants above them are
done.
"""
import json
import os
import shutil
from datetime import datetime, timezone

PRODUCTION_F1_THRESHOLD = 0.70
REQUIRED_CARD_FIELDS = ["intended_use", "training_data", "limitations", "ethical_considerations"]


class GovernanceError(Exception):
    """Raised when a promotion is attempted that violates a governance rule."""


def _now():
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _next_version_id(existing_dir):
    """Return the next version ID: v1, v2, v3, ..."""
    if not os.path.isdir(existing_dir):
        return "v1"

    nums = []
    for name in os.listdir(existing_dir):
        if name.startswith("v") and name[1:].isdigit():
            nums.append(int(name[1:]))

    return f"v{max(nums, default=0) + 1}"


def _model_dir(registry_dir, name, version_id=None):
    """Return the model directory, optionally for one specific version."""
    path = os.path.join(registry_dir, "models", name)

    if version_id is not None:
        path = os.path.join(path, version_id)

    return path


def _version_dir(name, version_id, registry_dir):
    """Return the directory for one particular model version."""
    return _model_dir(registry_dir, name, version_id)


def _manifest_path(name, version_id, registry_dir):
    """Return the path to a version's manifest.json file."""
    return os.path.join(
        _version_dir(name, version_id, registry_dir),
        "manifest.json",
    )


def _load_json(path):
    """Load and return JSON data from a file."""
    with open(path, "r") as f:
        return json.load(f)


def _save_json(path, data):
    """Save JSON data to a file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Part 1 — Register a model version (the artifact store)
# ---------------------------------------------------------------------------

def register_model(name, model_path, metrics, registry_dir):
    """Register a new version of model `name` in the registry.

    A model is stored as an immutable version containing:
      - model.json
      - metrics.json
      - manifest.json

    The first registration is v1, the next is v2, etc.
    """
    if not name:
        raise ValueError("Model name cannot be empty.")

    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Model file does not exist: {model_path}")

    if not isinstance(metrics, dict):
        raise TypeError("metrics must be a dictionary.")

    model_versions_dir = _model_dir(registry_dir, name)
    version_id = _next_version_id(model_versions_dir)

    version_dir = _version_dir(name, version_id, registry_dir)
    os.makedirs(version_dir, exist_ok=False)

    # Read the model as JSON and write a registry copy as model.json.
    model_data = _load_json(model_path)
    _save_json(
        os.path.join(version_dir, "model.json"),
        model_data,
    )

    # Store the supplied metrics exactly as provided.
    _save_json(
        os.path.join(version_dir, "metrics.json"),
        metrics,
    )

    # The manifest must contain the supplied metrics as-is.
    manifest = {
        "version_id": version_id,
        "name": name,
        "metrics": metrics,
        "stage": "None",
        "created_at": _now(),
    }

    _save_json(
        os.path.join(version_dir, "manifest.json"),
        manifest,
    )

    return version_id


# ---------------------------------------------------------------------------
# Part 2 — Generate a model card
# ---------------------------------------------------------------------------

def generate_model_card(name, version_id, card_fields, registry_dir):
    """Validate and write a model card for a registered model version.

    Every field in REQUIRED_CARD_FIELDS must:
      - exist,
      - be a non-empty string, and
      - not contain the literal substring "TODO".
    """
    version_dir = _version_dir(name, version_id, registry_dir)

    if not os.path.isdir(version_dir):
        raise FileNotFoundError(
            f"Registered model version not found: {name}/{version_id}"
        )

    if not isinstance(card_fields, dict):
        raise TypeError("card_fields must be a dictionary.")

    # Validate every required field, not merely the fields supplied by
    # the caller. This is important for the governance requirement.
    for field_name in REQUIRED_CARD_FIELDS:
        if field_name not in card_fields:
            raise ValueError(
                f"Model card field '{field_name}' is missing."
            )

        value = card_fields[field_name]

        if not isinstance(value, str):
            raise ValueError(
                f"Model card field '{field_name}' must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"Model card field '{field_name}' is empty."
            )

        if "TODO" in value.upper():
            raise ValueError(
                f"Model card field '{field_name}' still contains TODO."
            )

    manifest = _load_manifest(name, version_id, registry_dir)

    card = {
        "name": name,
        "version_id": version_id,
        **card_fields,
        "metrics": manifest["metrics"],
        "created_at": _now(),
    }

    card_path = os.path.join(version_dir, "model_card.json")
    _save_json(card_path, card)

    return card_path


# ---------------------------------------------------------------------------
# Part 3 — Promote a model version (the governance gate)
# ---------------------------------------------------------------------------

def _load_manifest(name, version_id, registry_dir):
    """Load a model version's manifest."""
    path = _manifest_path(name, version_id, registry_dir)

    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Manifest not found for {name}/{version_id}"
        )

    return _load_json(path)


def _save_manifest(name, version_id, manifest, registry_dir):
    """Save a model version's manifest."""
    _save_json(
        _manifest_path(name, version_id, registry_dir),
        manifest,
    )


def _all_versions(name, registry_dir):
    """Return all registered version IDs for a model."""
    model_dir = _model_dir(registry_dir, name)

    if not os.path.isdir(model_dir):
        return []

    versions = []

    for entry in os.listdir(model_dir):
        path = os.path.join(model_dir, entry)

        if (
            os.path.isdir(path)
            and entry.startswith("v")
            and entry[1:].isdigit()
        ):
            versions.append(entry)

    versions.sort(key=lambda x: int(x[1:]))

    return versions


def promote_model(name, version_id, target_stage, registry_dir):
    """Promote a model version to Staging or Production.

    Production requires both:
      1. A complete model_card.json.
      2. metrics["f1"] >= PRODUCTION_F1_THRESHOLD.

    When a new version reaches Production, any existing Production version
    of the same model is moved to Archived.

    Every successful stage change is appended to manifest["history"].
    """
    valid_stages = {
        "None",
        "Staging",
        "Production",
        "Archived",
    }

    if target_stage not in valid_stages:
        raise ValueError(f"Invalid target stage: {target_stage}")

    manifest = _load_manifest(name, version_id, registry_dir)
    version_dir = _version_dir(name, version_id, registry_dir)

    if target_stage == "Production":
        # Governance gate 1: complete model card must exist.
        card_path = os.path.join(version_dir, "model_card.json")

        if not os.path.exists(card_path):
            raise GovernanceError(
                f"Promotion blocked: {name}/{version_id} "
                f"does not have a model card."
            )

        # Governance gate 2: F1 must meet the production threshold.
        metrics = manifest.get("metrics")

        if not isinstance(metrics, dict):
            raise GovernanceError(
                f"Promotion blocked: metrics are missing "
                f"for {name}/{version_id}."
            )

        if "f1" not in metrics:
            raise GovernanceError(
                f"Promotion blocked: f1 metric is missing "
                f"for {name}/{version_id}."
            )

        f1 = metrics["f1"]

        try:
            passes_f1_gate = f1 >= PRODUCTION_F1_THRESHOLD
        except TypeError as exc:
            raise GovernanceError(
                f"Promotion blocked: f1 metric for "
                f"{name}/{version_id} is not numeric."
            ) from exc

        if not passes_f1_gate:
            raise GovernanceError(
                f"Promotion blocked: f1={f1:.3f} is below "
                f"production threshold "
                f"{PRODUCTION_F1_THRESHOLD:.2f}."
            )

        # Archive any other version currently in Production.
        for other_version in _all_versions(name, registry_dir):
            if other_version == version_id:
                continue

            other_manifest = _load_manifest(
                name,
                other_version,
                registry_dir,
            )

            if other_manifest.get("stage") == "Production":
                old_stage = other_manifest["stage"]
                other_manifest["stage"] = "Archived"
                other_manifest.setdefault("history", []).append(
                    {
                        "from_stage": old_stage,
                        "to_stage": "Archived",
                        "at": _now(),
                    }
                )
                other_manifest["archived_at"] = _now()

                _save_manifest(
                    name,
                    other_version,
                    other_manifest,
                    registry_dir,
                )

    # Update the requested version and preserve its audit history.
    old_stage = manifest.get("stage", "None")
    manifest["stage"] = target_stage

    manifest.setdefault("history", []).append(
        {
            "from_stage": old_stage,
            "to_stage": target_stage,
            "at": _now(),
        }
    )

    _save_manifest(
        name,
        version_id,
        manifest,
        registry_dir,
    )

    return manifest


# ---------------------------------------------------------------------------
# Part 4 — Look up what's currently in production
# ---------------------------------------------------------------------------

def get_production_model(name, registry_dir):
    """Return the Production manifest, or None if nothing is in Production."""
    for version_id in _all_versions(name, registry_dir):
        manifest = _load_manifest(
            name,
            version_id,
            registry_dir,
        )

        if manifest.get("stage") == "Production":
            return manifest

    return None
