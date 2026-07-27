# Week 4 — Day 2: Using Existing Skills

**Task:** Execute several existing Claude Skills using different inputs and compare their outputs and behavior.

**Skills executed:** `docx` (x2 inputs), `pptx` (x1 input)

---

## Run 1 — `docx`, simple input (memo)

**Input:** A short instruction — write a one-paragraph reminder memo about logging gym sessions.

**Behavior observed:**
- Skill went straight to the `docx`-js (npm) path since this was a create-new-document task, not an edit.
- No table/list/image gotchas were relevant, so the script was plain `Paragraph`/`TextRun`/`HeadingLevel` — the simplest branch of the skill's decision tree.
- Verification step (render to PDF → JPEG) was still run even though the content was simple — the skill doesn't skip verification just because the input is low-risk.

**Output:** `memo.docx` — clean single-page memo, heading + 3 body paragraphs.

---

## Run 2 — `docx`, complex input (table report)

**Input:** A weekly progress report containing a 4-column, 4-row data table.

**Behavior observed:**
- Same skill, same script pattern — but this run activated several of the documented gotchas that Run 1 never touched:
  - `columnWidths` had to be set on the table **and** matching `width` on every cell, both in DXA, summing exactly to the table width.
  - Header row shading required `ShadingType.CLEAR` — using `SOLID` would have rendered the header black (a gotcha with no visual warning until rendered).
- This is the clearest behavioral difference between the two docx runs: the *skill itself* didn't change, but a different portion of its gotcha list became relevant purely because the input had a table. A simpler input genuinely exercises less of the skill.

**Output:** `report.docx` — heading, intro paragraph, formatted table with shaded header row.

---

## Run 3 — `pptx`, short outline (3-slide deck)

**Input:** A 3-slide outline — title slide, bullet list slide, chart slide — on a beginner gym routine.

**Behavior observed vs. the `docx` runs:**
- **Different creation library** (`pptxgenjs` instead of `docx`-js) and a different unit system (inches/EMU vs. DXA) — confirms the two skills are genuinely separate toolchains, not variations of one.
- **Layout had to be set explicitly before adding slides** (`LAYOUT_WIDE`) — pptx has no equivalent of "just start writing paragraphs"; canvas dimensions are a required first decision.
- **Native chart handling**: the chart slide used `addChart()` with explicit `showTitle`, `showValue`, `dataLabelPosition`, and grid-line styling — pptx's skill instructions are emphatic about not defaulting to a bare chart or falling back to a static image.
- **Verification step differs from docx**: pptx has its own `validate.py` (schema/relationship/chart-axis checks) *in addition to* the thumbnail-grid visual check — a stricter two-stage verification than docx's single render-and-look step. This reflects that pptx has more silent-corruption failure modes (bad hex colors, negative shadow offsets, undeclared chart axes) than docx does.

**Output:** `deck.pptx` — 3 slides, validated clean, thumbnail grid confirmed visually correct.

---

## Comparison summary

| | `docx` (memo) | `docx` (report) | `pptx` (deck) |
|---|---|---|---|
| Library | docx-js | docx-js | pptxgenjs |
| Unit system | DXA (twips) | DXA (twips) | inches/EMU |
| Gotchas triggered | none | table widths, shading type | layout size, chart config |
| Verification | render → image | render → image | validate.py **+** thumbnail grid |
| Failure mode if skipped | unlikely to break | table renders misaligned/black | file can be silently corrupted |

**Key takeaway:** The two `docx` runs show that *within* a single skill, behavior scales with input complexity — the skill has a long gotcha list but only pulls the relevant subset per task. The `pptx` run shows that *across* skills, even for visually similar "create an Office document" tasks, the underlying toolchain, unit system, and verification rigor are completely different — pptx's extra validation step exists because its failure modes are more severe (a corrupted, unopenable file) than docx's (a misaligned but still-openable one).

---

*Outcome: ran existing skills successfully; observed that skill behavior is driven by which part of the skill's instructions the input actually exercises, and that superficially similar skills (docx vs pptx) can have meaningfully different internal verification requirements.*
