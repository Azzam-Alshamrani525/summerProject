from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="I'm a beginner at the gym and I keep confusing two things: feeling too tired to do another rep, "
    "and feeling sore the next day. Explain the difference between muscle failure and muscle soreness in simple terms.",
    config=types.GenerateContentConfig(
        max_output_tokens=400,
        temperature=0.7,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )
)

print(response.text)