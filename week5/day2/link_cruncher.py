"""
TL;DR Link Cruncher — Day 2 (single-tool agent)

Tool: webpage reader (trafilatura) — fetches a URL and extracts clean
article text, stripped of navigation/ads/related-content clutter.

Reasoning: Groq (openai/gpt-oss-20b) reads the clean text and produces
2-5 non-redundant bullet points + a 1-sentence conclusion, per spec.md.

Run:
    python link_cruncher.py
"""

import os
import trafilatura
from groq import Groq

GROQ_MODEL = "openai/gpt-oss-20b"


def fetch_article_text(url: str) -> str | None:
    """
    The agent's one tool: fetch a URL and extract clean article text.
    Returns None if the page couldn't be fetched or had no extractable
    article content (dead link, blocked page, non-article page, etc.).
    """
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        return None

    text = trafilatura.extract(downloaded)
    if not text or len(text.strip()) < 200:
        # Too little content to be a real article (e.g. a landing page)
        return None

    return text


def summarize(article_text: str) -> str:
    """
    The agent's reasoning step. Sends the clean article text to Groq
    with the rules from spec.md and returns the formatted digest.
    """
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    system_prompt = (
        "You are a careful summarizing agent. You will be given the full "
        "text of a web article. Your job:\n"
        "1. Identify the genuinely distinct key points in the article. "
        "Do not pad, and do not force a fixed count.\n"
        "2. Output between 2 and 5 bullet points, one per distinct key "
        "point. Never output two bullets that restate the same idea.\n"
        "3. Output exactly one final sentence labeled 'Conclusion:' that "
        "captures the article's overall takeaway.\n"
        "Do not add any other commentary, preamble, or headers besides "
        "the bullets and the Conclusion line."
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": article_text},
        ],
        max_tokens=600,
        temperature=0.3,
    )

    return response.choices[0].message.content


def run_agent(url: str) -> str:
    """
    The full Day 2 agent loop:
    receive URL -> call tool -> check result -> reason -> return output
    """
    article_text = fetch_article_text(url)

    if article_text is None:
        return (
            "Couldn't retrieve readable article content from that link. "
            "It may be broken, blocked, or not an article page."
        )

    return summarize(article_text)


if __name__ == "__main__":
    url = input("Paste a link: ").strip()
    print()
    print(run_agent(url))
