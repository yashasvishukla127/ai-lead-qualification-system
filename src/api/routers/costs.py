# src/api/routers/costs.py
import csv
import logging

from fastapi import APIRouter, HTTPException
from src.api.schemas import CostsResponse, CostEntry
from src.utils.cost_tracker import get_today_total ,COSTS_FILE


from pathlib import Path
# # COSTS_FILE = Path(COSTS_FILE)
# # COSTS_FILE = Path("costs.csv")
# COSTS_FILE = Path(__file__).resolve().parent.parent.parent / "costs.csv"
# file_exists = Path(COSTS_FILE).exists() and Path(COSTS_FILE).stat().st_size > 0

# if not file_exists:
#     writer.writerow(
#         ["timestamp", "function_name", "input_tokens", "output_tokens", "cost_usd"]
#     )

router = APIRouter(prefix="/api/v1", tags=["Costs"])
logger = logging.getLogger(__name__)




@router.get(
    "/costs",
    response_model=CostsResponse,
    summary="Return all logged costs from costs.csv",
)

async def get_costs() -> CostsResponse:
    costs_path = Path(COSTS_FILE)
    print("✅READING:", COSTS_FILE)
    if not COSTS_FILE.exists():
        raise HTTPException(status_code=404, detail="costs.csv not found")

    entries: list[CostEntry] = []
    total = 0.0

    try:
        with open(COSTS_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry = CostEntry(
                    timestamp=row.get("timestamp", ""),
                    function_name=row.get("function_name", ""),
                    input_tokens=int(row.get("input_tokens", 0)),
                    output_tokens=int(row.get("output_tokens", 0)),
                    cost_usd=float(row.get("cost_usd", 0)),
)
                entries.append(entry)
                total += entry.cost_usd

    except Exception as e:
        logger.error(f"Failed to read costs.csv | error={e}")
        raise HTTPException(status_code=500, detail="Could not read cost data")

    return CostsResponse(
        total_cost_usd=round(total, 6), # ( round upto 6 digits  -> 9.023455)
        today_cost_usd=get_today_total(),
        entries=entries,
    )