import asyncio
import json
from datetime import datetime

import anthropic
from pydantic import ValidationError

from models import (
    LeadProfile,
    EmailDraft
)

# SWITCH PROVIDER  
from providers.groq_provider import generate_response

 
# from providers.anthropic_provider import generate_response
# from providers.gemini_provider import generate_response


def log_error(function_name: str, error_type: str, detail: str) -> None:
    timestamp = datetime.now().isoformat()
    line = f"[{timestamp}] | {function_name} | {error_type} | {detail}\n"
    with open("errors.log", "a", encoding="utf-8") as f:
        f.write(line)


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

        try:
            text = await generate_response(
                system_prompt=system_prompt,
                user_prompt=lead_text,
                temperature=0
            )
        except anthropic.RateLimitError:
            await asyncio.sleep(10)
            text = await generate_response(
                system_prompt=system_prompt,
                user_prompt=lead_text,
                temperature=0
            )

        cleaned = clean_json(text)

        return LeadProfile.model_validate_json(
            cleaned
        )

    except anthropic.APIConnectionError as e:
        log_error("analyse_lead", "APIConnectionError", str(e))
        return None

    except anthropic.RateLimitError as e:
        log_error("analyse_lead", "RateLimitError", str(e))
        return None

    except anthropic.APIStatusError as e:
        log_error("analyse_lead", "APIStatusError", f"{e.status_code} {e.message}")
        return None

    except json.JSONDecodeError:
        log_error("analyse_lead", "JSONDecodeError", text)
        return None

    except ValidationError as e:
        log_error("analyse_lead", "ValidationError", str(e.errors()))
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

        try:
            text = await generate_response(
                system_prompt=system_prompt,
                user_prompt=f"""
Lead Profile:
{lead_profile.model_dump()}
""",
                temperature=0.6
            )
        except anthropic.RateLimitError:
            await asyncio.sleep(10)
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

    except anthropic.APIConnectionError as e:
        log_error("draft_email", "APIConnectionError", str(e))
        return None

    except anthropic.RateLimitError as e:
        log_error("draft_email", "RateLimitError", str(e))
        return None

    except anthropic.APIStatusError as e:
        log_error("draft_email", "APIStatusError", f"{e.status_code} {e.message}")
        return None

    except json.JSONDecodeError:
        log_error("draft_email", "JSONDecodeError", text)
        return None

    except ValidationError as e:
        log_error("draft_email", "ValidationError", str(e.errors()))
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