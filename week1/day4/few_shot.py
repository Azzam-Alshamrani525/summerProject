from google import genai
from google.genai import types
import os
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="""Classify each food as High-Protein or Not High-Protein, with a one-sentence reason.
Food: Lentils
Classification: High-Protein
Reason: Contains about 18g of protein per cooked cup, making it a strong plant-based source.
Food: White rice
Classification: Not High-Protein
Reason: Contains only about 4g of protein per cooked cup and is mostly carbohydrate.
Food: Grilled chicken breast
Classification:""",
    config=types.GenerateContentConfig(
        max_output_tokens=400,
        temperature=0.7,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )
)
print(response.text)