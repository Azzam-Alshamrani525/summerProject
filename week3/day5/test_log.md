# Test Log: spec.md Reliability Check

**Goal:** verify that `spec.md`, used together with `system_prompt.md` as intended, is precise enough for an AI to build `booktracker.py` correctly.

## Method

An AI assistant was given `system_prompt.md` as its governing instructions and `spec.md` as its task. `system_prompt.md` explicitly states: *"If a requirement is ambiguous, ask before assuming."*

## Round 1 — Testing spec.md alone (incorrect method — noted as a mistake)

The first test run gave the AI only `spec.md`, without `system_prompt.md`. Without the "ask before assuming" rule in force, the AI silently guessed its way through 6 gaps in the spec instead of asking:

1. No unique book ID — guessed at using `title` as the lookup key, which breaks on duplicate titles
2. No stated rule on case-sensitivity for title-based lookups
3. No stated behavior for marking an already-finished book finished again
4. Filter/search with zero results reused a misleading generic message
5. No defined menu structure — the AI invented one
6. "Non-empty title/author" was stated in the spec but not actually enforced in the build

**Lesson learned:** testing `spec.md` in isolation was itself a mistake. It bypassed the governing rule in `system_prompt.md` and let the AI guess instead of ask — which is exactly the failure mode `system_prompt.md` exists to prevent.

## Round 2 — Correct method: spec.md + system_prompt.md together

Re-ran the test giving the AI both files together, as intended. This time, following the "ask before assuming" rule, the AI stopped and asked clarifying questions on the 3 highest-impact ambiguities (book identity/ID, re-finishing behavior, menu structure) before writing any code, and stated its assumptions openly for the 2 lower-stakes ones (search case-sensitivity, empty-result messaging) instead of silently deciding.

## Revisions Made to spec.md (based on answers received)

- Added a system-assigned unique `id` field; all lookups (mark finished, rate) now use `id`, not `title` text
- Defined exact behavior for re-finishing an already-finished book (no-op message, not an error)
- Defined distinct "no results" messages for filtered/search views vs. a genuinely empty library
- Added a new section (5a) locking in the exact menu structure and exit behavior
- Reworded the non-empty title/author rule to explicitly require reject-and-reprompt behavior

## Verification Build

`booktracker.py` was built from the revised `spec.md` and run through a full simulated session:

- Two books with the same title ("Dune") added and manipulated independently by `id` — no collision
- Marking an already-finished book returned the correct no-op message, not an error or crash
- Filtering by status returned only matching books
- Invalid menu input handled gracefully, no crash
- Rating validation correctly rejected an out-of-range value

**Result: all 6 gaps closed. No crashes. No silent guessing — every non-trivial ambiguity was resolved through a question, not an assumption.**

## Conclusion

`spec.md` is finalized. Just as importantly, this test confirmed that `system_prompt.md`'s "ask before assuming" rule is doing real work — it's the difference between an AI silently producing a flawed build and one that surfaces gaps for the human to decide on.
