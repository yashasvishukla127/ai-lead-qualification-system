import os
import asyncio

from groq import AsyncGroq, AuthenticationError, RateLimitError, APIConnectionError
from dotenv import load_dotenv

from exceptions import ProviderError

load_dotenv()

client = AsyncGroq(
    api_key=os.getenv("GROQ_API_KEY")
)


async def generate_response(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0
) -> str:

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            max_tokens=700,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    except AuthenticationError as e:
        raise ProviderError(
            provider="groq",
            error_type="AuthenticationError",
            detail=f"Invalid API key — check GROQ_API_KEY in .env | {e}",
            retryable=False
        )

    except RateLimitError as e:
        raise ProviderError(
            provider="groq",
            error_type="RateLimitError",
            detail=str(e),
            retryable=True
        )

    except APIConnectionError as e:
        raise ProviderError(
            provider="groq",
            error_type="APIConnectionError",
            detail=str(e),
            retryable=True
        )