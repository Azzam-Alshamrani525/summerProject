from google import genai
from google.genai import types
import os
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="""Classify grilled chicken breast as a food source. Respond ONLY in this exact format:
Food: [name]
Protein per 100g: [amount]
Classification: [High-Protein / Not High-Protein]
Reason: [one sentence]""",
    config=types.GenerateContentConfig(
        max_output_tokens=200,
        temperature=0.7,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )
)
print(response.text)