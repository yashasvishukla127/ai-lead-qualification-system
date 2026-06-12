from pathlib import Path

# This gives the absolute folder path of the executing script
file_dir = Path(__file__).resolve().parent
print(f"File directory: {file_dir}")
# D:\ai engineering\Agentic Ai\src\providers-groq_provider.py
import os
import asyncio

from groq import AsyncGroq, AuthenticationError, RateLimitError, APIConnectionError
from dotenv import load_dotenv

from src.exceptions import ProviderError

from src.utils.cost_tracker import log_cost

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
        if not hasattr(response.usage, "input_tokens"):
            response.usage.input_tokens = response.usage.prompt_tokens
        if not hasattr(response.usage, "output_tokens"):
            response.usage.output_tokens = response.usage.completion_tokens

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        log_cost(function_name="generate_response", input_tokens=input_tokens, output_tokens=output_tokens)

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