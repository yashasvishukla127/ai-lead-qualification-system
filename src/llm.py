import os
import json

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from models import LeadProfile , EmailDraft
from pydantic import ValidationError

load_dotenv()  # from .env 

client = AsyncAnthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY") #so that it can take api keys
)

#async so that system don't wait until there is waiting period for response
async def analyse_lead(lead_text: str) -> LeadProfile | None:
    """
    Analyse a mortgage lead using Claude and return
    a validated LeadProfile object.
    """

    system_prompt = """
    You are a mortgage broker assistant.
    You must respond ONLY with valid JSON.
    The JSON must match this schema exactly:

    {
        "intent_score": 8,
        "situation_summary": "Customer is looking for a first home loan.",
        "urgency": "high",
        "is_first_buyer": true,
        "recommended_approach": "Schedule a consultation call immediately.",
        "confidence": 0.92
    }

    Rules:
    - intent_score must be between 1 and 10
    - urgency must be one of: low, medium, high
    - confidence must be between 0 and 1
    - Return ONLY JSON
    """

    try:       #try running this code is something crashes don't kill whole program
        response = await client.messages.create(        #await here means wait until response comes
            model="claude-haiku-4-5",
            max_tokens=250,
            temperature=0,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": lead_text
                }
            ]
        )

        text = "".join(
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        ).strip()

        cleaned_text = text.replace("```json", "").replace("```", "").strip()

        lead_profile = LeadProfile.model_validate_json(cleaned_text)

        return lead_profile

   
    except ValidationError as e: 
        print(f"Pydantic validation failed:\n{e}") 
        return None 
    
    except Exception as e:
        print(f"Unexpected error:\n{e}")
        return None
    

async def draft_email(lead_profile: LeadProfile) -> EmailDraft | None:
    """
    Generate a personalised mortgage broker email draft
    based on a LeadProfile.
    """

    system_prompt = """
        You are an expert mortgage broker assistant.

        Write warm, human, personalised mortgage outreach emails.

        You must respond ONLY with valid JSON.

        The JSON must match this schema exactly:

        {
        "subject": "Helping You With Your First Home Loan",
        "body": "Hi John, ...",
        "tone_score": 8,
        "word_count": 120,
        "key_personalisation": "Mentions the customer's urgency for first-home approval."
        }

        Rules:
        - tone_score must be between 1 and 10
        - word_count must be an integer
        - key_personalisation should explain what makes the email personalised
        - Return ONLY JSON
        """

    try:

        response = await client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=400,
            temperature=0.6,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"""
Generate a personalised mortgage email for this lead:

{lead_profile.model_dump()}
"""
                }
            ]
        )

        text = "".join(
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        ).strip()

        cleaned_text = (
            text.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        print("\nRAW LLM RESPONSE:")
        print(cleaned_text)

        email_draft = EmailDraft.model_validate_json(cleaned_text)

        print(f"\nDraft 1 score: {email_draft.tone_score}")

        # Self-review loop
        if email_draft.tone_score < 7:

            refined_draft = await refine_email(
                email_draft,
                lead_profile
            )

            if refined_draft:

                print(
                    f"Draft 1 score: {email_draft.tone_score} "
                    f"→ Draft 2 score: {refined_draft.tone_score}"
                )

                return refined_draft

        return email_draft

    except Exception as e:
        print(f"Error generating email draft: {e}")
        return None
    


async def refine_email(
    draft: EmailDraft,
    lead_profile: LeadProfile
) -> EmailDraft | None:
    """
    Critique and improve an existing email draft.
    """

    system_prompt = """
        You are an expert mortgage broker email reviewer.

        Your task:
        1. Critique weak parts of the email
        2. Improve warmth and personalization
        3. Improve clarity and human tone

        You must respond ONLY with valid JSON.

        The JSON must match this schema exactly:

        {
        "subject": "Helping You With Your First Home Loan",
        "body": "Hi John...",
        "tone_score": 9,
        "word_count": 140,
        "key_personalisation": "Mentions urgency and first-home buyer situation."
        }

        Rules:
        - tone_score must be between 1 and 10
        - Return ONLY JSON
        """

    try:

        response = await client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=400,
            temperature=0.4,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Lead Profile:

                    {lead_profile.model_dump()}

                    Current Email Draft:

                    {draft.model_dump()}

                    Critique the weaknesses in this draft and improve it.
                    """
                 }
                ]
                )

        text = "".join(
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        ).strip()

        cleaned_text = (
            text.replace("```json", "")
            .replace("```", "")
            .strip()
        )
        print("\nRAW LLM RESPONSE:")
        print(cleaned_text)
        refined_email = EmailDraft.model_validate_json(cleaned_text)

        return refined_email

    except Exception as e:
        print(f"Error refining email: {e}")
        return None