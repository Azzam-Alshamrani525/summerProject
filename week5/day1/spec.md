# TL;DR Link Cruncher — Agent Spec (v1)

## Objective
Given a single web link, produce a fast, accurate digest of the content so the
user gets the core value without reading/watching the full thing.

v1 scope: **web articles only**. Video (YouTube) support is planned for Day 3.

## Why this is an agent, not static automation
The agent must *decide* which points in the source are actually the most
important — a judgment call, not a fixed extraction rule (e.g. "first 3
sentences"). It reasons over the whole content before producing an answer.

## Inputs
- One URL, sent by the user

## Available Tools
### v1 (Day 1–2)
- **Webpage reader tool** — fetches the page at the given URL and returns
  clean, readable article text (stripped of ads/nav/boilerplate)

### Planned (Day 3)
- **YouTube transcript reader tool** — fetches the transcript of a YouTube
  video link
- **Memory** — remembers links already summarized, so repeat requests don't
  redo work from scratch

## Outputs
On a successful fetch:
- **2–5 bullet points** — count is *not* fixed. The agent decides how many
  distinct key points the content actually has and outputs that many.
- **1-sentence conclusion**

On a failed fetch (see Guardrails below):
- A short plain error message. No bullets. No fabricated summary.

## Content Rules
- Each bullet must be a **genuinely distinct point**. No two bullets may
  restate the same idea in different words.
- Never pad the bullet count to hit a target number — if the article only
  supports 2 solid distinct points, output 2.
- Never omit content just to force a round number.

## Decision Process (reasoning loop)
1. Receive the URL.
2. Call the webpage reader tool to fetch the content.
3. Check whether the fetch returned usable article text.
   - **No** → return the v1 error message (see Guardrails), stop.
   - **Yes** → continue.
4. Read and reason over the full text to identify the distinct key points
   (not just the opening paragraph).
5. Condense findings into 2–5 non-redundant bullets + 1 conclusion sentence.
6. Return the result to the user.

## Guardrails (v1 — minimal, refined Day 5)
- If the fetch fails, returns empty content, or the page isn't readable
  article text (e.g. dead link, blocked page): return a plain error message
  stating the content couldn't be retrieved from that link. Do not guess at
  or invent a summary.
- v1 does **not** yet distinguish *why* it failed (paywall vs. broken link
  vs. non-article page) — that refinement is deferred to Day 5.

## Out of Scope for v1 (explicitly deferred, not silently dropped)
- YouTube/video link support → **Day 3**
- Memory of previously summarized links → **Day 3**
- Distinguishing failure reasons (paywall/broken/non-article) → **Day 5**
- Multi-link batches (not planned this week)

## Open Question for Day 3
Once video support is added: how should the agent handle a genuinely
important detail from a video that doesn't fit as one of the main
takeaways (e.g. a strong aside)? Two candidate options to test with real
videos before deciding:
- (a) Add a small optional "Also noted" section for such details
- (b) Stay strict — if it's not important enough to be a bullet, it isn't
  surfaced at all

Decision will be made after testing on real video content, not upfront.

## Definition of Done — Day 1
- [x] Objective defined
- [x] Tools (current + planned) defined
- [x] Inputs/outputs defined, including failure-case output
- [x] Decision process written as an explicit step-by-step loop
- [x] Content rules (bullet count range, no redundancy, no padding) defined
- [x] Out-of-scope items explicitly listed, not silently assumed
- [x] Open question for Day 3 flagged for future testing, not decided now
