from google import genai
from google.genai import types
import os
#has Task, Context
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

chat = client.chats.create(
    model="gemini-3.1-flash-lite",
    config=types.GenerateContentConfig(
        max_output_tokens=200,
        temperature=0.7,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )
)

print("Chat started (Improved prompt). Type 'exit' to quit.")
first_message = ("I'm a beginner at the gym and I confuse feeling too tired to finish a set "
                  "with feeling sore the next day. Explain the difference between muscle failure "
                  "and muscle soreness. Keep your response under 120 words.")
print("You:", first_message)
response = chat.send_message(first_message)
print("AI:", response.text)

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    response = chat.send_message(user_input)
    print("AI:", response.text)