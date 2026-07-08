from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Is grilled chicken breast a high-protein food? " \
    "Think through this step by step: first state the approximate protein content per typical serving, " \
    "then compare it to a general threshold for what counts as 'high-protein', then give your final classification.",
    config=types.GenerateContentConfig(
        max_output_tokens=400,
        temperature=0.7,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )
)
print(response.text)