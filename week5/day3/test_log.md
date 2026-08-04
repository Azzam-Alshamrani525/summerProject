# Day 3 — Test Log

**Agent:** 2 tools (webpage reader + YouTube transcript reader) + memory

## Bug 1: YouTube links always failed

- **Cause:** video-ID regex matched the first `/` in the URL — which
  shows up in `https://` itself, before the real ID. Wrong 11 characters
  were extracted every time.
- **Fix:** regex now only matches `v=` or `youtu.be/`, never a bare `/`.
- Confirmed fixed via debug output (correct video ID extracted).

## Bug 2: long video transcript crashed the request

- **Cause:** Groq free tier caps a single request at 8000 tokens (input +
  output combined). A long transcript alone was ~19,000 tokens — an
  instant hard failure, not a rate-limit-wait situation.
- **Fix:** added `truncate_content()` — caps input around 18,000
  characters before sending. Adds a note to the summary when truncation
  happens.
- Confirmed fixed: same video now truncates and summarizes successfully.

## Confirmed working
- Memory: repeat link → instant cached result, no second API call.
- Second tool (YouTube) works end-to-end on a normal-length video.
- Correct routing between article vs. video tool.

## Accepted limitations (not fixed, noted for later)
- Some sites (NASA, NYT) block automated fetches — reported as a clean
  "couldn't retrieve" error. Real fix (telling paywall vs. blocked vs.
  dead link apart) is Day 5's job.
- Citation-heavy Wikipedia pages can hit the truncation limit from their
  footnotes alone, even when the real article is short. Didn't affect
  output quality this time (prose comes before citations), but worth
  revisiting later.
