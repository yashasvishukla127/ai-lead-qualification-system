# D:\ai engineering\Agentic Ai\src\services-lead_service.py


import asyncio
import json
import os
from datetime import datetime
from pydantic import ValidationError

# from models import LeadProfile, EmailDraft
# from exceptions import ProviderError
from src.models import LeadProfile, EmailDraft
from src.exceptions import ProviderError

import logging
logger = logging.getLogger(__name__)

# SWITCH PROVIDER HERE
#from providers.groq_provider import generate_response
from src.providers.groq_provider import generate_response
# from providers.anthropic_provider import generate_response
# from providers.gemini_provider import generate_response


# ── Logger ────────────────────────────────────────────────────────────────────

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "errors.log")

def log_error(function_name: str, error_type: str, detail: str) -> None:
    timestamp = datetime.now().isoformat()
    line = f"[{timestamp}] | {function_name} | {error_type} | {detail}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)


# ── Helpers ───────────────────────────────────────────────────────────────────

def clean_json(text: str) -> str:
    return (
        text.replace("```json", "")
            .replace("```", "")
            .strip()
    )


# ── Core functions ────────────────────────────────────────────────────────────

async def analyse_lead(lead_text: str) -> LeadProfile | None:

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

    text = None  # needed so JSONDecodeError handler can reference it safely 
    # if there is some error app do not crashes , instead it prints text 

    try:
        try:
            text = await generate_response(
                system_prompt=system_prompt,
                user_prompt=lead_text,
                temperature=0
            )
        except ProviderError as e:
            if e.retryable:
                log_error("analyse_lead", e.error_type, f"Retrying after 10s — {e}")
                await asyncio.sleep(10)
                text = await generate_response(
                    system_prompt=system_prompt,
                    user_prompt=lead_text,
                    temperature=0
                )
            else:
                raise  # non-retryable → fall to outer except

        cleaned = clean_json(text)
        return LeadProfile.model_validate_json(cleaned)

        # if not even retry then other left ones except would be checked

    except ProviderError as e:
        log_error("analyse_lead", e.error_type, str(e))
        return None

    except json.JSONDecodeError as e:
        log_error("analyse_lead", "JSONDecodeError", f"raw={text} | err={e}")
        return None

    except ValidationError as e:
        failed = [str(err["loc"]) for err in e.errors()]
        log_error("analyse_lead", "ValidationError", f"fields={failed}")
        return None


async def draft_email(lead_profile: LeadProfile) -> EmailDraft | None:

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

    text = None

    try:
        try:
            text = await generate_response(
                system_prompt=system_prompt,
                user_prompt=f"Lead Profile:\n{lead_profile.model_dump()}", #model_dump - for making python readable dictionary format
                temperature=0.6
            )
        except ProviderError as e:
            if e.retryable:
                log_error("draft_email", e.error_type, f"Retrying after 10s — {e}")
                await asyncio.sleep(10)
                text = await generate_response(
                    system_prompt=system_prompt,
                    user_prompt=f"Lead Profile:\n{lead_profile.model_dump()}",
                    temperature=0.6
                )
            else:
                raise

        cleaned = clean_json(text)
        return EmailDraft.model_validate_json(cleaned) #EmailDraft must contain 
                        # it validates ex. must contain subject ,body ,word_count ( all as defined)             
    except ProviderError as e:
        log_error("draft_email", e.error_type, str(e))
        return None

    except json.JSONDecodeError as e:
        log_error("draft_email", "JSONDecodeError", f"raw={text} | err={e}")
        return None

    except ValidationError as e:
        failed = [str(err["loc"]) for err in e.errors()]
        log_error("draft_email", "ValidationError", f"fields={failed}")
        return None


async def process_lead(lead_text: str):

    lead_profile = await analyse_lead(lead_text)

    if lead_profile is None:
        return {"error": "Lead analysis failed"}

    email_draft = await draft_email(lead_profile)

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

    strategy = strategies.get(follow_up_number, "Friendly follow-up")

    system_prompt = f"""
        You are an expert mortgage broker assistant.
        Write a personalised follow-up email.
        Strategy: {strategy}
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

    text = None

    try:
        text = await generate_response(
            system_prompt=system_prompt,
            user_prompt=f"""
            Lead Profile: {lead_profile.model_dump()}
            Days Since Last Contact: {days_since_last_contact}
            Previous Emails: {previous_emails}
            Generate follow-up #{follow_up_number}
            """,
            temperature=0.6
        )

        cleaned = clean_json(text)
        return EmailDraft.model_validate_json(cleaned)

    except ProviderError as e:
        log_error("generate_followup", e.error_type, str(e))
        return None

    except json.JSONDecodeError as e:
        log_error("generate_followup", "JSONDecodeError", f"raw={text} | err={e}")
        return None

    except ValidationError as e:
        failed = [str(err["loc"]) for err in e.errors()]
        log_error("generate_followup", "ValidationError", f"fields={failed}")
        return None