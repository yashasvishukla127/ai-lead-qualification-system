import asyncio

from llm import (
    process_lead,
    generate_followup
)


async def main():

    fake_lead = """
Young couple urgently looking for first home loan approval.
"""

    result = await process_lead(
        fake_lead
    )

    print("\nFULL PIPELINE RESULT:")
    print(result)

    if "error" in result:
        return

    lead_profile = result["lead_profile"]
    initial_email = result["email_draft"]

    print("\nINITIAL EMAIL:")
    print(initial_email.model_dump())

    previous_emails = [
        initial_email.body
    ]

    for i in range(1, 4):

        followup = await generate_followup(
            lead_profile=lead_profile,
            follow_up_number=i,
            days_since_last_contact=i * 3,
            previous_emails=previous_emails
        )

        if followup:

            print(f"\nFOLLOW-UP {i}:")
            print(followup.model_dump())

            previous_emails.append(
                followup.body
            )


if __name__ == "__main__":
    asyncio.run(main())