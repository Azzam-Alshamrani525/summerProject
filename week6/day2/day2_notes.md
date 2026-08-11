# Week 6 — Day 2: Connecting Tools & APIs in n8n

## Task
Connect two external APIs inside n8n and exchange data between them successfully.

## What got added
Workflow now: Schedule Trigger → RSS Read → Limit → Edit Fields → HTTP Request

- **Edit Fields** — pulls clean `title` and `link` out of the RSS item
- **HTTP Request** — calls Groq (`api.groq.com/openai/v1/chat/completions`), sends the video title, asks for a 2-3 sentence summary of what the video is likely about

Two APIs connected: YouTube RSS feed → Groq completions. Data flows from one into the other.

## Scope decision
Summarizing just the **title**, not the full transcript, for now. Getting a real transcript needs a third-party API (YouTube has no official one) — deferring that to a later day so today stays focused on proving the API-to-API connection works.

## Bugs found and fixed

| Bug | Cause | Fix |
|---|---|---|
| Edit Fields output was empty/errored | Put the `{{ $json.title }}` expression in the field *name* box instead of the *value* box | Name = plain text (`title`), Value = the expression |
| Groq replied asking "what title?" instead of summarizing | *(false lead — turned out this was a stale response from before the next fix, not the real cause)* | Re-ran after confirming Expression mode |
| Same issue, real cause | Body's "Fixed / Expression" toggle needs to be on **Expression**, or n8n treats the JSON body as plain text and never substitutes `{{ }}` | Switched toggle to Expression |

## Other things learned
- HTTP Request auth: Groq needs a `Header Auth` credential, header name `Authorization`, value `Bearer <api_key>` (space between Bearer and key)
- API keys are stored as n8n credentials, not typed into the node body — so they don't leak if the workflow JSON is exported/shared
- Nodes need to be actually wired together (drag connector dot to dot) — adding a node near another doesn't connect it. "No input connected" on a node is the tell.

## Deferred
- Real transcript-based summary (needs a transcript API)
- Extracting just the clean summary text out of Groq's full response object (currently buried in `choices[0].message.content`)
- WhatsApp delivery

## Files
- `workflow.json` — exported n8n workflow
