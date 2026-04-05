"""AI helper for generating quote text with OpenAI."""
from app import config


def generate_service_description(service_name: str, keywords: str = "") -> str:
    if not config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not configured in the .env file.")

    try:
        from openai import OpenAI
    except ImportError:
        raise ValueError("The openai package is not installed. Run: pip install openai")

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    prompt_parts = [f"Service: {service_name}"]
    if keywords.strip():
        prompt_parts.append(f"Keywords: {keywords}")

    user_content = "\n".join(prompt_parts)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional quote writer for a modern service business. "
                    "Write a concise and clear description of a service or product to include in a quote. "
                    "Use English, 1-3 sentences, professional tone, and focus on what is delivered. "
                    "Return only the description text and nothing else."
                ),
            },
            {"role": "user", "content": user_content},
        ],
        max_tokens=200,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
