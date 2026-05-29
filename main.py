import os

from anthropic import Anthropic
from dotenv import load_dotenv


def test_connection() -> None:
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found")

    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Say hello in one sentence"
            }
        ],
    )

    text = "".join(
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text"
    ).strip()

    print(text)

    usage = response.usage

    print("\n=== Token Usage ===")
    print(f"Input tokens  : {usage.input_tokens}")
    print(f"Output tokens : {usage.output_tokens}")

    # Optional fields
    if hasattr(usage, "cache_creation_input_tokens"):
        print(f"Cache write   : {usage.cache_creation_input_tokens}")

    if hasattr(usage, "cache_read_input_tokens"):
        print(f"Cache read    : {usage.cache_read_input_tokens}")


if __name__ == "__main__":
    test_connection()




client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),  # This is the default and can be omitted
)
page = client.beta.models.list()
page = page.data[0]
print(page.id)