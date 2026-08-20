# AI Engineering — 7-Week Summer Training

A public log of a 7-week AI Engineering training program: every day, every project, and every bug along the way.

Rather than a single polished final project, this repo keeps the full path — from first environment setup to a working, deployed capstone.

**Author:** Azzam Fahdel Alshamrani — Information Technology, King Abdulaziz University
**Duration:** 7 weeks · 35 working days · 46 commits

---

## Capstone — Scout

**Scout** is a bilingual (Arabic/English) multi-user Telegram bot that monitors YouTube channels and delivers AI-generated summaries of new videos.

- Users submit a channel via chat; the bot resolves the channel ID and saves the subscription
- New uploads are detected through YouTube RSS polling (no API key required)
- Video transcripts are summarized through an LLM and delivered to Telegram
- Multi-user session state, so each user manages their own channel list

📂 [`week7/`](week7/)

---

## Week by week

| Week | Focus | What was built |
|------|-------|----------------|
| [1](week1/) | Foundations | Python, Git, and Docker environment; prompt patterns; a Dockerized text summarizer with PDF/TXT output |
| [2](week2/) | Spec-first development | Password Strength Checker — written from a spec, reviewed, deliberately broken and debugged, with a Streamlit UI |
| [3](week3/) | Writing for AI | Specs, system prompts, and structured context — practiced on a Book Tracker CLI |
| [4](week4/) | Claude Skills | Analyzed existing skills, then built a custom `inbox-triage` skill and chained it with document generation |
| [5](week5/) | Agentic AI | TL;DR Link Cruncher — an agent with web and YouTube tools, persistent memory, and 8 automated guardrail tests |
| [6](week6/) | Automation | A Telegram bot built in n8n: two workflow chains, scheduled polling, LLM summarization, and an approval gate |
| [7](week7/) | Capstone | Scout — see above |

---

## Stack

`Python` · `Docker` · `Streamlit` · `n8n` · `Telegram Bot API` · `Groq` · `Gemini` · `Git`

---

## Notes

Each week folder is organized as `day1`–`day5`. Test logs record bugs in a bug / cause / fix format — including the ones that took a while to find.
