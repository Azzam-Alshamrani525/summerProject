# Project: YouTube Channel Summarizer Bot (n8n)

## 1. Objective
A Telegram bot, built in n8n, that lets a user either (a) get a one-time AI summary of any YouTube video, or (b) start ongoing monitoring of a YouTube channel — automatically summarizing and delivering each new upload as it's posted.

## 2. Current Status
Two working chains exist right now. Everything below is built and tested, not planned.

---

## 3. Chain A — Channel Submission (Telegram Trigger branch)

**Trigger:** Telegram Trigger, "On message" — fires on any incoming message to the bot.

**Flow, in order:**
1. **`if youtube link`** (IF node) — checks if message text contains `youtube.com` or `youtu.be`.
   - False → `no youtube link` — sends "not a YouTube link" message. End.
   - True → continue.
2. **`if youtube vid`** (IF node) — checks if the text contains `watch?v=` or `youtu.be/` (i.e. is it a video link, not a channel link).
   - True (video link) → `oEmbed for youtube vid` (HTTP Request, GET) — calls `https://www.youtube.com/oembed?url={{ encodeURIComponent($json.message.text) }}&format=json`. Returns `author_name` (channel name) and `author_url` (channel page link). No auth needed, public endpoint.
   - False (channel link, e.g. `@handle`) → skips oEmbed, goes straight to next step using the original message text.
3. **`fetch channel page`** (HTTP Request, GET) — both branches converge here. URL: `{{ $json.author_url || $json.message.text }}`. Fetches the raw HTML of the channel's page.
4. **`extract channle ID`** (Code node, JavaScript) — parses the HTML for a channel ID using two fallback regex patterns (some channel types, e.g. YouTube "Topic" channels, don't embed the ID the same way as normal channels):
   ```javascript
   const html = $input.first().json.data;
   let match = html.match(/"channelId":"(UC[a-zA-Z0-9_-]{22})"/);
   if (!match) {
     match = html.match(/youtube\.com\/channel\/(UC[a-zA-Z0-9_-]{22})/);
   }
   if (!match) { throw new Error("Could not find a channel ID in the page HTML"); }
   const channelId = match[1];
   const titleMatch = html.match(/<title>(.*?)<\/title>/);
   const channelName = titleMatch ? titleMatch[1].replace(/ - YouTube$/, '') : 'Unknown channel';
   return [{ json: { channelId, channelName, rssUrl: `https://www.youtube.com/feeds/videos.xml?channel_id=${channelId}` } }];
   ```
5. **`start monitoring this channle?`** (Telegram — Send and Wait for Response, Response Type: Approval, both buttons enabled) — asks to confirm, includes the video link (with underscores escaped via `.replace(/_/g, '\\_')`) so the user can watch it without reading further. Message must avoid raw unescaped underscores/URLs in text (Telegram's default parser breaks on unpaired `_` — treats it as markdown italics).
6. **`approve or disaprove of monitring the channle`** (IF node) — checks `{{ $json.data.approved }}` is Boolean `true`.
   - False → `not monitoring message` — short "okay, not monitoring" reply. End.
   - True → continue.
7. **`Edit Fields1`** — builds three clean fields: `channelId`, `channelName`, `rssUrl` (all String type), referencing `$('extract channle ID').item.json...` since by this point `$json` no longer points to that node's data.
8. **`Convert to File`** (Convert to JSON, output field `data`) — converts the fields from Edit Fields1 into a binary JSON file. Required because the next node (Update) needs binary input, unlike the Create operation used earlier which took raw text directly. Note: this node wraps its output in an array even for a single item — the downstream reader (Chain B, step 2) must account for this.
9. **`Update file`** (Google Drive — Resource: File, Operation: **Update**, file selected via "From list", Input Data Field Name: `data`) — overwrites the same `channel_config.json` in the dedicated Drive folder (`n8n_channel_summarizer`) in place. **Important: originally built with "Create From Text," which created a new duplicate file every approval — Chain B's Download node stayed pinned to the first/oldest file. Switched to Update specifically to fix this.**
10. **`confirm monitring message`** — sends "✅ Now monitoring [channel]" confirmation.

---

## 4. Chain B — Scheduled Summarization (Schedule Trigger branch)

**Trigger:** Schedule Trigger — currently set to run periodically (interval adjustable).

**Flow, in order:**
1. **`Download file`** (Google Drive — Operation: Download, file selected via "From list" — must point at the exact same file `Update file` in Chain A writes to) — downloads the current `channel_config.json` from the same Drive folder.
2. **`Code in JavaScript`** — parses the downloaded binary into usable JSON. Must unwrap the array `Convert to File` wraps single items in (content arrives as `[{...}]`, not `{...}`; n8n's Code node requires `json` to be a plain object, not an array):
   ```javascript
   const buffer = await this.helpers.getBinaryDataBuffer(0, 'data');
   const text = buffer.toString('utf-8');
   const parsed = JSON.parse(text);
   const data = Array.isArray(parsed) ? parsed[0] : parsed;
   return [{ json: data }];
   ```
3. **`RSS Read`** — URL field set to `{{ $json.rssUrl }}` **in Expression mode** (must toggle the fx/Expression switch, not Fixed — this is a recurring gotcha throughout the project).
4. **`Limit`** — Max Items: 1 (keeps only the newest video from the feed).
5. **`Edit Fields`** — extracts clean `title` and `link` from the RSS item.
6. **`HTTP Request`** (Groq call #1) — POST to `https://api.groq.com/openai/v1/chat/completions`, model `openai/gpt-oss-20b`, prompt asks for an intro sentence + 3 bullet points based on the video title. `max_tokens: 1500` (this model spends tokens on internal `reasoning` before `content` — too-low token limits produce an empty `content` field). Auth: Header Auth credential, header `Authorization`, value `Bearer <groq_api_key>`. Body must be in **Expression** mode.
   - Error output → `error grok 1` — sends `⚠️ Workflow failed: {{ $workflow.name }} / Node: HTTP Request (Groq #1) / Error: HTTP {{ $json.error.status }}`.
7. **`HTTP Request1`** (Groq call #2) — takes call #1's output and reformats it into a short, Telegram-style message (emoji, no markdown headers). References call #1 by name: `{{ $('HTTP Request').item.json.choices[0].message.content }}` — wrapped in `JSON.stringify(...).slice(1,-1)` if the text contains raw line breaks, since those break JSON string bodies otherwise.
   - Error output → `error grok 2` — same alert pattern as above.
8. **`Send message and wait for response`** (Telegram — Send and Wait, Approval type, custom labels "Yes, start monitoring" / "No, Don't" — reused pattern) — asks "📺 {{ $('Code in JavaScript').item.json.channelName }} uploaded a new video: '{{ $('Edit Fields').item.json.title }}' — 🔗 {{ $('Edit Fields').item.json.link.replace(/_/g, '\\_') }} — Want to receive it?" (link included and underscore-escaped so the user can watch before deciding on the summary).
9. **`approve or disaprove of vid summery`** (IF) — checks `{{ $json.data.approved }}` is Boolean `true`.
   - True → `approve message` — sends the real final message: `{{ $('Edit Fields').item.json.title }}` + `{{ $('HTTP Request1').item.json.choices[0].message.content }}` + `🔗 {{ $('Edit Fields').item.json.link }}`.
   - False → `disapprove` — short "skipped" message.

---

## 5. Error Handling (built, Day 4)
- Both Groq HTTP Request nodes use **"On Error: Continue (using error output)"** in node Settings — gives each a second red output for failures, wired to dedicated Telegram alert nodes (see steps 6/7 above in Chain B).
- A separate workflow-level Error Trigger workflow was also built but found **unreliable** — confirmed via Executions tab that real production failures didn't trigger it, despite correct configuration (known n8n issue, not a config mistake). Per-node error handling above is the one actually relied upon.
- "Append n8n Attribution" turned off on all Telegram send nodes (removes the "sent automatically with n8n" footer).

## 6. Known Recurring Bugs (worth checking first if something breaks)
- **Expression vs Fixed mode**: any `{{ }}` that doesn't seem to evaluate — check the fx/Expression toggle on that specific field first.
- **Telegram markdown parser**: unpaired underscores in message text (e.g. inside URLs or channel IDs) crash message sends with "can't find end of the entity." Either escape (`.replace(/_/g, '\\_')`) or avoid putting raw URLs in text bodies where not essential.
- **Node references after inserting new steps**: `$json` only ever means "immediately previous node." After adding approval/IF nodes mid-chain, downstream nodes referencing old data must switch to `$('NodeName').item.json...` by name.
- **n8n 2.0+ blocks local file writes by default** (`Read/Write Files from Disk` fails "not writable" on any path unless `N8N_RESTRICT_FILE_ACCESS_TO` env var explicitly allows it). Project moved to Google Drive storage instead of fighting this.
- **n8n binary data** is stored as a filesystem reference internally, not raw accessible bytes — use `await this.helpers.getBinaryDataBuffer(0, 'data')`, not manual `.data.data` access.
- **"Create From Text" duplicates files instead of overwriting**: each approval created a new `channel_config.json`, and Chain B's Download node stayed pinned to the first one it was ever pointed at (via "From list," which selects a specific file, not "whatever's newest"). Fixed by switching Chain A's save step to Update instead of Create.
- **"Update" operation needs binary input, not raw text** — unlike Create From Text. Requires a Convert to File node beforehand.
- **Convert to File wraps output in an array**, even for a single item — downstream JSON.parse gets `[{...}]`, not `{...}`. Must check `Array.isArray()` and unwrap before returning as `json` (n8n requires `json` to be a plain object).

## 7. Infrastructure
- **n8n**: self-hosted, installed globally (`npm install -g n8n`, launched with `n8n` — not `npx n8n`, which re-downloads on every launch).
- **Public HTTPS tunnel**: currently `ngrok` (`ngrok http 5678`), required for Telegram Trigger's webhook and "Send and Wait" approval buttons (Telegram rejects `localhost` button URLs). URL changes every ngrok restart — must set `WEBHOOK_URL` env var to the current ngrok URL before each `n8n` launch. **Known pain point, accepted as temporary** — real fix (Cloudflare Tunnel + free Namecheat domain from GitHub Student Pack) deferred until actual deployment, not needed for local dev/testing.
- **Google Drive credential**: required a manually created Google Cloud OAuth app (Client ID + Secret) — self-hosted n8n has no built-in Google login shortcut. One-time setup, done.
- **Telegram bot**: created via @BotFather, token stored as n8n credential. Chat ID for the primary user: `1087117148`.
- **Groq**: model `openai/gpt-oss-20b`, API key stored as n8n Header Auth credential.

## 8. Deployment Readiness
Logic is fully proven end-to-end locally. **Not yet deployed.** Still needed before going live:
- Move n8n to a real server (not local machine + ngrok)
- Point a real domain (Student Pack Namecheat domain via Cloudflare) at that server
- Replace Google Drive JSON storage with a real database (Postgres planned)
- Build the Streamlit frontend (not started)

---

## 9. NEXT PHASE — Vision (not yet built, this is the spec for it)

Goal: turn the bot into a proper guided conversational flow instead of "just send a link and it figures out what you meant."

### 9.1 Entry point
- Bot listens for `/start`. Telegram's own client automatically shows a native "START" button the first time a user opens a chat with a never-before-messaged bot — tapping it silently sends `/start`. No custom UI needed for this part; it's a Telegram platform behavior, not something to build.
- On `/start` received → send a welcome/explainer message with an inline button (via Send and Wait, Approval-type, single button) to begin.

### 9.2 Path selection
- After the start button is tapped (same execution, continues via n8n's Send and Wait — this does NOT trigger a new webhook/execution, it resumes the paused one) → ask: **"Just summarize something, or monitor a channel?"** — two buttons (Send and Wait, Approval type, "Approve and Disapprove" mode repurposed as the two choices, or consider if n8n supports custom multi-button labeling beyond just approve/disapprove for a cleaner UX — verify this when building).

### 9.3 Path A — One-time summary
- Bot asks (Send and Wait, **Free Text** response type — NOT Approval) — "Send me a link."
- User's typed reply arrives within the SAME execution (this is the key mechanism — Free Text response type pauses and resumes on arbitrary text reply, unlike Approval which only handles button taps).
- Accepts any URL, not just YouTube (website articles or videos).
- Runs through Groq call #1 only (reuse existing prompt/node) — **skip Groq call #2 entirely for this path** — send call #1's raw output directly to the user. No monitoring, no file write, no approval step. One-shot.

### 9.4 Path B — Monitor
- Bot asks (Send and Wait, Free Text type) — "Send me the channel or video link."
- Reply must be validated as a YouTube link specifically (reuse existing `if youtube link` logic). If not YouTube → reply "Wrong — not a YouTube link" and re-prompt or end (decide which when building).
- If valid → proceeds into the EXISTING Chain A pipeline described in section 3 above (steps 2 onward: video-vs-channel check, oEmbed, ID extraction, approval, Drive save) — fully reused, not rebuilt.

### 9.5 Stop/exit command
- `/stop` — a plain slash command, checked as an **exact match** (not "contains"), completely independent of whatever guided flow state exists. Chosen over a persistent Telegram reply-keyboard button for simplicity: no risk of colliding with real URLs, no extra UI state to maintain alongside the existing inline Approval/Free-Text buttons already in use elsewhere.
- On `/stop` received → clear/reset the monitored channel (exact mechanism TBD when building — e.g. overwrite `channel_config.json` to empty/null, or delete it) so Chain B's schedule either does nothing or waits for a new setup.

### 9.6 Design rationale (why this works statelessly)
- Telegram Trigger fires fresh, with no memory, on every new incoming message — this is a hard platform/n8n constraint, not a bug.
- The entire guided flow (9.1–9.4) sidesteps this by staying inside ONE continuous execution via chained Send and Wait nodes (mixing Approval type for button choices and Free Text type for actual text/link input) — no external state storage needed for the guided part.
- `/stop` (9.5) doesn't need conversation memory either, since it's an unambiguous, always-checkable exact-match command independent of any active flow.

---

## 10. Open Questions / Decide When Building
- Exact UX for "Summarize or Monitor?" button labeling (n8n's Approval type is really built for approve/disapprove semantics — confirm it supports arbitrary two-choice labeling cleanly, or consider Custom Form response type instead).
- What happens if a non-YouTube link is sent in Path B after re-prompting — re-ask indefinitely, or give up after N tries?
- Exact mechanism for "clearing" monitoring on `/stop` (empty file vs. delete vs. a status flag inside the file).
