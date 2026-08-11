# Week 6 — Day 5: End-to-End Automation

## Task
Build an end-to-end automation that receives input, processes it with AI, stores the result, and sends a notification.

## What this is
Replaced the hardcoded channel with a real submission flow: send the bot a YouTube link, approve it, and it becomes the live monitored channel — no more editing the workflow to change channels.

## New branch: channel submission
Telegram Trigger (on message) → IF (is it a YouTube link?) → IF (video link or channel link?)
- **Video link** → HTTP Request to YouTube's oEmbed endpoint (`youtube.com/oembed?url=...&format=json`, free, no key) → returns the channel name/URL for that video
- **Channel link** → skips oEmbed, used directly
- Both converge → HTTP Request fetches the channel page HTML → Code node extracts `channelId` via regex (two fallback patterns, since some channel types like YouTube "Topic" channels don't embed the ID the same way) and builds `channelId`, `channelName`, `rssUrl`
- **Send and Wait (Approval)** — asks to confirm monitoring this channel, includes the video link (underscores escaped) so the user can watch it without reading the summary first
- On approve → Edit Fields (builds clean object) → **Convert to File** (JSON) → **Google Drive: Update file** (overwrites the same `channel_config.json`, picked via "From list" — not Create, which made a new duplicate file every approval) → confirmation message
- On disapprove → short "not monitoring" message

## Existing branch: now reads the file dynamically
Schedule Trigger → **Google Drive: Download file** (same file, selected via "From list") → Code node (parses binary → JSON, unwraps the array Convert to File wraps single items in) → RSS Read (URL = `{{ $json.rssUrl }}`, must be in Expression mode) → rest unchanged

## Bugs fixed
- **Binary data parsing** — n8n stores binary as a filesystem reference now, not raw base64 directly accessible via `.data.data`. Fixed using n8n's official helper: `await this.helpers.getBinaryDataBuffer(0, 'data')`.
- **RSS Read URL stayed literal text** — field was in Fixed mode, not Expression. Same bug class as Day 2/3, keeps recurring — always check the fx toggle when an expression doesn't seem to apply.
- **Telegram markdown parse error on approval message** — underscores in channel IDs/URLs broke Telegram's default parser (reads `_..._` as italics). Fixed by escaping (`.replace(/_/g, '\\_')`) or removing the raw URL from messages where not essential.
- **Local file write blocked** — n8n 2.0+ restricts "Read/Write Files from Disk" by default (security feature), fails silently with "not writable" on any path unless `N8N_RESTRICT_FILE_ACCESS_TO` env var explicitly allows it. Abandoned local disk entirely in favor of Google Drive instead — no permission fights, and it's closer to where storage is heading anyway (Streamlit + real DB later).
- **"Create file from text" made a new duplicate file every approval** — schedule chain kept downloading the first (oldest) file instead of the latest channel, since Download's "From list" selector stays pinned to whichever file was picked at setup. Fixed by switching the save step to **Update** (overwrites in place) instead of Create.
- **"Update file" needs binary, not raw text** — unlike Create From Text, the Update operation expects a binary field. Added a **Convert to File** node before it.
- **Convert to File wraps output in an array** — even for one item, so the downloaded content back in Chain B was `[{...}]` not `{...}`, which broke the Code node's JSON parse (n8n requires `json` to be a plain object, not an array). Fixed by checking `Array.isArray(parsed)` and unwrapping to `parsed[0]` if needed.

## Infra notes
- **ngrok** still used for testing (temporary public HTTPS, required for Telegram approval buttons + Trigger webhook). URL changes every restart — accepted as a dev-only cost for now, not solved permanently. Considered: GitHub Student Pack free domain + Cloudflare Tunnel for a fixed URL, deferred until actual deployment.
- **Switched `npx n8n` → global install** (`npm install -g n8n`, launch with just `n8n`) — npx was re-downloading n8n on every launch, costing ~10 min each session.
- **Google Drive credential** — required a real Google Cloud OAuth app (Client ID + Secret), since self-hosted n8n has no built-in Google login. One-time setup, done.

## Deployment readiness
**This is semi-ready for real deployment.** The logic is fully proven: channel submission, approval, storage, dynamic feed reading, summarization, error handling, all working end-to-end locally. What's still local/temporary and needs replacing before going live:
- n8n itself → needs a real server (not local machine + ngrok)
- Domain → Student Pack Namecheat domain + Cloudflare, pointed at that server
- Storage → currently Google Drive JSON; fine for now, real DB (Postgres) planned once deployed
- Streamlit frontend → not built yet, planned alongside deployment

## Files
- `workflow.json`
