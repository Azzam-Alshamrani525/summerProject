# Week 4 — Day 5: Test & Chain Skills

**Task:** Chain two skills together to complete a multi-step workflow. Test and improve reliability through peer review.

**Skills chained:** `inbox-triage` → `docx`

**Workflow:** Paste a batch of emails → `inbox-triage` sorts them into all 5 categories → the full sorted result gets turned into an "Inbox Triage Summary" Word doc — same content as the triage output, just formatted as a document instead of chat text.

---

## Why this chain

`inbox-triage` produces a sorted list, but a list in chat isn't something you'd forward to yourself or print. Feeding its output into `docx` turns "what needs my attention" into an actual shareable document — the two skills solve different halves of the same real task.

---

## Step 1: run `inbox-triage`

Two batches tested:
- **Batch C** — a normal mixed inbox (1 Urgent, 2 Needs Reply, 2 FYI, 1 Noise)
- **Batch D** — deliberately built with **zero Urgent** emails, to stress-test what the next step does when a category comes back empty

*(See `triage-output-C.md` / `triage-output-D.md`.)*

## Step 2: build the summary doc (v1 — before fix)

First version of the chaining script printed a heading for every one of the 5 categories, then listed whatever items existed under each.

**Bug found (peer-review pass):** running it on Batch D — the zero-Urgent case — produced a doc with an "Urgent" heading and nothing underneath it. Technically not wrong, but it reads like something broke or got missed, which defeats the point of a summary doc (it should build confidence about what's covered, not create doubt).

## Fix applied

The build script now only prints a category heading if that category actually has items in it. Empty categories are skipped entirely instead of showing up as a bare heading with nothing under it.

## Step 2: re-run (v2 — after fix)

- Batch C's doc — all categories present, all correct.
- Batch D's doc — the empty "Urgent" category is skipped entirely; the other 4 populated categories show cleanly with no dangling heading.

*(See `inbox-summary-C.docx` / `inbox-summary-D.docx` — the two final deliverable files.)*

---

## Reliability lesson

The bug wasn't in either skill individually — `inbox-triage`'s output was correct, and `docx`'s formatting was correct. It only showed up at the **seam between them**, where the second step assumed the first step's output would always be non-empty. This is the general risk with chaining: each skill can pass its own test in isolation and the chain can still break, because the failure mode only exists in how one skill's output gets *consumed* by the next one. Worth testing the connection point deliberately, not just each skill on its own — which is why Batch D was built specifically to be empty in one category, rather than just running another normal-looking batch.

---

## Outcome

Working two-step chain: `inbox-triage` → `docx`, verified against both a normal case and an edge case, with the edge-case failure caught and fixed before calling it done. Final deliverables: `inbox-summary-C.docx` and `inbox-summary-D.docx`.

This closes out Week 4. Up next: **Week 5, Day 1 — design an AI agent for a real-world scenario** (objective, tools, inputs/outputs, decision process), which is a different kind of task from anything in Week 4 — this is design/planning, not skill-writing.
