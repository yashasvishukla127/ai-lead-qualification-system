# D:\ai engineering\Agentic Ai\src\utils\cost_tracker.py
import csv
import os
from datetime import datetime
from pathlib import Path
import logging
from collections import defaultdict 


logger = logging.getLogger(__name__)

COSTS_FILE = Path(__file__).resolve().parent.parent.parent / "costs.csv"
COSTS_FILE.parent.mkdir(parents=True, exist_ok=True)
COSTS_FILE.touch(exist_ok=True)
 

# COSTS_FILE = Path(__file__).resolve().parent.parent.parent / "costs.csv"
# print(" 🚩WRITING:", COSTS_FILE)

# Path(COSTS_FILE).parent.mkdir(parents=True, exist_ok=True)

# if not Path(COSTS_FILE).exists():
#     Path(COSTS_FILE).touch()



MODEL_PRICING = {
    "claude-sonnet-4-6":   {"input": 3.00,  "output": 15.00},
    "claude-haiku-4-5":    {"input": 0.80,  "output": 4.00},
    "claude-opus-4-6":     {"input": 15.00, "output": 75.00},
    "default":             {"input": 3.00,  "output": 15.00},
}

def _calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000



def log_cost(function_name: str, input_tokens: int, output_tokens: int) -> None:
    cost_usd = (input_tokens * 0.000003) + (output_tokens * 0.000015)
    timestamp = datetime.now().isoformat()
    file_exists = os.path.isfile(COSTS_FILE)


    logger.info(f"Reading costs from: {COSTS_FILE}")
                      # a means add new line and append
    with open(COSTS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                ["timestamp", "function_name", "input_tokens", "output_tokens", "cost_usd"]
            )
        writer.writerow([timestamp, function_name, input_tokens, output_tokens, cost_usd])


def log_cost(function_name: str, input_tokens: int, output_tokens: int, model: str = "claude-sonnet-4-6") -> None:
    cost_usd = _calculate_cost(model, input_tokens, output_tokens)
    timestamp = datetime.now().isoformat()
    file_exists = os.path.isfile(COSTS_FILE)

    with open(COSTS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "function_name", "model", "input_tokens", "output_tokens", "cost_usd"])
        writer.writerow([timestamp, function_name, model, input_tokens, output_tokens, cost_usd])


def get_today_total() -> float:
    if not os.path.isfile(COSTS_FILE):
        return 0.0
    today = datetime.now().strftime("%Y-%m-%d")
    total = 0.0
    with open(COSTS_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["timestamp"].startswith(today):
                total += float(row["cost_usd"])
    return round(total, 6)


def get_daily_summary() -> list[dict]:
    """
    Returns per-day, per-model aggregated stats.
    [
      {
        "date": "2025-06-18",
        "model": "claude-sonnet-4-6",
        "calls": 12,
        "input_tokens": 4500,
        "output_tokens": 1200,
        "cost_usd": 0.0315
      },
      ...
    ]
    """
    if not os.path.isfile(COSTS_FILE):
        return []

    # key: (date, model)
    buckets: dict[tuple, dict] = defaultdict(lambda: {
        "calls": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0
    })

    with open(COSTS_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["timestamp"][:10]
            model = row.get("model", "unknown")
            key = (date, model)
            buckets[key]["calls"] += 1
            buckets[key]["input_tokens"] += int(row["input_tokens"])
            buckets[key]["output_tokens"] += int(row["output_tokens"])
            buckets[key]["cost_usd"] += float(row["cost_usd"])

    result = []
    for (date, model), stats in sorted(buckets.items()):
        result.append({
            "date": date,
            "model": model,
            **stats,
            "cost_usd": round(stats["cost_usd"], 6),
        })
    return result