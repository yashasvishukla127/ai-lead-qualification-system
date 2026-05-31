import asyncio

from llm import analyse_lead, draft_email


async def main():

    fake_lead_1 = """
    Young couple urgently looking for first home loan approval.
    """

    lead_profile = await analyse_lead(fake_lead_1)

    print("\nLEAD PROFILE:")
    print(lead_profile)

    if lead_profile:

        email_draft = await draft_email(lead_profile)

        print("\nEMAIL DRAFT:")
        print(email_draft)

        if email_draft:
            print(email_draft.model_dump())


if __name__ == "__main__":
    asyncio.run(main())