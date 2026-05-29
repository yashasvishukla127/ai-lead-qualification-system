from src.models import LeadProfile


lead = LeadProfile(
    intent_score=15,
    situation_summary="Customer looking for a 2BHK apartment.",
    urgency="high",
    is_first_buyer=True,
    recommended_approach="Schedule a consultation call.",
    confidence=0.92
)

print(lead)

print(lead.model_dump())
LeadProfile.model_validate(lead)


import asyncio

from src.llm import analyse_lead


async def main():

    fake_lead_1 = """
    Young couple urgently looking for first home loan approval.
    """

    result = await analyse_lead(fake_lead_1)

    print(result)

    if result:
        print(result.model_dump())


if __name__ == "__main__":
    asyncio.run(main())