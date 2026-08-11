# Where the prompts live

Three nodes in `summry_bot_workflow_v9.json` hold user-facing prompt text. All
three are HTTP Request nodes posting to `https://api.groq.com/openai/v1/chat/completions`
with `openai/gpt-oss-20b`.

| Node | Path | Job | Language comes from |
|---|---|---|---|
| `Groq call (Path A)` | On-demand summarize | Summarizes a page or video the user sent | The button they tapped |
| `HTTP Request` | Monitor (hourly) | Summarizes a new upload | The subscriber group being served |
| `HTTP Request1` | Monitor (hourly) | Reformats the above for Telegram | Inherited — told to keep the same language |

`HTTP Request1` never sees the source material, only the summary from
`HTTP Request`. That is why it is told to preserve the language rather than being
given a language instruction of its own — it has no way to know what was asked for.

## The language expressions

They differ because the two paths learn the language differently.

**Path A** — read from the button that was tapped. `S_AR` and `ML_AR` both contain
`_AR`, so one check covers both:

```
{{ $('Telegram Trigger').first().json.callback_query.data.includes('_AR')
   ? 'Write your entire answer in Arabic.'
   : 'Write your entire answer in English.' }}
```

**Monitor path** — read from the language group being processed. `split by language`
emits one item per distinct language among a channel's subscribers:

```
{{ $json.lang === 'ar' ? 'Write your entire answer in Arabic.'
                       : 'Write your entire answer in English.' }}
```

## Escaping — read this before editing any prompt

The prompt lives inside a JSON string, inside an n8n expression, inside a JSON
body. Three layers, and each one bites differently.

**Line breaks are `\n`, not real newlines.** A literal newline inside the JSON
string makes the body invalid and the node fails with a parse error before the
request is ever sent.

**Any interpolated text must be JSON-escaped:**

```
{{ JSON.stringify($json.content).slice(1, -1) }}
```

`JSON.stringify` escapes quotes, backslashes and newlines; `.slice(1, -1)` strips
the wrapping quotes it adds, since the surrounding JSON already supplies them.
Dropping this is the single most likely way to break a prompt — page text contains
quotes and newlines constantly, and one unescaped quote ends the JSON string early.

**Single quotes inside the expression, double quotes outside.** The JSON string is
delimited by `"`, so any string literal inside an expression uses `'`.

## Verifying an edit before importing

Strip the expressions and check the body is still valid JSON:

```python
import json, re
body = open('prompt.txt').read().lstrip('=')
json.loads(re.sub(r'\{\{.*?\}\}', 'PLACEHOLDER', body))
```

No exception means the body parses. This catches unescaped quotes and stray real
newlines in a second, instead of after an import and a failed run.

## Related

The prompts assume the fetch chain has already run. That chain is
`normalize link → fetch page → extract text` (Path A) and
`normalize link (video) → fetch page (video) → extract text (video)` (monitor).
`extract text` is what produces the `content` and `source` fields the prompts
depend on, so a prompt problem and a fetch problem look identical from Telegram.
Check `source` in the execution log before touching the prompt.
