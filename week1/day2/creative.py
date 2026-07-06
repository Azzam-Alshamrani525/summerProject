from google import genai
from google.genai import types
import os
#has Role, Task, Context
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

chat = client.chats.create(
    model="gemini-3.1-flash-lite",
    config=types.GenerateContentConfig(
        max_output_tokens=250,
        temperature=0.9,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        system_instruction="You are an enthusiastic personal trainer who loves using vivid analogies."
    )
)

print("Chat started (Creative prompt). Type 'exit' to quit.")
first_message = ("A new client asked about the difference between muscle failure and muscle soreness. "
                  "Explain it using a fun, memorable analogy. Keep your response under 120 words.")
print("You:", first_message)
response = chat.send_message(first_message)
print("AI:", response.text)

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    response = chat.send_message(user_input)
    print("AI:", response.text)