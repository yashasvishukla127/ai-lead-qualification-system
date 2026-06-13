# test/test_models.py
import asyncio

from src.services.lead_service import (
    process_lead,
    generate_followup
)


def print_separator(title: str):

    print("\n" + "=" * 60)
    print(f"{title}")
    print("=" * 60)


def print_email(title: str, email):

    print_separator(title)

    print(f"SUBJECT:\n{email.subject}\n")

    print(f"BODY:\n{email.body}\n")

    print(f"TONE SCORE: {email.tone_score}")

    print(f"WORD COUNT: {email.word_count}")

    print(
        f"KEY PERSONALISATION:\n"
        f"{email.key_personalisation}"
    )


def print_lead_profile(lead_profile):

    print_separator("LEAD PROFILE")

    print(
        f"INTENT SCORE: "
        f"{lead_profile.intent_score}"
    )

    print(
        f"URGENCY: "
        f"{lead_profile.urgency}"
    )

    print(
        f"FIRST BUYER: "
        f"{lead_profile.is_first_buyer}"
    )

    print(
        f"CONFIDENCE: "
        f"{lead_profile.confidence}"
    )

    print(
        f"\nSITUATION SUMMARY:\n"
        f"{lead_profile.situation_summary}"
    )

    print(
        f"\nRECOMMENDED APPROACH:\n"
        f"{lead_profile.recommended_approach}"
    )


async def main():

    fake_lead = """
        Young couple urgently looking for first home loan approval.
        """

    result = await process_lead(
        fake_lead
    )

    if "error" in result:

        print_separator("ERROR")

        print(result["error"])

        return

    lead_profile = result["lead_profile"]

    initial_email = result["email_draft"]

    print_lead_profile(
        lead_profile
    )

    print_email(
        "INITIAL EMAIL",
        initial_email
    )

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

            print_email(
                f"FOLLOW-UP {i}",
                followup
            )

            previous_emails.append(
                followup.body
            )


if __name__ == "__main__":
    asyncio.run(main())