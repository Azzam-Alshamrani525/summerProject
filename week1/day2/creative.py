from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain the difference between muscle failure and muscle soreness using a fun analogy"
    " or metaphor, as if explaining it to a friend who's never worked out before.",
    config=types.GenerateContentConfig(
        max_output_tokens=400,
        temperature=0.9,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )
)

print(response.text)