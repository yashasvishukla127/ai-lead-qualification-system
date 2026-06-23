# src/api/routers/leads.py
import logging
from fastapi import APIRouter, HTTPException, status

from src.api.schemas import AnalyseLeadRequest, AnalyseLeadResponse
from src.services.lead_service import process_lead
from src.utils.logger import get_correlation_id

router = APIRouter(prefix="/api/v1", tags=["Leads"])
logger = logging.getLogger(__name__)


@router.post(
    "/analyse-lead",
    response_model=AnalyseLeadResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyse a lead and generate email + follow-up angles",
)
async def analyse_lead(request: AnalyseLeadRequest) -> AnalyseLeadResponse:
    
    cid = get_correlation_id()
    logger.info(f"Received lead analysis request | length={len(request.lead_text)}")

    try:
        result = await process_lead(request.lead_text)
        

        if "error" in result or "lead_profile" not in result:
            logger.error(f"Lead analysis returned error state | result={result}")
            raise HTTPException(status_code=422, detail="Lead analysis failed — could not generate a valid profile")

        return AnalyseLeadResponse(
            correlation_id=cid,
            lead_profile=result["lead_profile"],
            email_draft=result["email_draft"],
            # follow_up_angles=result["follow_up_angles"],
        )

    except ValueError as e:
        logger.warning(f"Validation error during lead analysis | error={e}")
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        logger.error(f"Lead analysis failed | error={e}")
        raise HTTPException(status_code=500, detail="Internal processing error")