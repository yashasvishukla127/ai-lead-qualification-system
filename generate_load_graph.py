# generate_load_graph.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

RUNS = {
    "1 user":   "results/load_u1_stats.csv",
    "10 users":  "results/load_u10_stats.csv",
    "50 users":  "results/load_u50_stats.csv",
    "200 users": "results/load_u200_stats.csv",
}

TARGET_NAME = "/api/v1/analyse-lead"   # must match `name=` in locustfile.py

records = []
for label, path in RUNS.items():
    if not Path(path).exists():
        print(f"Skipping {path} — not found")
        continue
    df = pd.read_csv(path)
    row = df[df["Name"] == TARGET_NAME]
    if row.empty:
        print(f"No row for {TARGET_NAME} in {path}")
        continue
    records.append({
        "label":  label,
        "p50":    float(row["50%"].values[0]),
        "p95":    float(row["95%"].values[0]),
        "p99":    float(row["99%"].values[0]),
    })

if not records:
    print("No data found. Run run_load_tests.bat first.")
    exit(1)

labels = [r["label"] for r in records]
p50 = [r["p50"] for r in records]
p95 = [r["p95"] for r in records]
p99 = [r["p99"] for r in records]

x = range(len(labels))
width = 0.25

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar([i - width for i in x], p50, width, label="p50 (median)", color="#4CAF50")
ax.bar([i          for i in x], p95, width, label="p95",          color="#FF9800")
ax.bar([i + width  for i in x], p99, width, label="p99 (tail)",   color="#F44336")

ax.set_xlabel("Concurrent Users")
ax.set_ylabel("Latency (ms)")
ax.set_title("POST /api/v1/analyse-lead — Latency at Scale")
ax.set_xticks(list(x))
ax.set_xticklabels(labels)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}ms"))
ax.legend()
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
output = "results/latency_graph.png"
plt.savefig(output, dpi=500)  #150 -> 200 -> 300 -> 500 -> 1000 for best professional
print(f"Graph saved to {output}")