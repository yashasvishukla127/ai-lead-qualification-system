import os

from groq import AsyncGroq
from dotenv import load_dotenv

from models import LeadProfile, EmailDraft
from pydantic import ValidationError


load_dotenv()

client = AsyncGroq(
    api_key=os.getenv("GROQ_API_KEY")
)


async def analyse_lead(
    lead_text: str
) -> LeadProfile | None:

    system_prompt = """
You are a mortgage broker assistant.

You must respond ONLY with valid JSON.

JSON schema:

{
    "intent_score": 8,
    "situation_summary": "Customer is looking for a first home loan.",
    "urgency": "high",
    "is_first_buyer": true,
    "recommended_approach": "Schedule a consultation call immediately.",
    "confidence": 0.92
}

Rules:
- intent_score between 1 and 10
- urgency must be low, medium, or high
- confidence between 0 and 1
- Return ONLY raw JSON
"""

    try:

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0,
            max_tokens=500,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": lead_text
                }
            ]
        )

        text = response.choices[0].message.content.strip()

        cleaned_text = (
            text.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        lead_profile = LeadProfile.model_validate_json(
            cleaned_text
        )

        return lead_profile

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

Write warm, personalised mortgage outreach emails.

Return ONLY valid JSON.

JSON schema:

{
  "subject": "Helping You With Your First Home Loan",
  "body": "Hi John...",
  "tone_score": 8,
  "word_count": 120,
  "key_personalisation": "Mentions urgency and first-home situation."
}
"""

    try:

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            max_tokens=700,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"""
Generate a personalised mortgage email.

Lead Profile:
{lead_profile.model_dump()}
"""
                }
            ]
        )

        text = response.choices[0].message.content.strip()

        cleaned_text = (
            text.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        email_draft = EmailDraft.model_validate_json(
            cleaned_text
        )

        print(f"\nDraft 1 score: {email_draft.tone_score}")

        if email_draft.tone_score < 7:

            refined = await refine_email(
                email_draft,
                lead_profile
            )

            if refined:

                print(
                    f"Draft 1 score: "
                    f"{email_draft.tone_score}"
                    f" → Draft 2 score: "
                    f"{refined.tone_score}"
                )

                return refined

        return email_draft

    except Exception as e:
        print(f"Error generating email: {e}")
        return None


async def refine_email(
    draft: EmailDraft,
    lead_profile: LeadProfile
) -> EmailDraft | None:

    system_prompt = """
You are an expert mortgage broker email reviewer.

Improve warmth, personalization, and clarity.

Return ONLY valid JSON.
"""

    try:

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=700,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"""
Lead Profile:
{lead_profile.model_dump()}

Current Draft:
{draft.model_dump()}

Improve this email.
"""
                }
            ]
        )

        text = response.choices[0].message.content.strip()

        cleaned_text = (
            text.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        refined_email = EmailDraft.model_validate_json(
            cleaned_text
        )

        return refined_email

    except Exception as e:
        print(f"Error refining email: {e}")
        return None


async def process_lead(lead_text: str):

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
        1: """
Helpful value-add follow-up.
Provide useful mortgage guidance.
No pressure.
""",

        2: """
Urgency-based follow-up.
Explain why acting sooner may help.
Encourage conversation.
""",

        3: """
Polite final check-in.
Warm professional closure.
No pressure.
"""
    }

    strategy = strategies.get(
        follow_up_number,
        "Friendly follow-up."
    )

    system_prompt = f"""
You are an expert mortgage broker assistant.

Write a personalised follow-up email.

Follow-up strategy:
{strategy}

IMPORTANT:
- Reference the customer's original situation
- Avoid repeating previous emails
- Sound warm and human
- Keep email concise

You must respond ONLY with valid JSON.

The JSON MUST match this schema EXACTLY:

{{
  "subject": "Checking In About Your Home Loan",
  "body": "Hi John...",
  "tone_score": 8,
  "word_count": 120,
  "key_personalisation": "References urgency and first-home situation."
}}

Rules:
- tone_score must be between 1 and 10
- word_count must be an integer
- key_personalisation must explain why the email feels personalised
- Return ONLY raw JSON
- Do NOT wrap JSON in markdown
- Do NOT explain anything
"""

    try:

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            max_tokens=700,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"""
Lead Profile:
{lead_profile.model_dump()}

Days Since Last Contact:
{days_since_last_contact}

Previous Emails:
{previous_emails}

Generate follow-up #{follow_up_number}.
"""
                }
            ]
        )

        text = response.choices[0].message.content.strip()

        print("\nRAW FOLLOW-UP RESPONSE:")
        print(text)

        cleaned_text = (
            text.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        followup = EmailDraft.model_validate_json(
            cleaned_text
        )

        return followup

    except ValidationError as e:
        print(f"Pydantic validation failed:\n{e}")
        return None

    except Exception as e:
        print(f"Error generating follow-up: {e}")
        return None