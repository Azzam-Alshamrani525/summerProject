"""
TL;DR Link Cruncher — Day 3 (2 tools + memory)

Tools:
  1. Webpage reader (trafilatura)      - Day 2
  2. YouTube transcript reader          - NEW

Memory: a JSON file (memory.json) that remembers links already
summarized, so a repeat link skips re-fetching/re-summarizing and
returns the cached result instantly. This is managed entirely by the
script - you never create, edit, or pass in the JSON file yourself.
You still only ever give the script a URL.

Run:
    python link_cruncher.py
Type 'exit' to quit.
"""

import os
import json
import re

import trafilatura
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi

GROQ_MODEL = "openai/gpt-oss-20b"
MEMORY_FILE = "memory.json"

# Groq's free tier caps a single request at 8000 tokens/minute (input +
# output combined). Long video transcripts can easily blow past this.
# ~18000 characters is a conservative estimate for staying well under
# that limit, leaving headroom for the system prompt (~150 tokens) and
# the response (max_tokens below).
MAX_INPUT_CHARS = 18000


def truncate_content(text: str, max_chars: int = MAX_INPUT_CHARS) -> tuple[str, bool]:
    """
    Returns (possibly-truncated text, was_truncated). Truncating loses
    whatever came after the cutoff - an accepted v1 limitation, same
    category as paywalled/blocked sources. Splitting long content into
    chunks and combining summaries is a better long-term fix, but is
    out of scope for now.
    """
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars], True


# ---------- Memory ----------

def load_memory() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(memory: dict) -> None:
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


# ---------- Tool 1: webpage reader ----------

def fetch_article_text(url: str) -> str | None:
    try:
        downloaded = trafilatura.fetch_url(url)
    except Exception as e:
        print(f"[DEBUG] fetch_url raised: {e}")
        return None

    if downloaded is None:
        print("[DEBUG] fetch_url returned None (request failed or was blocked)")
        return None

    text = trafilatura.extract(downloaded)
    if not text or len(text.strip()) < 200:
        print(f"[DEBUG] extract() returned too little text: {len(text.strip()) if text else 0} chars")
        return None
    return text


# ---------- Tool 2: YouTube transcript reader ----------

def extract_video_id(url: str) -> str | None:
    # Specifically requires 'v=' (watch?v=ID) or 'youtu.be/' (short link),
    # NOT a bare '/', which would incorrectly match the slashes in
    # 'https://' before ever reaching the actual video ID.
    match = re.search(r"(?:v=|youtu\.be/)([0-9A-Za-z_-]{11})", url)
    if match:
        return match.group(1)
    return None


def fetch_youtube_transcript(url: str) -> str | None:
    video_id = extract_video_id(url)
    if video_id is None:
        print("[DEBUG] Could not extract a video ID from that URL")
        return None
    print(f"[DEBUG] Extracted video ID: {video_id}")

    try:
        transcript_list = YouTubeTranscriptApi().fetch(video_id)
        text = " ".join(chunk.text for chunk in transcript_list)
    except Exception as e:
        print(f"[DEBUG] YouTubeTranscriptApi raised: {type(e).__name__}: {e}")
        return None

    if not text or len(text.strip()) < 200:
        print(f"[DEBUG] transcript too short: {len(text.strip()) if text else 0} chars")
        return None
    return text


# ---------- Routing: decide which tool to use ----------

def is_youtube_url(url: str) -> bool:
    return "youtube.com/watch" in url or "youtu.be/" in url


def fetch_content(url: str) -> tuple[str | None, str]:
    """
    Returns (content_text_or_None, source_type) where source_type is
    'video' or 'article' - used for a clearer error message.
    """
    if is_youtube_url(url):
        return fetch_youtube_transcript(url), "video"
    else:
        return fetch_article_text(url), "article"


# ---------- Reasoning step ----------

def summarize(content_text: str) -> str:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    system_prompt = (
        "You are a careful summarizing agent. You will be given the full "
        "text (article text or video transcript) of a piece of content. "
        "Your job:\n"
        "1. Identify the genuinely distinct key points. Do not pad, and "
        "do not force a fixed count.\n"
        "2. Output between 2 and 5 bullet points, one per distinct key "
        "point. Never output two bullets that restate the same idea.\n"
        "3. Output exactly one final sentence labeled 'Conclusion:' that "
        "captures the overall takeaway.\n"
        "Do not add any other commentary, preamble, or headers besides "
        "the bullets and the Conclusion line."
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content_text},
        ],
        max_tokens=1000,
        temperature=0.3,
    )

    return response.choices[0].message.content


# ---------- Agent loop ----------

def run_agent(url: str, memory: dict) -> str:
    if url in memory:
        return f"(from memory - already summarized this link)\n\n{memory[url]}"

    content_text, source_type = fetch_content(url)

    if content_text is None:
        return (
            f"Couldn't retrieve readable content from that {source_type} "
            "link. It may be broken, blocked, private, or (for video) "
            "missing captions."
        )

    content_text, was_truncated = truncate_content(content_text)

    result = summarize(content_text)
    if was_truncated:
        result = (
            "(note: this content was long and was truncated before "
            "summarizing - the summary may miss points from later in "
            "the piece)\n\n" + result
        )

    memory[url] = result
    save_memory(memory)
    return result


if __name__ == "__main__":
    memory = load_memory()

    while True:
        url = input("Paste a link (or 'exit'): ").strip()
        if url.lower() == "exit":
            break
        print()
        print(run_agent(url, memory))
        print()
