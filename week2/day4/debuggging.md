# Day 4 — Debugging Log (Streamlit Password Checker)

## Bug 1
**Symptom:** Entering "sds" (no uppercase at all) didn't get flagged as missing an uppercase letter.
**Diagnosis:** `has_upper` was written as `any(c.islower() for c in password)` — checking for lowercase instead of uppercase.
**Fix:** Changed to `any(c.isupper() for c in password)`.

## Bug 2
**Symptom:** As soon as the app loaded (before typing anything), it showed a strength rating and reasons. Once a real password was typed in, it said "No password entered" instead.
**Diagnosis:** The condition was written as `if not password:` — meaning it evaluated the password when the box was empty, and skipped evaluation once real text was entered. The logic was backwards.
**Fix:** Changed to `if password:`.

## Bug 3
**Symptom:** Typing "Tr0ub4dor&3" (11 characters) was flagged as "too short."
**Diagnosis:** `length_ok` used `len(password) <= 8` instead of `>= 8`, so it rewarded short passwords and penalized long ones.
**Fix:** Changed to `len(password) >= 8`.

## What I learned
Moving from a CLI loop to a GUI meant one of my old bugs (the "end"/break-continue one) no longer applied — there's no exit command in a GUI. Instead, a new kind of bug showed up that's specific to GUIs: getting an if/else condition backwards, which flips *when* the logic runs instead of breaking the logic itself.