import os
import json

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from src.models import LeadProfile


load_dotenv()

client = AsyncAnthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


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

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
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

        lead_profile = LeadProfile.model_validate_json(text)

        return lead_profile

    except json.JSONDecodeError:
        return None