# src/tests/test_errors.py

import asyncio
import os
from unittest.mock import AsyncMock, patch

# ── pick which provider to test ──────────────────────────
PROVIDER = "groq"       # change to "anthropic" to test that
# ────────────────────────────────────────────────────────

if PROVIDER == "groq":
    import groq as sdk
    PATCH_TARGET = "src.providers.groq_provider.client"
else:
    import anthropic as sdk
    PATCH_TARGET = "src.providers.anthropic_provider.client"

from src.services.lead_service import analyse_lead
from src.models import LeadProfile


FAKE_LEAD = "Young couple urgently needs first home loan."

VALID_LEAD_PROFILE = LeadProfile(
    intent_score=8,
    situation_summary="First home buyer.",
    urgency="high",
    is_first_buyer=True,
    recommended_approach="Call immediately.",
    confidence=0.92
)


def print_log():
    log_path = os.path.join(os.path.dirname(__file__), "..", "errors.log")
    print("\n── errors.log tail ──────────────────────────")
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
            # print last 3 lines only
            for line in lines[-3:]:
                print(line.strip())
    except FileNotFoundError:
        print("  (errors.log not created yet)")
    print("─────────────────────────────────────────────\n")


# ════════════════════════════════════════════════════════
# ERROR 1 — AuthenticationError (Groq) / APIStatusError 401 (Anthropic)
# HOW: pass a wrong API key in .env
# ════════════════════════════════════════════════════════
async def test_bad_api_key():
    print("\n>>> TEST 1: Bad API Key")
    print("ACTION: Set a wrong key in .env and run normally")
    print("No mock needed — just run: python test_models.py with bad key")
    print("Expected log entry:")
    if PROVIDER == "groq":
        print("  | AuthenticationError | [groq] Invalid API key")
    else:
        print("  | APIStatusError | [anthropic] Status 401")


# ════════════════════════════════════════════════════════
# ERROR 2 — RateLimitError
# HOW: mock the SDK to raise it
# ════════════════════════════════════════════════════════
async def test_rate_limit():
    print("\n>>> TEST 2: RateLimitError")

    if PROVIDER == "groq":
        error_to_raise = sdk.RateLimitError(
            message="Rate limit exceeded",
            response=AsyncMock(status_code=429),
            body={}
        )
        mock_path = "src.providers.groq_provider.client.chat.completions.create"
    else:
        error_to_raise = sdk.RateLimitError(
            message="Rate limit exceeded",
            response=AsyncMock(status_code=429),
            body={}
        )
        mock_path = "src.providers.anthropic_provider.client.messages.create"

    with patch(mock_path, new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = error_to_raise
        result = await analyse_lead(FAKE_LEAD)
        print(f"  Result: {result}")
        print_log()


# ════════════════════════════════════════════════════════
# ERROR 3 — APIConnectionError
# HOW: mock the SDK to raise it
# ════════════════════════════════════════════════════════
async def test_connection_error():
    print("\n>>> TEST 3: APIConnectionError")

    if PROVIDER == "groq":
        error_to_raise = sdk.APIConnectionError(request=AsyncMock())
        mock_path = "src.providers.groq_provider.client.chat.completions.create"
    else:
        error_to_raise = sdk.APIConnectionError(request=AsyncMock())
        mock_path = "src.providers.anthropic_provider.client.messages.create"

    with patch(mock_path, new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = error_to_raise
        result = await analyse_lead(FAKE_LEAD)
        print(f"  Result: {result}")
        print_log()


# ════════════════════════════════════════════════════════
# ERROR 4 — JSONDecodeError
# HOW: mock generate_response to return plain text, not JSON
# ════════════════════════════════════════════════════════
async def test_json_decode_error():
    print("\n>>> TEST 4: JSONDecodeError")

    with patch(
        "src.services.lead_service.generate_response",
        new_callable=AsyncMock
    ) as mock_gen:

        # model returns plain English instead of JSON
        mock_gen.return_value = "Sorry, I cannot help with that request."

        result = await analyse_lead(FAKE_LEAD)
        print(f"  Result: {result}")
        print_log()


# ════════════════════════════════════════════════════════
# ERROR 5 — ValidationError
# HOW: mock generate_response to return JSON with wrong fields
# ════════════════════════════════════════════════════════
async def test_validation_error():
    print("\n>>> TEST 5: ValidationError (wrong JSON schema)")

    with patch(
        "src.services.lead_service.generate_response",
        new_callable=AsyncMock
    ) as mock_gen:

        # valid JSON but missing required fields / wrong types
        mock_gen.return_value = '{"intent_score": "not-a-number", "urgency": "extreme"}'

        result = await analyse_lead(FAKE_LEAD)
        print(f"  Result: {result}")
        print_log()


# ════════════════════════════════════════════════════════
# ERROR 6 — APIStatusError (Anthropic only — e.g. 500)
# ════════════════════════════════════════════════════════
async def test_api_status_error():
    print("\n>>> TEST 6: APIStatusError (Anthropic 500)")

    if PROVIDER != "anthropic":
        print("  Skipped — only applies to Anthropic provider")
        return

    import httpx
    error_to_raise = sdk.APIStatusError(
        message="Internal server error",
        response=httpx.Response(500),
        body={}
    )

    with patch(
        "src.providers.anthropic_provider.client.messages.create",
        new_callable=AsyncMock
    ) as mock_call:
        mock_call.side_effect = error_to_raise
        result = await analyse_lead(FAKE_LEAD)
        print(f"  Result: {result}")
        print_log()


# ════════════════════════════════════════════════════════
# RUN ALL
# ════════════════════════════════════════════════════════
async def main():
    print(f"\n{'='*50}")
    print(f"  Testing error logs for: {PROVIDER.upper()}")
    print(f"{'='*50}")

    await test_bad_api_key()
    await test_rate_limit()
    await test_connection_error()
    await test_json_decode_error()
    await test_validation_error()
    await test_api_status_error()

    print("\n✅ All tests done. Check errors.log for entries.")


if __name__ == "__main__":
    asyncio.run(main())