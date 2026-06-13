# src/api/routers/health.py
import logging
from fastapi import APIRouter
from src.api.schemas import HealthResponse
from src.utils.cost_tracker import get_today_total  

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="API health check with today's spend",
)
async def health_check() -> HealthResponse:
    
    today_cost = get_today_total()  # reads costs.csv, filters by today's date
    logger.info(f"Health check | today_cost_usd={today_cost}")
    return HealthResponse(status="ok", today_cost_usd=today_cost)