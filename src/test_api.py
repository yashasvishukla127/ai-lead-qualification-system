# test_api.py
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from main import app
from src.models import LeadProfile, EmailDraft  # adjust to your actual imports


MOCK_LEAD_PROFILE = LeadProfile(
    intent_score=8,
    urgency="high",
    is_first_buyer=True,
    confidence=0.9,
    recommended_approach="value-led",
)

MOCK_EMAIL_DRAFT = EmailDraft(
    subject="Quick question about your reporting workflow",
    body="Hi Sarah, I noticed...",
    tone_score=8,
)

MOCK_PROCESS_RESULT = {
    "lead_profile": MOCK_LEAD_PROFILE,
    "email_draft": MOCK_EMAIL_DRAFT,
    "follow_up_angles": {
        "value_add": "Show ROI dashboard",
        "urgency": "Q2 deadline approaching",
        "final": "Offer a free audit",
    },
}


@pytest.mark.asyncio
async def test_health_check():     # without this asgi it would send request to real server now for testing on local server
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "today_cost_usd" in data

    #assert here verified that test running is fine if not rasies an assertion error

@pytest.mark.asyncio  #to manage pauses and resumptoin of test this @pytest marking is required
async def test_analyse_lead_success(): 
    #patch here tells there is in this path src -> api -> routers -> leads some function instead calling it directly mock it assume it is coming from there 
    with patch("src.api.routers.leads.process_lead", new_callable=AsyncMock) as mock:
        mock.return_value = MOCK_PROCESS_RESULT
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/analyse-lead",
                json={"lead_text": "Sarah runs a 15-person startup and needs automation tools."},
                headers={"x-request-id": "test-correlation-123"},
            )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "test-correlation-123"  # echoed back
    data = response.json()
    assert data["correlation_id"] == "test-correlation-123"
    assert data["lead_profile"]["intent_score"] == 8


@pytest.mark.asyncio
async def test_analyse_lead_short_text_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyse-lead",
            json={"lead_text": "Hi"},
        )
    assert response.status_code == 422  # Pydantic min_length triggers this


@pytest.mark.asyncio
async def test_correlation_id_generated_if_missing():
    with patch("src.api.routers.leads.process_lead", new_callable=AsyncMock) as mock:
        mock.return_value = MOCK_PROCESS_RESULT
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/analyse-lead",
                json={"lead_text": "Sarah runs a 15-person startup and needs automation tools."},
                # No x-request-id header — server should generate one
            )
    assert "x-request-id" in response.headers
    assert len(response.headers["x-request-id"]) == 36  # UUID format