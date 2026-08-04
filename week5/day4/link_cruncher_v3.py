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
    except Exception:
        return None

    if downloaded is None:
        return None

    text = trafilatura.extract(downloaded)
    if not text or len(text.strip()) < 200:
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
        return None

    try:
        transcript_list = YouTubeTranscriptApi().fetch(video_id)
        text = " ".join(chunk.text for chunk in transcript_list)
    except Exception:
        return None

    if not text or len(text.strip()) < 200:
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
        max_tokens=1200,
        temperature=0.3,
    )

    return response.choices[0].message.content


# ---------- URL extraction (for multi-link input) ----------

def extract_urls(text: str) -> list[str]:
    """
    Finds all URLs in a single line of input. Lets the user paste one
    link (business as usual) or several at once (space/comma separated)
    without needing a special command or menu.
    """
    matches = re.findall(r"https?://[^\s,]+", text)
    return matches


# ---------- Per-link agent step ----------

def summarize_one_link(url: str, memory: dict) -> tuple[str, str]:
    """
    Runs the full single-link pipeline (memory check -> fetch -> summarize).
    Returns (display_text, clean_summary):
      - display_text: what gets printed for this link (may include a
        memory or truncation note)
      - clean_summary: just the actual summary content, with no notes,
        used as input to the cross-link synthesis step
    """
    if url in memory:
        clean_summary = memory[url]
        display_text = f"(from memory - already summarized this link)\n\n{clean_summary}"
        return display_text, clean_summary

    content_text, source_type = fetch_content(url)

    if content_text is None:
        error_text = (
            f"Couldn't retrieve readable content from that {source_type} "
            "link. It may be broken, blocked, private, or (for video) "
            "missing captions."
        )
        return error_text, ""  # empty clean_summary = excluded from synthesis

    content_text, was_truncated = truncate_content(content_text)
    clean_summary = summarize(content_text)

    display_text = clean_summary
    if was_truncated:
        display_text = (
            "(note: this content was long and was truncated before "
            "summarizing - the summary may miss points from later in "
            "the piece)\n\n" + clean_summary
        )

    memory[url] = clean_summary
    save_memory(memory)
    return display_text, clean_summary


# ---------- Cross-link synthesis (Day 4: new reasoning step) ----------

def synthesize_common_theme(summaries: list[str]) -> str:
    """
    New Day 4 step: after all individual links are summarized, reason
    across ALL of them together to find the common thread. This is the
    'decomposition' part - the big task (summarize + compare N links)
    only makes sense once broken into: summarize each -> then synthesize.
    """
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    combined = "\n\n---\n\n".join(
        f"Summary {i+1}:\n{s}" for i, s in enumerate(summaries)
    )

    system_prompt = (
        "You will be given several independent summaries, each from a "
        "different article or video. Identify the SPECIFIC, concrete "
        "connection across all of them - not a vague restatement like "
        "'they're all about the same broad subject.' Name the precise "
        "thread that ties them together (e.g. a shared event, mechanism, "
        "person, or cause-and-effect link between them). If they "
        "genuinely don't share a meaningful connection beyond a broad "
        "topic, say so plainly instead of forcing one. "
        "Respond in 2-3 sentences, no preamble."
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": combined},
        ],
        max_tokens=700,
        temperature=0.3,
    )

    content = response.choices[0].message.content
    if not content or not content.strip():
        return "(the model returned an empty response for the synthesis step - try again)"
    return content


# ---------- Agent loop (single link - kept for backward compatibility) ----------

def run_agent(url: str, memory: dict) -> str:
    display_text, _ = summarize_one_link(url, memory)
    return display_text


if __name__ == "__main__":
    memory = load_memory()

    while True:
        raw_input_line = input("Paste a link (or 'exit'): ").strip()
        if raw_input_line.lower() == "exit":
            break

        urls = extract_urls(raw_input_line)

        if not urls:
            print("\nNo valid link found in that input.\n")
            continue

        if len(urls) == 1:
            # Single-link path - unchanged from Day 2/3
            print()
            print(run_agent(urls[0], memory))
            print()
            continue

        # --- Multi-link path (Day 4: planning & decomposition) ---
        print(f"\nDetected {len(urls)} links. Plan: summarize each individually, "
              f"then find the common theme across all of them.\n")

        clean_summaries = []
        for i, url in enumerate(urls, start=1):
            print(f"--- Link {i}/{len(urls)}: {url} ---")
            display_text, clean_summary = summarize_one_link(url, memory)
            print(display_text)
            print()
            if clean_summary:  # skip failed links when synthesizing
                clean_summaries.append(clean_summary)

        if len(clean_summaries) < 2:
            print("Not enough successful summaries to find a common theme.\n")
            continue

        print("--- Common theme across all links ---")
        print(synthesize_common_theme(clean_summaries))
        print()
