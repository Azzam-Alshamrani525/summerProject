# Week 6 — Day 1: Automation Foundations & Intro to n8n

## Task
Build an n8n workflow that runs on a schedule and performs at least two connected actions.

## What this builds toward
Full week goal: auto-detect a new upload from an informational YouTube channel, summarize it, and send the summary to WhatsApp. Day 1 only covers detection — no summarization or messaging yet.

## Workflow: Schedule Trigger → RSS Read → Limit

- **Schedule Trigger** — runs every 1 hour (interval not critical at this stage; testing is done via manual execution)
- **RSS Read** — polls the channel's RSS feed:
  `https://www.youtube.com/feeds/videos.xml?channel_id=UCYskjD6IuQJrxrW3I0EriZA`
  (channel: أسئلة نص الليل / @noselleel)
- **Limit** — set to Max Items = 1, keeps only the newest video from the feed

## Design decisions

- **Original idea (scrapped):** schedule a workflow to re-read Link Cruncher's `memory.json` and produce a digest. Rejected because `memory.json` doesn't change on its own — a schedule only makes sense when it's checking something external that updates independently. Reused the summarization logic idea but moved the "what to check" to an actual live source (a YouTube channel's feed) instead of static local data.
- **RSS Feed Trigger vs. RSS Read vs. Schedule Trigger:** n8n has two RSS-related nodes that look similar but behave differently:
  - *RSS Feed Trigger* — self-contained, polls on its own timer, only fires on new items
  - *RSS Read* — plain action node, does nothing unless something else calls it
  - Went with **Schedule Trigger → RSS Read** instead of RSS Feed Trigger alone, since it was already built and tested working.
- **Limit node added** because RSS Read returns the entire feed (15 items), not just the newest video. Without it, every run would reprocess all 15 videos instead of just the latest one.

## Deferred to later days
- Actual summarization of the video (Day 2 — connecting external APIs, reuse Groq logic from Week 5)
- Sending the summary to WhatsApp (likely Day 2–3, needs a messaging API connection)
- Handling "no new video" / failure cases (Day 4 — error handling & human-in-the-loop)

## Files
- `workflow.json` — exported n8n workflow
