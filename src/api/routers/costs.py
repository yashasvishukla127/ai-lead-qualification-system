# src/api/routers/costs.py
import csv
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from src.api.schemas import CostsResponse, CostEntry
from src.utils.cost_tracker import get_today_total

router = APIRouter(prefix="/api/v1", tags=["Costs"])
logger = logging.getLogger(__name__)

COSTS_FILE = Path("costs.csv")


@router.get(
    "/costs",
    response_model=CostsResponse,
    summary="Return all logged costs from costs.csv",
)
async def get_costs() -> CostsResponse:
    if not COSTS_FILE.exists():
        raise HTTPException(status_code=404, detail="costs.csv not found")

    entries: list[CostEntry] = []
    total = 0.0

    try:
        with open(COSTS_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry = CostEntry(
                    timestamp=row["timestamp"],
                    provider=row["provider"],
                    input_tokens=int(row["input_tokens"]),
                    output_tokens=int(row["output_tokens"]),
                    cost_usd=float(row["cost_usd"]),
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