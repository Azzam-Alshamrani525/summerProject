from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain the difference between muscle failure and muscle soreness in detail." \
    " Cover: what causes each, when each one happens (during vs. after a workout)," \
    " how each one feels physically, and whether either one is a sign of a good workout.",
    config=types.GenerateContentConfig(
        max_output_tokens=500,
        temperature=0.7,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )
)

print(response.text)