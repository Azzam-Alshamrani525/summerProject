from groq import Groq
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = []  # holds the full conversation history

print("Chat started. Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",   # current supported model (llama-3.1-8b-instant is deprecated)
        messages=messages,
        max_tokens=300,
        temperature=0.7
    )

    reply = response.choices[0].message.content
    print("Groq:", reply)

    messages.append({"role": "assistant", "content": reply})