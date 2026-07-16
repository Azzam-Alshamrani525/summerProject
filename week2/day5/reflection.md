# Week 2 — Reflection

## The project
A command-line password strength checker. It takes a password, checks it 
against 5 basic rules (length, uppercase, lowercase, number, special 
character), rates it Weak/Medium/Strong, and explains what's missing. 
It loops until you type "end", and also flags a short list of known 
common passwords.

## Where AI helped
- Gave me a working first draft fast, once I explained the spec in my 
  own words — I didn't have to start from a blank file.
- Explained *why* my 3 intentional bugs broke things, instead of just 
  silently fixing them. Seeing the actual reasoning (e.g., `continue` 
  vs `break`) made it click better than if it was just handed to me fixed.
- Pointed out real weaknesses in my own code during review (mixing 
  printing with logic, unexplained threshold numbers) that I wouldn't 
  have noticed on my own.

## Where I had to step in manually
- The actual behavior of the app was my call, not AI's — things like 
  how "end" should handle spacing/casing, and what to show on an empty 
  input. AI only built what I decided.
- I introduced and interpreted the 3 bugs myself, and reasoned out from 
  the test output *why* each one was wrong before asking for help fixing 
  it — the diagnosis started with me noticing something looked off.
- I add the rules of weak = less then 2 and meduim = 4 or less.

## Something I didn't fully agree with
AI's first version treated "passing all 5 rules" as good enough proof a 
password isn't common — but that's not really true (e.g., `Password1!` 
passes every rule and is still a well-known weak password). We both 
flagged this as a real limitation rather than a fix, so today I added a 
small hardcoded common-password list instead, which isn't perfect either, 
but is more honest than assuming rule-passing equals safety.

## Overall
AI was most useful as a fast first draft + a second pair of eyes for 
bugs and weak spots — but the actual decisions about what the app should 
do, and catching real issues in testing, still came down to me.