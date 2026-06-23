# D:\ai engineering\Agentic Ai\src\providers-groq_provider.py

from pathlib import Path
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
            max_tokens=1200,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ]
        )
        if not hasattr(response.usage, "input_tokens"): #if response.usage do not have "input tokens" then input token = prompt token
            response.usage.input_tokens = response.usage.prompt_tokens # becaz some times response.usage do not have "input tokens"
                # but we need to give output in tokens format 
        if not hasattr(response.usage, "output_tokens"):
            response.usage.output_tokens = response.usage.completion_tokens

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        log_cost(function_name="generate_response", input_tokens=input_tokens, output_tokens=output_tokens)
            # usualy response gives the output in dict format - and multiple choices hence we need 1st choice 
        return response.choices[0].message.content.strip()

    except AuthenticationError as e:
        raise ProviderError(
            provider="groq",
            error_type="AuthenticationError",
            detail=f"Invalid API key — check GROQ_API_KEY in .env | {e}",
            retryable=False
        )
                # when we get to many requests then it will throw RateLimitError
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