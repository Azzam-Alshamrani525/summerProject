# Week 4 — Day 3: The SKILL.md Structure

**Task:** Design the folder structure and write the first version of a SKILL.md file for a custom skill.

**Skill chosen:** `inbox-triage` — sorts a batch of emails into priority categories (Urgent / Needs Reply / FYI / Can Wait / Noise). Chosen as a new, work/email-related skill, separate from anything built earlier in the course.

---

## Folder structure

```
inbox-triage/
├── SKILL.md                          ← required: frontmatter + instructions
├── references/
│   └── category-rules.md             ← loaded only when a category boundary is unclear
└── examples/
    └── sample-triage-output.md       ← one worked example of the expected output shape
```

**Why this shape:** Claude Skills load in three stages — the `name`+`description` are always in context, the `SKILL.md` body loads once the skill triggers, and anything in `references/` or `examples/` loads only if the body points to it. So the SKILL.md itself stays short (rules that apply *every* time), and the harder edge-case judgment calls (Urgent vs. Needs Reply, FYI vs. Can Wait) live in `references/category-rules.md`, pulled in only when the top-level summary isn't enough to decide. This skill doesn't need a `scripts/` folder — there's no deterministic/repetitive code step, it's pure judgment-based sorting, so that directory was left out rather than added empty.

---

## Annotated SKILL.md

Below is what each part of the draft is doing and why — this is the part of the exercise that's easy to skip past, so it's worth spelling out.

**`description` (frontmatter):**
This is the *only* thing evaluated to decide whether the skill triggers at all — the body isn't read yet at that point. It's written a little "pushy" on purpose (naming several phrasings: "triage," "what needs my attention," "help me get through my inbox") because skills tend to *under*-trigger if the description is too narrow. It also states what the skill explicitly does **not** do (draft replies) right in the description, so a reply-drafting request doesn't accidentally route here.

**"When this applies":**
Handles the single-email edge case up front instead of leaving Claude to guess whether the skill still applies outside its main use case.

**"Categories":**
The core judgment call, defined once at the top level so it's always in context when the skill is active. Kept to 5 categories — enough to be useful, not so many that sorting becomes its own hard problem.

**"Output format":**
A fixed template, per skill-creator guidance ("define output formats explicitly"). Without this, output shape would drift between runs — sometimes a table, sometimes prose. Locking the format is what makes the output actually skimmable.

**"What this skill does NOT do":**
Explicit boundaries were added after noticing (from the docx/pptx skills studied on Day 1) that the strongest skills are explicit about scope. Without this section, it would be easy for a future run to "helpfully" draft a reply, which is a different job with different tone and risk considerations.

**"Edge cases":**
Written with an explanation of *why*, not just a rule — e.g. "default to Needs Reply over Urgent because false urgency is worse than a missed one." This follows the skill-writing guidance to explain reasoning instead of issuing bare ALWAYS/NEVER commands, so the skill generalizes to inboxes it hasn't seen rather than only matching the exact examples given.

---

## Next steps (Day 4)

This draft hasn't been run yet — Day 4 is implementation and verification: feed it real (sample) email batches, see where it gets a category judgment wrong or the output format drifts, and revise. Worth deciding before then whether to test with synthetic sample emails or real (anonymized) ones.
