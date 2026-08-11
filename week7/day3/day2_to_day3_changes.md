# Day 2 → Day 3: What Changed

Day 2 ended with a working n8n bot. Day 3 turned it into a real application.
Details live in `workflow_map.md`, `summary-style/SKILL.md`, and the deployment guides.

---

## Interaction

**Native inline buttons.** Every button used to open a browser tab and send the user
back to Telegram to start over. Send-and-Wait can only produce URL buttons, so all of
them were replaced with `callback_data` buttons that stay inside the chat.

**Stateless flow.** Button taps are now separate executions. State travels inside the
button data and Telegram's reply chain instead of a database.

---

## Summaries

**It actually reads the content now.** The old prompt handed Groq a bare URL, which it
cannot open, so it refused. A fetch step was added: transcript first, description
second, title last.

**Arabic or English.** Asked once per summary, and stored per person for monitored
channels.

**Injection guard.** Scraped pages are treated as content to summarize, never as
instructions.

---

## Monitoring

**No more duplicates.** The last video ID is saved, so the same upload is never
announced twice.

**No approval step.** A new upload sends two messages — the link, then the summary
behind a spoiler. Nothing waits for a tap, so this half runs unattended.

**Cheaper.** One Groq call per language, shared by everyone following that channel.

---

## Multi-user

**Replies go to the sender.** Chat IDs are read from the incoming message instead of
being hardcoded.

**Per-person subscriptions.** The config file is keyed by channel, with a subscriber
list holding each person's chat ID and language. Older file shapes migrate on read.

---

## Around the app

**Permanent URL.** A free ngrok dev domain replaced the rotating one, so `WEBHOOK_URL`
never needs editing again.

**Custom Claude Skill.** `summary-style` defines the summary contract the workflow
implements, with a script that checks output against it.

**Deployment path.** Guides for moving to an always-on Oracle VM and for hardening it.

---

## Known limits

- Runs locally until the server move is done
- Groq calls bill to one key, and the bot is open to anyone
- Google Drive writes can collide if two people save at the same moment
