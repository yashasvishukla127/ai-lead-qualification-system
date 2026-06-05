import os

from groq import AsyncGroq
from dotenv import load_dotenv


load_dotenv()

client = AsyncGroq(
    api_key=os.getenv("GROQ_API_KEY")
)


async def generate_response(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0
) -> str:

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        max_tokens=700,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()