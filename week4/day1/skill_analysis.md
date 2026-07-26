# Week 4 — Day 1: What is a Skill

**Task:** Analyze three existing Claude Skills and explain when each should be triggered and what problem it solves.

**Skills analyzed:** `docx`, `pptx`, `skill-creator`

---

## 1. `docx` — Word document creation/editing

**Problem it solves:**
A `.docx` file is a ZIP archive of XML, not plain text. Without this skill, an AI would either refuse to touch Word files or hand-roll fragile XML edits. The skill packages known gotchas (page size defaults to A4, tables need dual width settings, bullets need a numbering config instead of a literal `•` character, etc.) plus scripts to verify output by rendering it to images.

**When it triggers:**
Any mention of "Word doc," `.docx`/`.dotx`, or a request for a report/memo/letter/template as a Word file — including edits, extraction, or reformatting. Explicitly scoped *out* of PDFs, spreadsheets, or unrelated coding.

**Trigger mechanism:**
Keyword/intent matching on file type and common synonyms for the deliverable ("report," "memo").

---

## 2. `pptx` — PowerPoint deck creation/editing

**Problem it solves:**
Same ZIP-of-XML problem as `docx`, but with a much longer list of corruption traps (bad hex color formats, negative shadow offsets, missing chart axis declarations) that would silently produce a file PowerPoint refuses to open. The skill exists because these failure modes aren't obvious from general programming knowledge — they're specific to how `pptxgenjs` and the OOXML format interact.

**When it triggers:**
Whenever a `.pptx`/`.potx` file is involved *at all* — input or output — including reading slide content for reuse elsewhere, not just creating decks.

**Trigger mechanism:**
Broader than `docx`'s — it explicitly covers use "regardless of what they plan to do with the content afterward," so even indirect uses (extract slide text to summarize in an email) route through it.

---

## 3. `skill-creator` — meta-skill for building skills

**Problem it solves:**
A completely different problem from the two above — not a file format, but a *process*: capturing a workflow, drafting a SKILL.md, writing test cases, running evals, and iterating based on results. It solves the "how do I package expertise into something reliably triggerable" problem.

**When it triggers:**
When the user wants to create, edit, or benchmark a skill — including vague requests like "turn this into a skill," where it's expected to extract structure from the preceding conversation rather than starting from a blank slate.

**Trigger mechanism:**
Intent-based rather than filetype-based — it watches for a *goal* (build/improve a skill) rather than a document type appearing.

---

## Pattern across all three

Every skill's trigger logic lives entirely in its `description` field — that's the only thing evaluated to decide relevance before the skill's body is even loaded. The strongest skills are explicit about what's *in scope* and *out of scope* (`docx` explicitly excludes PDFs/spreadsheets) so skills don't collide or over-fire on adjacent tasks. `skill-creator` also shows that a skill's "problem" doesn't have to be a file format — it can be a repeatable process.
