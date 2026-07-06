from google import genai
from google.genai import types
import os
#has Role, Task, Format/Constraints
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

chat = client.chats.create(
    model="gemini-3.1-flash-lite",
    config=types.GenerateContentConfig(
        max_output_tokens=200,
        temperature=0.7,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        system_instruction="You are a certified personal trainer."
    )
)

print("Chat started (Constraints prompt). Type 'exit' to quit.")
first_message = ("Explain the difference between muscle failure and muscle soreness. "
                  "Respond in exactly 3 bullet points. Keep your response under 120 words total.")
print("You:", first_message)
response = chat.send_message(first_message)
print("AI:", response.text)

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    response = chat.send_message(user_input)
    print("AI:", response.text)