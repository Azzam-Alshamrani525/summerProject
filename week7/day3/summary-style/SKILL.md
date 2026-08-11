---
name: summary-style
description: The house style for every summary Summry_bot produces — a one-sentence intro plus exactly three bullets, in the reader's chosen language, never refusing. Use this skill whenever writing, editing, auditing, or debugging the Groq prompts inside the n8n workflow, whenever checking whether a summary the bot produced is acceptable, and whenever a summary comes back wrong (refusal, wrong language, wrong bullet count, broken Telegram formatting). Also use it when adding a new summarization path to the bot, so the new prompt matches the existing ones instead of drifting.
---

# Summry_bot summary style

Summry_bot summarizes web pages and YouTube videos and delivers the result over
Telegram. Three separate Groq calls produce user-facing text, and they must all
sound like the same bot. This skill is the single definition of what "correct
output" means, so the prompts can be regenerated or audited without guessing.

Read `references/prompt-nodes.md` for exactly which n8n node holds which prompt
and the escaping rules that apply inside an n8n JSON body. Read it before editing
any prompt — the escaping is the part that silently breaks things.

## The contract

Every summary is:

1. **One short intro sentence.** What the thing is, in plain language.
2. **Exactly three bullet points.** Not two, not five. Three is the promise the
   bot makes, and consistency is what makes the output feel designed rather than
   whatever the model felt like producing that run.
3. **In the reader's chosen language** — English or Arabic, chosen per request
   for one-off summaries and stored per subscriber for monitored channels.

Nothing else. No headers, no "Sure, here's a summary", no meta-commentary about
where the text came from.

## Never refuse, never ask

The model cannot browse. It only ever sees text that the workflow already
fetched. That means a refusal is always wrong — there is nothing to refuse.

Every prompt carries these two rules, and they exist because both failure modes
were observed in production:

```
- You already have everything you need. Never say you cannot view, access or
  retrieve anything, and never ask for a transcript or a description.
- Do not mention that this information was given to you.
```

**Do not describe a fetch failure to the model.** An earlier version passed
`"No transcript or description could be retrieved for this video"` as the
content, and the model dutifully apologised and asked the user for a transcript —
it was reading the failure notice as an instruction. If a fetch comes up empty,
pass the plain facts instead:

```
Video title: How To Squat Properly
Channel: AzzamFit
```

A fact invites a summary. A failure notice invites an apology.

## Three tiers of source material

`extract text` labels what it found in a `source` field. The tier changes how
confident the summary is allowed to sound:

| `source` | What the model got | How it should read |
|---|---|---|
| `transcript` | The real captions | Summarize directly and confidently |
| `description` | The uploader's description | Summarize directly |
| `title only` | Nothing but a title | Hedge — open with "Based on the title," |

The hedge matters. A three-bullet summary of a video nobody read is a guess, and
presenting a guess as fact is the kind of thing users notice and stop trusting.
Say where you stand.

When auditing output, check `source` first. Bullets that sound authoritative on a
`title only` run are a bug in the prompt, not a bad model day.

## Language

The language instruction is injected, not hardcoded, so one node serves both
languages:

```
- {{ <language expression> ? 'Write your entire answer in Arabic.'
                           : 'Write your entire answer in English.' }}
```

The expression differs by path — see `references/prompt-nodes.md`. Whatever
carries it, the rule stays identical in wording, because two differently-phrased
language instructions drift apart the moment one gets edited.

Arabic means Arabic throughout: intro, bullets, everything. A summary that
switches to English halfway has failed, even if the content is right.

## Telegram formatting

The bot sends with `parse_mode: HTML`, so:

- Only `&`, `<` and `>` need escaping, and the workflow does that with
  `.replace()` before the text goes out
- `<tg-spoiler>` hides monitored-channel summaries until tapped
- **No Markdown.** Asterisks and underscores are literal characters in HTML mode.
  Asking for `**bold**` produces visible asterisks

Never request Markdown from the model. This is why the reformat prompt says
"no markdown headers" — an early version used MarkdownV2 and unpaired
underscores in video titles broke sends outright.

## Checking a summary

Walk this list. Any failure means the prompt needs work, not a retry:

- [ ] One intro sentence, then exactly 3 bullets
- [ ] Entirely in the requested language
- [ ] No apology, no "I cannot", no request for more information
- [ ] No mention of being given text, or of a transcript existing
- [ ] Hedged if `source` was `title only`, confident otherwise
- [ ] No Markdown syntax
- [ ] Short enough to read on a phone without scrolling much

`scripts/check_summary.py` automates the mechanical half of this:

```bash
python scripts/check_summary.py summary.txt --lang ar --source title_only
```

It reports bullet count, detected language, refusal phrases, Markdown leakage and
missing hedge. Judgement calls — is the summary actually *good* — still need a
human. The script catches the failures that are objective, so review time goes to
the ones that aren't.

## Adding a new summarization path

If the bot grows a fourth Groq call, copy an existing prompt rather than writing
one fresh. Keep the rule block word-for-word identical and change only the opening
line that names the subject. Same reason as the language rule: prompts that start
as near-copies diverge under editing, and then two paths behave differently for
reasons nobody can reconstruct later.
