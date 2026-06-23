# src/api/schemas.py
from pydantic import BaseModel, Field
from src.models import LeadProfile, EmailDraft  # your existing models

class AnalyseLeadRequest(BaseModel):
    lead_text: str = Field(..., min_length=10, description="Raw lead description text")
 #                       means must be min 10 char string , 
    model_config = {
        "json_schema_extra": {
            "example": {
                "lead_text": "Yashasvi a startup owner , related to automation ."
                " wants to buy a duplex ultra luxury villa  "
                "in Greater Noida region "
            }
        }
    }


# class FollowUpAngles(BaseModel):
#     value_add: str
#     urgency: str
#     final: str


class AnalyseLeadResponse(BaseModel):
    correlation_id: str
    lead_profile: LeadProfile
    email_draft: EmailDraft
    # follow_up_angles: FollowUpAngles


class HealthResponse(BaseModel):
    status: str
    today_cost_usd: float
    version: str = "1.0.0"


class CostEntry(BaseModel):
    timestamp: str
    model: str
    function_name: str
    # function_version: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


class CostsResponse(BaseModel):
    total_cost_usd: float
    today_cost_usd: float
    entries: list[CostEntry]