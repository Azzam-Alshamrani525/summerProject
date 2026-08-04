# Day 2 — Test Log

**Test article:** essays.quotidiana.org/stevenson/apology_for_idlers/ (~2,500 words)

## Bug: response cut off, no Conclusion line

- **Cause:** `max_tokens=400` was too small — the model got cut off before
  reaching the required Conclusion sentence. Not a prompt problem, a
  length-limit problem.
- **Fix:** raised to 600 (later 1000, once Day 3 needed room for longer
  content).
- **Takeaway:** `max_tokens` only limits the *output*, never the input.
  Setting it generously costs nothing — it's a ceiling, not a target.

Result: full 4-bullet + conclusion output confirmed working.
