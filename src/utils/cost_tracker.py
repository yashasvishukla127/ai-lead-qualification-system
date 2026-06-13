# D:\ai engineering\Agentic Ai\src\utils\cost_tracker.py
import csv
import os
from datetime import datetime
from pathlib import Path

# COSTS_FILE = str(Path(__file__).resolve().parent.parent.parent / "costs.csv")
COSTS_FILE = str(Path("/tmp/costs.csv"))


def log_cost(function_name: str, input_tokens: int, output_tokens: int) -> None:
    cost_usd = (input_tokens * 0.000003) + (output_tokens * 0.000015)
    timestamp = datetime.now().isoformat()
    file_exists = os.path.isfile(COSTS_FILE)

    with open(COSTS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                ["timestamp", "function_name", "input_tokens", "output_tokens", "cost_usd"]
            )
        writer.writerow([timestamp, function_name, input_tokens, output_tokens, cost_usd])


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

    return total
