---
name: inbox-triage
description: "Use this skill whenever the user wants to sort, triage, or prioritize a batch of emails — for example pasting in inbox contents, forwarding several emails, or asking 'what needs my attention today' or 'help me get through my inbox.' Also trigger on requests to categorize emails by urgency, flag what needs a reply, or summarize an inbox at a glance. This skill only sorts and prioritizes — it does not draft replies or take any action on the emails (archiving, deleting, sending). If the user wants a reply written, that's a separate task."
---

# Inbox Triage

Sorts a batch of emails into priority categories so the user can see what actually needs attention first, without reading every email top to bottom.

## When this applies

The user will typically provide multiple emails at once — pasted text, a forwarded thread, or a description of several messages. If given only one email, still categorize it, but mention that triage is most useful with a batch.

## Categories

Sort every email into exactly one of these:

1. **Urgent** — explicit deadline within 24-48 hours, or something concretely blocking/broken/time-critical *with identifiable stakes*. Words like "ASAP" or "urgent" are not sufficient on their own — see the urgency-language rule under Edge Cases.
2. **Needs Reply** — a direct question or request that specifically expects a response back from the user, no hard deadline. If the email just requires the user to eventually *do* something (fill out a form, make a selection) rather than reply to a person, that's Can Wait unless it has a near-term deadline, in which case it's Urgent.
3. **FYI** — informational, no action expected (status updates, confirmations, cc's)
4. **Can Wait** — low-stakes, no immediate action, could be handled whenever
5. **Noise** — newsletters, automated notifications, mass mail

See `references/category-rules.md` for the full signal list used to tell these apart — read it when a category boundary is unclear (e.g. deciding Urgent vs. Needs Reply).

## Output format

Always group by category, most urgent first. Within a category, no need to re-sort further unless dates are given. Use this shape:

```
## Urgent (2)
- [Sender] — [one-line reason it's urgent]

## Needs Reply (3)
- [Sender] — [what they're asking for]

## FYI (1)
- [Sender] — [what it's telling you]

## Can Wait (1)
- [Sender] — [why it's low priority]

## Noise (2)
- [Sender] — [newsletter/automated]
```

See `examples/sample-triage-output.md` for a full worked example.

## What this skill does NOT do

- Does not draft or send replies — only sorts and explains why
- Does not archive, delete, or move anything — the user acts on the sorted list themselves
- Does not guess at missing context — if an email's urgency genuinely can't be determined from what's given, put it in Needs Reply and say what's unclear, rather than silently picking a category

## Edge cases

- **Ambiguous sender importance** (e.g. unclear if this is the user's manager): default to Needs Reply rather than Urgent, and note the ambiguity — false urgency is worse than a missed one, since the user reviews this list themselves.
- **Urgency language without verifiable backing**: a sender claiming "ASAP" or "urgent" is not enough by itself — that's a claim, not evidence. Only mark Urgent if there's also a stated deadline, a known-important sender, or concrete stakes (something broken, blocking, or client-facing). Otherwise treat it like the ambiguous-sender case: Needs Reply, with a note that the claimed urgency couldn't be verified from what was given.
- **Threads with multiple messages**: triage the thread once, based on the most recent unresolved message, not each message separately.
- **Batch of 10+ emails**: still use the same category output format — don't add sub-grouping by sender or date unless asked.
