import os

from anthropic import AsyncAnthropic
from dotenv import load_dotenv


from utils.cost_tracker import log_cost

load_dotenv()

client = AsyncAnthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


async def generate_response(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0
) -> str:

    response = await client.messages.create(
        model="claude-3-5-sonnet-latest",
        temperature=temperature,
        max_tokens=700,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    log_cost(function_name="generate_response", input_tokens=input_tokens, output_tokens=output_tokens)

    text = "".join(
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text"
    ).strip()

    return text