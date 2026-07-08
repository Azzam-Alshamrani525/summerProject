from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="You are a certified nutritionist. A client asks you: " \
    "'Is grilled chicken breast a high-protein food?' Classify it as high-protein or not, and explain why.",
    config=types.GenerateContentConfig(
        max_output_tokens=400,
        temperature=0.7,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )
)
print(response.text)