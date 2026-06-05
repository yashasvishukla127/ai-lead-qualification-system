from pydantic import ValidationError

from models import (
    LeadProfile,
    EmailDraft
)

# SWITCH PROVIDER HERE
from providers.groq_provider import generate_response

# Example:
# from providers.anthropic_provider import generate_response
# from providers.gemini_provider import generate_response


def clean_json(text: str) -> str:

    return (
        text.replace("```json", "")
        .replace("```", "")
        .strip()
    )


async def analyse_lead(
    lead_text: str
) -> LeadProfile | None:

    system_prompt = """
You are a mortgage broker assistant.

Return ONLY valid JSON.

JSON schema:

{
    "intent_score": 8,
    "situation_summary": "Customer is looking for a first home loan.",
    "urgency": "high",
    "is_first_buyer": true,
    "recommended_approach": "Schedule consultation immediately.",
    "confidence": 0.92
}
"""

    try:

        text = await generate_response(
            system_prompt=system_prompt,
            user_prompt=lead_text,
            temperature=0
        )

        cleaned = clean_json(text)

        return LeadProfile.model_validate_json(
            cleaned
        )

    except ValidationError as e:
        print(f"Pydantic validation failed:\n{e}")
        return None

    except Exception as e:
        print(f"Unexpected error:\n{e}")
        return None


async def draft_email(
    lead_profile: LeadProfile
) -> EmailDraft | None:

    system_prompt = """
You are an expert mortgage broker assistant.

Write warm personalised mortgage emails.

Return ONLY valid JSON.

JSON schema:

{
  "subject": "Helping You With Your First Home Loan",
  "body": "Hi John...",
  "tone_score": 8,
  "word_count": 120,
  "key_personalisation": "References urgency and first-home situation."
}
"""

    try:

        text = await generate_response(
            system_prompt=system_prompt,
            user_prompt=f"""
Lead Profile:
{lead_profile.model_dump()}
""",
            temperature=0.6
        )

        cleaned = clean_json(text)

        email = EmailDraft.model_validate_json(
            cleaned
        )

        return email

    except Exception as e:
        print(f"Error generating email:\n{e}")
        return None


async def process_lead(
    lead_text: str
):

    lead_profile = await analyse_lead(
        lead_text
    )

    if lead_profile is None:
        return {"error": "Lead analysis failed"}

    email_draft = await draft_email(
        lead_profile
    )

    return {
        "lead_profile": lead_profile,
        "email_draft": email_draft
    }


async def generate_followup(
    lead_profile: LeadProfile,
    follow_up_number: int,
    days_since_last_contact: int,
    previous_emails: list[str]
) -> EmailDraft | None:

    strategies = {
        1: "Helpful value-add follow-up.",
        2: "Urgency-based follow-up.",
        3: "Polite final check-in."
    }

    strategy = strategies.get(
        follow_up_number,
        "Friendly follow-up"
    )

    system_prompt = f"""
You are an expert mortgage broker assistant.

Write a personalised follow-up email.

Strategy:
{strategy}

Avoid repeating previous emails.

Return ONLY valid JSON.

JSON schema:

{{
  "subject": "Checking In About Your Home Loan",
  "body": "Hi John...",
  "tone_score": 8,
  "word_count": 120,
  "key_personalisation": "References urgency and first-home situation."
}}
"""

    try:

        text = await generate_response(
            system_prompt=system_prompt,
            user_prompt=f"""
Lead Profile:
{lead_profile.model_dump()}

Days Since Last Contact:
{days_since_last_contact}

Previous Emails:
{previous_emails}

Generate follow-up #{follow_up_number}
""",
            temperature=0.6
        )

        cleaned = clean_json(text)

        return EmailDraft.model_validate_json(
            cleaned
        )

    except Exception as e:
        print(f"Error generating follow-up:\n{e}")
        return None