# Week 6 — Day 4: Error Handling & Human-in-the-Loop

## Task
Add error handling and a human approval step to an existing workflow, then test both success and failure scenarios.

## Workflow
Schedule Trigger → RSS Read → Limit → Edit Fields → Groq #1 → Groq #2 → **Send and Wait for Response (approval)** → IF → [true: real message] / [false: discard note]

Error outputs on Groq #1 and Groq #2 both branch to their own Telegram alert node.

## Error handling — per-node (this is the one that works)
- On each HTTP Request node (Groq #1, Groq #2): **Settings → On Error → "Continue (using error output)"**
- This gives the node a second red "error" output on the canvas, separate from the normal success path
- Wired each error output to its own Telegram "Send a text message" node
- Alert text (kept short on purpose, no raw JSON):
```
⚠️ Workflow failed: {{ $workflow.name }}
Node: HTTP Request (Groq #1)
Error: HTTP {{ $json.error.status }}
```
(second alert node: same, but `Node: HTTP Request1 (Groq #2)`)
- Turned off "Append n8n Attribution" on these so no branding footer

## Error handling — workflow-level Error Trigger (NOT reliable, low priority)
- Built a separate `Week6 Error Handler` workflow (Error Trigger → Telegram)
- Linked via main workflow Settings → Error Workflow
- Works when run manually, but does **not** reliably fire on real automatic/production failures — confirmed via Executions tab (real failures happened, error handler showed nothing)
- This is a known issue (found other users reporting the same on n8n's community forum), not a config mistake
- Left in place but not depended on — the per-node error handling above is the one actually doing the job

## Human approval step
- Node: **Telegram → Send message and wait for response**
- Response Type: Approval
- **Approval Options → Type of Approval** must be manually set to show both buttons — defaults to approve-only otherwise
- Message asks whether to receive the video (channel name hardcoded for now, video title pulled live from Edit Fields):
```
📺 أسئلة نص الليل uploaded a new video: "{{ $('Edit Fields').item.json.title }}"
Want to receive it?
```
- **IF node** after it: `{{ $json.data.approved }}` is Boolean `true`
  - True → real final message sent (title + Groq #2 summary + link)
  - False → short "skipped" message

## Bugs fixed
- **IF node type mismatch** — condition was comparing a Boolean to a String. Fixed by setting the condition type to Boolean.
- **Broken node reference after adding approval step** — final message node used `{{ $json... }}` which after inserting the approval/IF nodes no longer pointed at Groq #2. Fixed by referencing nodes by name directly: `{{ $('HTTP Request1').item.json.choices[0].message.content }}`.
- **"Send and Wait" button URL rejected by Telegram** — Telegram requires public HTTPS for button links, `localhost` doesn't work. Fixed with `ngrok http 5678` to get a temporary public HTTPS URL, then restarted n8n with `WEBHOOK_URL` set to that ngrok URL. Note: URL changes every ngrok restart (free plan), needs redoing each session.

## Design decision
Originally planned to have the approval message just preview the draft, then resend the same content again on approval — realized that's redundant when approver and recipient are the same person. Settled on: approval message asks a real yes/no question (receive this video or not), and the final message on approval is a clean copy without buttons — not just a duplicate.

## Deferred to Day 5
Replace the hardcoded channel with a real setup flow: bot asks for a channel URL, you approve it via Send and Wait, and that becomes the monitored source going forward — real decision-with-consequence for the approval step, instead of just gating a message.

## Files
- `workflow.json` (main)
- `error_handler_workflow.json` (secondary, kept but not relied on)
