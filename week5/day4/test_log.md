# Day 4 — Test Log

## Bug: synthesis step returned empty output
- **Cause:** `max_tokens=300` too low for a reasoning model - it used the
  budget on internal reasoning, leaving nothing for the visible answer.
- **Fix:** raised to 600 + added a fallback message for empty responses.

## Verified
- All 3 test video summaries matched their real content (checked via
  search) - accurate, not hallucinated.
- Tightened synthesis prompt to demand a specific connection, not a
  generic "same broad topic" answer.

## Bonus
- Added a simple Tkinter GUI (`gui.py`), same logic, no behavior changes.
  Full GUI polish deferred to Week 7.
