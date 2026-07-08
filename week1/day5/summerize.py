from google import genai
from google.genai import types
from fpdf import FPDF
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# --- Step 1: Get input text ---
print("Paste your text below. Type 'END' on its own line when finished:\n")
lines = []
while True:
    line = input("> ")
    if line.strip() == "END":
        break
    lines.append(line)
text = "\n".join(lines)

if not text.strip():
    print("No text entered. Exiting.")
    exit()

# --- Step 2: Ask user for output format ---
print("\nChoose output format:")
print("1) PDF")
print("2) TXT")
choice = input("Enter 1 or 2: ").strip()

# --- Step 3: Send ONLY the text to the LLM, asking for a plain summary ---
response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=f"Summarize the following text in a clear, concise paragraph:\n\n{text}",
    config=types.GenerateContentConfig(
        max_output_tokens=500,
        temperature=0.5,
        thinking_config=types.ThinkingConfig(thinking_budget=100)
    )
)
summary = response.text.strip()

print("\n--- Summary ---")
print(summary)

# --- Step 4: Local code handles the output format, not the LLM ---
if choice == "1":
    pdf = FPDF(format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", size=16)
    pdf.multi_cell(0, 10, summary)
    pdf.output("summary.pdf")
    print("\nSaved as summary.pdf")
elif choice == "2":
    with open("summarize.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    print("\nSaved as summarize.txt")
else:
    print("\nInvalid choice, nothing saved.")