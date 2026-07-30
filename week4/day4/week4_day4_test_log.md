# Week 4 — Day 4: Build Your Own Skill — Test Log

**Task:** Implement your own Claude Skill and verify that it performs the intended task successfully.

**Skill under test:** `inbox-triage` (v1 draft from Day 3)

---

## Method

Two test batches, run against the skill as written:
- **Batch A** — 6 straightforward emails, one clean case per category. Checks basic mechanics work at all.
- **Batch B** — 10 emails deliberately built to hit the edge cases the skill's "Edge Cases" section already claims to handle: an unverifiable urgency claim, a multi-message thread, a high-status sender with no actual action needed, and a deadline that's real but not near-term.

---

## Pass 1 — Batch A (straightforward)

Result: **clean pass.** All 6 emails landed in the expected category with the expected reasoning. No changes needed. This confirms the core mechanism — reading the category definitions and output format — works before testing anything adversarial.

*(See `output-batch-A-v1.md` for the full result.)*

---

## Pass 1 — Batch B (edge cases) — 2 bugs found

*(See `output-batch-B-v1.md` for the full result.)*

### Bug 1 — Keyword urgency beat the ambiguous-context rule
Email from an unknown sender "R. Kim" saying "need this back ASAP, urgent!" with zero other context landed in **Urgent**. But the skill's own edge-case rule says ambiguous senders and missing context should default to **Needs Reply**. Two rules in the same document pointed different directions, and the keyword match won by accident of ordering — not because it was actually the intended precedence.

**Root cause:** Category 1's definition said "language signaling something is... time-critical" without qualifying that the *language* alone (a claim) isn't the same as *verified* urgency (a deadline, known sender, or concrete stakes).

### Bug 2 — "Needs Reply" used as a catch-all for "requires action"
The HR benefits-enrollment email (deadline: 3 weeks out) landed in **Needs Reply**, but nobody's waiting on a reply from the user — it's a reminder to complete a task, not a question. It got pulled into Needs Reply only because there was no better-fitting category available, revealing that Needs Reply's definition was too loose ("requires action" instead of "expects a response back from the user").

---

## Fix applied to SKILL.md

1. Reworded the **Urgent** category definition: urgency keywords ("ASAP," "urgent") no longer count on their own — they need a stated deadline, known-important sender, or concrete stakes alongside them.
2. Added an explicit **Edge Case** rule making this precedence unambiguous: unverified urgency claims are treated the same as the ambiguous-sender case (default to Needs Reply, flag what's unverifiable).
3. Reworded the **Needs Reply** category definition to require that the email specifically expects a *response back from the user* — not just any pending action — with tasks/deadlines-without-a-person-waiting routed to Can Wait (or Urgent, if the deadline is actually near-term).

---

## Pass 2 — Batch B, re-run against the fixed skill

*(See `output-batch-B-v2.md` for the full result.)*

- R. Kim's email moved from Urgent → **Needs Reply**, now with an explicit note that the urgency couldn't be verified. ✅
- HR's email moved from Needs Reply → **Can Wait**, now with a note that it has a real (but non-near-term) deadline. ✅
- Every other email in the batch stayed in its original, already-correct category — the fix didn't break anything that was working. ✅

---

## Known limitation accepted for v1

Real inboxes have a fourth bucket the current 5 categories don't cleanly cover: things with a **real but distant deadline** (HR's 3-week window). Right now those get folded into Can Wait, which slightly undersells that a deadline exists at all. Expanding to a 6th category was considered and deliberately **not done for v1** — it adds complexity for a case that's genuinely secondary to the skill's main job (surfacing what needs attention *now*). Flagging it here rather than solving it, same as the common-password-list simplification accepted in the Week 2 project.

---

## Outcome

`inbox-triage` performs its intended task successfully after one fix cycle. Both categories' definitions and the edge-case section are now internally consistent — no more silent rule conflicts. Skill is ready for Day 5 (test/chain against a second skill, peer review).
