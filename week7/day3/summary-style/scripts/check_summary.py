#!/usr/bin/env python3
"""Check a Summry_bot summary against the house style.

Usage:
    python check_summary.py summary.txt
    python check_summary.py summary.txt --lang ar --source title_only
    echo "..." | python check_summary.py - --lang en

Checks only what can be checked objectively: bullet count, language, refusals,
Markdown leakage, and the hedge required on title-only summaries. Whether the
summary is actually any good is a human call.

Exit code 0 = passed, 1 = at least one failure.
"""

import argparse
import re
import sys

BULLET = re.compile(r"^\s*(?:[-*•·]|\d+[.)])\s+\S", re.MULTILINE)

REFUSAL = [
    "i can't", "i cannot", "i can not", "i'm sorry", "i am sorry", "sorry, but",
    "unable to", "don't have access", "do not have access", "cannot access",
    "can't view", "cannot view", "can't retrieve", "cannot retrieve",
    "could you share", "could you provide", "please provide", "if you can share",
    "لا أستطيع", "لا يمكنني", "عذرا", "عذراً", "آسف", "لم أتمكن",
]

LEAKED = [
    "the text provided", "the text below", "based on the text",
    "the information provided", "the content provided", "as an ai",
    "no transcript", "transcript was not", "النص المقدم", "المعلومات المقدمة",
]

MARKDOWN = [
    (re.compile(r"\*\*[^*\n]+\*\*"), "bold (**…**)"),
    (re.compile(r"^#{1,6}\s", re.MULTILINE), "heading (#)"),
    (re.compile(r"__[^_\n]+__"), "underline (__…__)"),
    (re.compile(r"```"), "code fence (```)"),
]

HEDGE = ["based on the title", "بناءً على العنوان", "بناء على العنوان"]

ARABIC = re.compile(r"[\u0600-\u06FF]")


def arabic_ratio(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if ARABIC.match(c)) / len(letters)


def check(text, lang=None, source=None):
    results = []

    def add(ok, label, detail=""):
        results.append((ok, label, detail))

    body = text.strip()

    # --- structure
    bullets = BULLET.findall(body)
    add(len(bullets) == 3, "exactly 3 bullet points", f"found {len(bullets)}")

    first = body.split("\n", 1)[0].strip()
    add(bool(first) and not BULLET.match(first),
        "opens with an intro line, not a bullet",
        f"first line: {first[:60]!r}" if first else "empty")

    # --- refusals and leakage
    low = body.lower()
    hits = [p for p in REFUSAL if p in low]
    add(not hits, "no refusal or request for more info",
        "found: " + ", ".join(hits[:3]) if hits else "")

    leaks = [p for p in LEAKED if p in low]
    add(not leaks, "no meta-commentary about supplied text",
        "found: " + ", ".join(leaks[:3]) if leaks else "")

    # --- formatting
    md = [label for pat, label in MARKDOWN if pat.search(body)]
    add(not md, "no Markdown syntax (HTML parse mode)",
        "found: " + ", ".join(md) if md else "")

    # --- language
    ratio = arabic_ratio(body)
    if lang == "ar":
        add(ratio > 0.5, "written in Arabic", f"{ratio:.0%} Arabic letters")
    elif lang == "en":
        add(ratio < 0.15, "written in English", f"{ratio:.0%} Arabic letters")
    else:
        detected = "Arabic" if ratio > 0.5 else "English" if ratio < 0.15 else "mixed"
        add(detected != "mixed", "language is consistent", f"detected: {detected}")

    # --- hedge on weak sources
    if source in ("title_only", "title only"):
        add(any(h in low for h in HEDGE), "hedged for a title-only source",
            "expected an opening like 'Based on the title,'")
    elif source in ("transcript", "description"):
        hedged = any(h in low for h in HEDGE)
        add(not hedged, "not hedged (real content available)",
            "hedge present despite having real source material" if hedged else "")

    return results


def main():
    ap = argparse.ArgumentParser(description="Check a summary against the house style.")
    ap.add_argument("file", help="file containing the summary, or - for stdin")
    ap.add_argument("--lang", choices=["en", "ar"], help="language it should be in")
    ap.add_argument("--source", choices=["transcript", "description", "title_only"],
                    help="what extract text reported")
    args = ap.parse_args()

    text = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()

    results = check(text, args.lang, args.source)
    failed = 0

    print()
    for ok, label, detail in results:
        mark = "PASS" if ok else "FAIL"
        line = f"  [{mark}] {label}"
        if detail and not ok:
            line += f"  —  {detail}"
        elif detail and ok:
            line += f"  ({detail})"
        print(line)
        if not ok:
            failed += 1

    print()
    if failed:
        print(f"  {failed} of {len(results)} checks failed — the prompt needs work, "
              f"not a retry.")
    else:
        print(f"  All {len(results)} checks passed. Quality is still a human call.")
    print()

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
