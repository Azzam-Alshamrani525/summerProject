from groq import Groq
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": "What is the Kingdom of Saudi Arabia in 10 words?"}
    ],
    max_tokens=200,
    temperature=0.7
)

print(response.choices[0].message.content)