from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="You are a certified personal trainer." \
    " A new client asked: 'What's the difference between muscle failure and being sore?' " \
    "Answer in under 80 words,between every 20 words put a new line." \
    " using simple everyday language, no jargon, and end with one practical tip for the gym.",
    config=types.GenerateContentConfig(
        max_output_tokens=400,
        temperature=0.7,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )
)

print(response.text)