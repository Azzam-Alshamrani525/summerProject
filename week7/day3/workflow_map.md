# Summry_bot — Workflow Map (v9)

How every path through the bot runs, from what the user does to what comes back.

**Legend**

```
──▶   flow continues            [button]   inline button, stays in Telegram
◀──   returns to a node         «force»    Force Reply prompt
✉     message sent to user      ⟳          back to the menu
⚠     error branch              💾         Google Drive write
```

Two things start a run, and they never mix:

```
Telegram Trigger  ──▶  something the user did          (message or button tap)
Schedule Trigger  ──▶  hourly channel check            (nobody involved)
```

---

## 1. The router

Every user action lands here first.

```
Telegram Trigger
      │
      ▼
 route update
      │
      ├─[callback]─▶ answer callback ──▶ route callback ──▶ see §3
      │              (stops the button spinner)
      │
      ├─[start]────▶ ✉ welcome + menu ──▶ [📝 Summarize] [📺 Monitor]
      │
      ├─[stop]─────▶ see §6  (/stop typed as a command)
      │
      ├─[link]─────▶ has reply context? ──▶ see §2
      │
      └─[other]────▶ ✉ help message
                      "Send /start, or just send me a link"
```

---

## 2. User sends a link

The bot has to work out *why* you sent it.

```
has reply context?          ← did you REPLY to one of the bot's questions?
      │
      ├─[yes]──▶ which prompt?
      │              │
      │              ├─[said "summarize"]──▶ ✉ 🌐 Which language?  [🇬🇧 EN] [🇸🇦 AR]
      │              │                          └──▶ §4
      │              │
      │              └─[said "channel"]────▶ §5  (YouTube check)
      │
      └─[no]───▶ ✉ "What should I do with this link?"
                    │        (sent as a reply to YOUR message)
                    ├─[📝 Summarize it]──▶ ✉ 🌐 Which language? ──▶ §4
                    └─[📺 Monitor this channel]──▶ §5
```

---

## 3. Every button, and where it goes

```
route callback
   │
   ├─ A_SUM  ──▶ «force» ✉ "Send me a link to summarize"
   │                        └─ you reply ──▶ §2 ──▶ §4
   │
   ├─ B_MENU ──▶ ✉ monitor menu
   │                ├─[📺 Monitor a new channel]──▶ B_NEW
   │                └─[🛑 Stop monitoring]───────▶ B_STOP ──▶ §6
   │
   ├─ B_NEW  ──▶ «force» ✉ "Send me the channel or video link"
   │                        └─ you reply ──▶ §5
   │
   ├─ B_STOP ──▶ §6
   │
   ├─ M_YES  ──▶ ✉ 🌐 Which language?  [🇬🇧 EN] [🇸🇦 AR]   ──▶ ML_EN / ML_AR
   ├─ M_NO   ──▶ ✉ "Okay, not monitoring" ──▶ ⟳
   │
   ├─ L_SUM  ──▶ ✉ 🌐 Which language? ──▶ S_EN / S_AR
   ├─ L_MON  ──▶ §5
   │
   ├─ S_EN / S_AR   ──▶ §4   (summarize now, in that language)
   ├─ ML_EN / ML_AR ──▶ §5b  (save the channel with that language)
   │
   └─ anything else ──▶ ✉ help message
```

---

## 4. Summarize a link

```
S_EN / S_AR
   │
   ▼
prep summarize input          ← link recovered from reply_to_message
   │
   ▼
normalize link                ← youtu.be, Shorts, ?si= all become watch?v=
   │   ├─⚠──▶ ✉ "couldn't open that link" ──▶ ⟳
   ▼
fetch page  (HTTP Request)
   │   ├─⚠──▶ ✉ "couldn't open that link" ──▶ ⟳
   ▼
extract text                  ← transcript > description > title only
   │
   ▼
Groq call (Path A)            ← prompt carries the chosen language
   │   ├─⚠──▶ ✉ error alert ──▶ ⟳
   ▼
✉ summary   ──▶ ⟳ "Anything else?"
```

---

## 5. Add a channel to monitor

```
link arrives (from B_NEW reply, or the [📺 Monitor this channel] button)
   │
   ▼
if youtube link
   ├─[no]──▶ ✉ "That's not a YouTube link" ──▶ «force» ask again
   │
   └─[yes]─▶ if youtube vid
                ├─[video]──▶ oEmbed ──▶ fetch channel page
                └─[channel]─────────────▶ fetch channel page
                                              │
                                              ▼
                                       extract channle ID
                                              │
                                              ▼
                             ✉ "Start monitoring <name>?"
                                   ├─[❌ No]──▶ ✉ "Okay" ──▶ ⟳
                                   └─[✅ Yes]──▶ M_YES ──▶ 🌐 language ──▶ §5b
```

### 5b. Saving it

```
ML_EN / ML_AR
   │
   ▼
fetch channel page (confirm)  ← channel ID travels inside the button
   ▼
extract channle ID (confirm)
   ▼
💾 Download config (save)
   ▼
merge my channel              ← adds { chatId, lang } to that channel's subscribers
   ▼                             and removes you from any channel you followed before
Convert to File ──▶ 💾 Update file
   ▼
✉ "✅ Now monitoring <name> — 🌐 <language>" ──▶ ⟳
```

---

## 6. Stop monitoring

Reached two ways — typing `/stop`, or the 🛑 button. Both run the same chain.

```
/stop  ─┐
        ├─▶ 💾 Download config (stop)
[🛑]  ──┘         ▼
             remove my channel     ← only YOUR entry is removed
                  ▼                  channel is deleted only if nobody is left
             Convert to File (stop) ──▶ 💾 Update file (stop)
                  ▼
             ✉ "🛑 Monitoring stopped" ──▶ ⟳
```

---

## 7. The hourly check (nobody involved)

```
Schedule Trigger
   ▼
💾 Download file ──▶ Code in JavaScript      ← one item per CHANNEL
   ▼
Loop Over Items ◀───────────────────────────────────────────┐
   │  (one channel at a time)                               │
   ▼                                                        │
RSS Read ──▶ Limit ──▶ Edit Fields                          │
   ▼                                                        │
is it new?    videoId  vs  saved lastVideoId                │
   ├─[same]──────────────────────────────────────────────▶──┤ stay quiet
   │                                                        │
   └─[different]                                            │
        ▼                                                   │
   💾 Download config (loop) ──▶ merge last video           │
        ▼                                                   │
   Convert to File (loop) ──▶ 💾 Update file (loop)         │
        ▼        ↑                                          │
        │        └── saved BEFORE Groq, so a failure        │
        │            can never repeat the notification      │
        ▼                                                   │
   prep video input ──▶ normalize link (video)              │
        ▼                    ├─⚠──▶ ✉ alert to owner ────▶──┤
   fetch page (video)        │                              │
        ▼                    └─⚠──▶ ✉ alert to owner ────▶──┤
   extract text (video)                                     │
        ▼                                                   │
   split by language     ← 1 item per LANGUAGE, not person  │
        ▼                                                   │
   Groq #1 ──⚠──▶ ✉ alert to owner ───────────────────────▶─┤
        ▼                                                   │
   Groq #2 ──⚠──▶ ✉ alert to owner ───────────────────────▶─┤
        ▼                                                   │
   fan out subscribers   ← 1 item per PERSON                │
        ▼                                                   │
   ✉ message 1: channel + title + link  (preview card)      │
        ▼                                                   │
   restore items                                            │
        ▼                                                   │
   ✉ message 2: summary hidden in a spoiler ──────────────▶─┘
                                                    next channel
```

**Why the loop:** without it, `Limit` would take one video across *all* feeds combined and every channel after the first would be skipped.

**Why split by language:** a channel with 5 English followers costs **one** Groq call, not five. English + Arabic followers costs two, and everyone gets their own language.

---

## 8. Button reference

| Button data | Meaning |
|---|---|
| `A_SUM` | Summarize something → ask for a link |
| `B_MENU` | Monitor a channel → sub-menu |
| `B_NEW` | Monitor a new channel → ask for a link |
| `B_STOP` | Stop monitoring |
| `M_YES:<channelId>` | Yes, monitor this channel |
| `M_NO` | No, don't monitor it |
| `L_SUM` / `L_MON` | What to do with a bare link |
| `S_EN` / `S_AR` | Summarize now, in this language |
| `ML_EN:<channelId>` / `ML_AR:<channelId>` | Monitor this channel, in this language |

Telegram caps this at 64 bytes. Longest in use is ~30.

---

## 9. Config file

`channel_config.json` on Google Drive:

```json
{ "channels": {
    "UCxxxxxxxxxxxxxxxxxxxxxx": {
      "channelName": "Some Channel",
      "rssUrl": "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxx…",
      "lastVideoId": "hGI3BGhrYYk",
      "subscribers": [
        { "chatId": "1087117148", "lang": "en" },
        { "chatId": "555999",     "lang": "ar" }
      ]
    }
}}
```

Every node that reads this file upgrades older shapes automatically — the original
single-user file, the per-user map, and plain-string subscribers all still load.

---

## 10. How state survives without a database

Each button tap is a **separate execution** with no memory of the last one. Nothing
is stored to bridge them. Three tricks do the work instead:

| What has to survive | How |
|---|---|
| Which button was pressed | The `callback_data` string itself |
| Which channel it referred to | Packed into `callback_data` after the `:` |
| The link you typed | Recovered from `reply_to_message` on the bot's question |

The only thing written to disk is what must outlive the conversation entirely:
who follows which channel, in which language, and the last video they were told about.
