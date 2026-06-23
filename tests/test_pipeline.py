#src/tests/test_pipeline.py
import pytest
from unittest.mock import AsyncMock, patch
from src.services.lead_service import analyse_lead, draft_email, generate_followup
from src.models import LeadProfile, EmailDraft


# ── Reusable fixtures ─────────────────────────────────────────────────────────

VALID_LEAD_JSON = """{
    "intent_score": 8,
    "situation_summary": "Young couple seeking first home loan.",
    "urgency": "high",
    "is_first_buyer": true,
    "recommended_approach": "Schedule consultation immediately.",
    "confidence": 0.92
}"""

VALID_EMAIL_JSON = """{
    "subject": "Your First Home Loan — Let's Talk",
    "body": "Hi there, I noticed you are looking for your first home loan...",
    "tone_score": 8,
    "word_count": 95,
    "key_personalisation": "References urgency and first-home situation."
}"""

VALID_EMAIL_JSON_2 = """{
    "subject": "Still Here to Help With Your Home Loan",
    "body": "Just a quick note — we have not spoken in a while and rates are moving...",
    "tone_score": 7,
    "word_count": 80,
    "key_personalisation": "References time passed and market urgency."
}"""

@pytest.fixture
def lead_profile():
    return LeadProfile(
        intent_score=8,
        situation_summary="Young couple seeking first home loan.",
        urgency="high",
        is_first_buyer=True,
        recommended_approach="Schedule consultation immediately.",
        confidence=0.92
    )


# ── Test 1: analyse_lead() happy path ─────────────────────────────────────────

async def test_analyse_lead_valid_text_returns_lead_profile():
    with patch(
        "src.services.lead_service.generate_response",
        new_callable=AsyncMock
    ) as mock_gen:

        mock_gen.return_value = VALID_LEAD_JSON

        result = await analyse_lead("Young couple needs first home loan urgently.")

        assert result is not None
        assert isinstance(result, LeadProfile)
        assert 1 <= result.intent_score <= 10
        assert result.urgency in ("low", "medium", "high")
        assert isinstance(result.is_first_buyer, bool)
        assert 0 <= result.confidence <= 1


# ── Test 2: analyse_lead() empty string returns None ─────────────────────────

async def test_analyse_lead_empty_string_returns_none():
    with patch(
        "src.services.lead_service.generate_response",
        new_callable=AsyncMock
    ) as mock_gen:

        # model returns broken JSON when given empty input
        mock_gen.return_value = "{}"

        result = await analyse_lead("")

        # must return None, never raise
        assert result is None


# ── Test 3: draft_email() returns valid EmailDraft ───────────────────────────

async def test_draft_email_returns_email_draft(lead_profile):
    with patch(
        "src.services.lead_service.generate_response",
        new_callable=AsyncMock
    ) as mock_gen:

        mock_gen.return_value = VALID_EMAIL_JSON

        result = await draft_email(lead_profile)

        assert result is not None
        assert isinstance(result, EmailDraft)
        assert len(result.subject) > 0
        assert len(result.body) > 0
        assert 1 <= result.tone_score <= 10
        assert result.word_count > 0


# ── Test 4: generate_followup() #1 and #3 return different body text ─────────

async def test_followup_1_and_3_have_different_bodies(lead_profile):
    with patch(
        "src.services.lead_service.generate_response",
        new_callable=AsyncMock
    ) as mock_gen:

        # first call returns email 1, second call returns email 2
        mock_gen.side_effect = [VALID_EMAIL_JSON, VALID_EMAIL_JSON_2]

        followup_1 = await generate_followup(
            lead_profile=lead_profile,
            follow_up_number=1,
            days_since_last_contact=3,
            previous_emails=[]
        )

        followup_3 = await generate_followup(
            lead_profile=lead_profile,
            follow_up_number=3,
            days_since_last_contact=9,
            previous_emails=[followup_1.body]
        )

        assert followup_1 is not None
        assert followup_3 is not None
        assert followup_1.body != followup_3.body


# ── Test 5: analyse_lead() returns None on bad JSON, never raises ─────────────

async def test_analyse_lead_bad_json_returns_none():
    with patch(
        "src.services.lead_service.generate_response",
        new_callable=AsyncMock
    ) as mock_gen:

        mock_gen.return_value = "Sorry, I cannot process that."

        result = await analyse_lead("some lead text")

        assert result is None


# ── Test 6: draft_email() returns None on provider error, never raises ────────

async def test_draft_email_provider_error_returns_none(lead_profile):
    from src.exceptions import ProviderError

    with patch(
        "src.services.lead_service.generate_response",
        new_callable=AsyncMock
    ) as mock_gen:

        mock_gen.side_effect = ProviderError(
            provider="groq",
            error_type="AuthenticationError",
            detail="Invalid API key",
            retryable=False
        )

        result = await draft_email(lead_profile)

        assert result is None