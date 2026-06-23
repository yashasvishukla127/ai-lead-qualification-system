# src/api/routers/costs.py  — replace the whole file
import csv
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from src.api.schemas import CostsResponse, CostEntry
from src.utils.cost_tracker import get_today_total, get_daily_summary

router = APIRouter(prefix="/api/v1", tags=["Costs"])
logger = logging.getLogger(__name__)
COSTS_FILE = Path(__file__).resolve().parent.parent.parent.parent / "costs.csv"


@router.get("/costs", response_model=CostsResponse, summary="All raw cost entries")
async def get_costs() -> CostsResponse:
    if not COSTS_FILE.exists():
        raise HTTPException(status_code=404, detail="costs.csv not found")
    entries: list[CostEntry] = []
    total = 0.0
    try:
        with open(COSTS_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry = CostEntry(
                    timestamp=row["timestamp"],
                    function_name=row["function_name"],
                    model=row.get("model", "unknown"),
                    input_tokens=int(row["input_tokens"]),
                    output_tokens=int(row["output_tokens"]),
                    cost_usd=float(row["cost_usd"]),
                )
                entries.append(entry)
                total += entry.cost_usd
    except Exception as e:
        logger.error(f"Failed to read costs.csv | error={e}")
        raise HTTPException(status_code=500, detail="Could not read cost data")
    return CostsResponse(total_cost_usd=round(total, 6), today_cost_usd=get_today_total(), entries=entries)


@router.get("/costs/summary", summary="Daily aggregated cost breakdown")
async def get_cost_summary():
    return {"summary": get_daily_summary(), "today_cost_usd": get_today_total()}


@router.get("/dashboard", response_class=HTMLResponse, summary="Visual cost dashboard", tags=["Dashboard"])
async def cost_dashboard():
    summary = get_daily_summary()
    # Build JS arrays for Chart.js
    dates  = sorted(set(r["date"]  for r in summary))
    models = sorted(set(r["model"] for r in summary))
    colors = ["#4e79a7", "#f28e2b", "#59a14f", "#e15759"]

    # cost per day per model
    datasets = []
    for i, model in enumerate(models):
        data = []
        for date in dates:
            row = next((r for r in summary if r["date"] == date and r["model"] == model), None)
            data.append(round(row["cost_usd"], 6) if row else 0)
        datasets.append({"label": model, "data": data, "backgroundColor": colors[i % len(colors)]})

    # table rows
    table_rows = "".join(
        f"<tr><td>{r['date']}</td><td>{r['model']}</td><td>{r['calls']}</td>"
        f"<td>{r['input_tokens']:,}</td><td>{r['output_tokens']:,}</td>"
        f"<td>${r['cost_usd']:.6f}</td></tr>"
        for r in summary
    )

    today = get_today_total()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Cost Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 40px auto; padding: 0 20px; background: #f9f9f9; }}
    h1 {{ color: #333; }} .card {{ background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 1px 4px rgba(0,0,0,.1); }}
    .stat {{ font-size: 2rem; font-weight: 700; color: #4e79a7; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
    th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; }}
    th {{ background: #f0f0f0; font-weight: 600; }}
    tr:hover {{ background: #fafafa; }}
  </style>
</head>
<body>
  <h1>🧠 Lead Analyser — Cost Dashboard</h1>
  <div class="card">
    <p>Today's spend</p>
    <div class="stat">${today:.6f}</div>
  </div>
  <div class="card">
    <canvas id="costChart" height="80"></canvas>
  </div>
  <div class="card">
    <h2>Daily Breakdown</h2>
    <table>
      <thead><tr><th>Date</th><th>Model</th><th>Calls</th><th>Input Tokens</th><th>Output Tokens</th><th>Cost (USD)</th></tr></thead>
      <tbody>{table_rows}</tbody>
    </table>
  </div>
  <script>
    const ctx = document.getElementById('costChart').getContext('2d');
    new Chart(ctx, {{
      type: 'bar',
      data: {{
        labels: {dates},
        datasets: {datasets}
      }},
      options: {{
        responsive: true,
        plugins: {{ title: {{ display: true, text: 'Daily Cost by Model (USD)' }} }},
        scales: {{ x: {{ stacked: true }}, y: {{ stacked: true }} }}
      }}
    }});
  </script>
</body>
</html>"""