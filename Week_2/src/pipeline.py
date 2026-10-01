"""
The "after" version — YOUR file to complete.

Fill in the three functions marked with # TODO. Everything else (CLI wiring,
imports) is already done for you. Do not hardcode any path, format string, or
threshold value anywhere in this file — if you find yourself typing a literal
number or file path outside of a default/example, it belongs in the config
file instead.

Run with:
    python src/pipeline.py --config config/pipeline.yaml
"""
import argparse
import csv
import json

import yaml

REQUIRED_KEYS = ["input_path", "input_format", "high_value_threshold", "output_path"]


def load_config(path):
    """Load a YAML config file and validate required keys are present.

    Must raise ValueError naming the specific missing key if REQUIRED_KEYS
    are not all present. Do not let this fail with a bare KeyError later.
    """
    # TODO: implement
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    if config["input_format"] not in ("csv", "json"):
        raise ValueError("input_format must be 'csv' or'json' ")
    return config
    raise NotImplementedError("load_config is not implemented yet")


def load_transactions(path, fmt):
    """Load transactions from `path`, using `fmt` ("csv" or "json") to decide
    how to parse it — not by sniffing the file extension.

    Must return a list of dicts. Every dict must have at least "amount"
    (str or float) and "is_fraud" (str "True"/"False" or bool).
    Raise ValueError for any fmt other than "csv" or "json".
    """
    # TODO: implement
    if fmt == "csv":
        with open(path, "r", newline="") as f:
            reader=csv.DictReader(f)
            transactions = list(reader)
    elif fmt == "json":
        with open(path,"r") as f:
            transactions = json.load(f)
    else: raise ValueError("fmt must be 'csv' or 'json' ")

    if not isinstance(transactions, list):
        raise ValueError("Transaction data must be a list")
    for transaction in transactions:
        if "amount" not in transaction:
            raise ValueError("Transaction is missing required key: amount")
        if "is_fraud" not in transaction:
            raise ValueError("Transaction is missing required key: is_fraud")
    
    return transactions
    raise NotImplementedError("load_transactions is not implemented yet")


def run_pipeline(config):
    """Load data per `config`, compute the same summary fields as
    pipeline_hardcoded.py (n_transactions, total_amount, fraud_rate,
    n_high_value, high_value_threshold), and write them as JSON to
    config["output_path"]. Return the report dict as well.
    """
    # TODO: implement
    transactions = load_transactions(config["input_path"], config["input_format"])
    n_transactions = len(transactions)

    total_amount = sum(float(transaction["amount"]) for transaction in transactions)
    total_amount = round(total_amount,2)
    fraud_count = 0

    for transaction in transactions:
        is_fraud = transaction["is_fraud"]
        if is_fraud == "True":
            fraud_count += 1
        elif str(is_fraud).lower() == "true":
            fraud_count += 1
    fraud_rate = (fraud_count / n_transactions if n_transactions > 0 else 0)

    high_value_threshold = config["high_value_threshold"]

    n_high_value = sum(1 for transaction in transactions if float(transaction["amount"]) >= high_value_threshold)

    report = {
        "n_transactions": n_transactions,
        "total_amount": total_amount,
        "fraud_rate": fraud_rate,
        "n_high_value": n_high_value,
        "high_value_threshold": high_value_threshold
    }

    with open(config["output_path"], "w") as f:
        json.dump(report, f, indent=2)
    
    return report
    
    raise NotImplementedError("run_pipeline is not implemented yet")


def main():
    parser = argparse.ArgumentParser(description="Config-driven fraud transaction summary pipeline")
    parser.add_argument("--config", required=True, help="Path to a YAML config file")
    args = parser.parse_args()

    config = load_config(args.config)
    report = run_pipeline(config)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
