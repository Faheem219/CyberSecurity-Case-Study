# CLAUDE.md — HCI CA-3 (Raktdaan blood donation app): handoff

## Task
HCI CA-3, **Group 06**, faculty **Dr. Sudhanshu Gonge**. Members (CSE-C): Raghav Sonchhatra – PRN 23070122172;
Sanidhya Awasthi – PRN 23070122192; Faheemuddin Sayyed – PRN 23070122196.
Faculty notice (7 Oct 2026): upload **PPT Presentation, Figma Design, HTML & CSS code** to the class Drive folder
(one folder per group) by **13 Oct 2026**, files properly named.

Topic: **Raktdaan** — blood donation & blood bank mobile app (Figma design system + 15 screens + plain HTML/CSS prototype).

## Files
| File | What |
|---|---|
| `raktdaan.html` | The group's HTML & CSS prototype (15 screens, no JS). Source of truth for screens and design tokens. |
| `Blood Donation App – *.png`, `Icons — Phosphor *.png` | Figma exports (UI screens, design system, icons). |
| `G06_HCI_CA3_Presentation.html` | Deck (18 slides, self-contained, 2 MB). Same controls/layout as the Cyber Security deck (`../build_presentation.py`). |
| `G06_HCI_CA3_Presentation.pdf` / `.pptx` | Exports for Drive. PPTX = one image per slide (not editable text). |
| `capture_screens.py` | Headless Chrome → `presentation_assets/screens/*.webp` (2x phone captures) + Figma crops. Re-run only if `raktdaan.html` changes. |
| `build_presentation.py` | Writes the deck. Tokens, contrast ratios, line/input/aria-label counts are read from `raktdaan.html`. |
| `export_presentation.py` | PDF (Chrome print, vector) + PPTX (needs `pip install python-pptx`). `--png` → slide PNGs for checking. |
| `presentation_assets/fonts/` | Figtree + Fraunces latin woff2 (OFL), embedded in the deck. |

Rebuild: `python capture_screens.py` (if HTML changed) → `python build_presentation.py` → `python export_presentation.py`.
Python on this machine is `python` (3.13, Windows); Chrome at `C:\Program Files\Google\Chrome\Application\chrome.exe`.

## Decisions
- Slide 1 follows the group template (rounded frame, SIT logo, course line, topic, group, names, footer) **plus "Guided by"**.
- Deck uses Raktdaan's palette and fonts (Fraunces headings, Figtree body) instead of the Cyber Security deck's blue.
- Personas are labelled **proto-personas** (assumption-based); no user study was done — do not invent study results.
- Accessibility slide: user asked (2026-10-10) for no "Fix" / "next iteration" wording, so the contrast table shows only
  pairs that really pass AA (build asserts ≥ 4.5:1 — never label a failing pair "Pass"). Not shown: sage tag 4.2:1,
  turmeric tag 3.2:1, tertiary text 3.1:1 are below AA in `raktdaan.html`; darkening those 3 tokens would make all pass.

## Status (2026-10-10)
Deck, PDF, PPTX built and visually checked. Remaining for the group: upload PPT + Figma link/file + `raktdaan.html` to the Drive folder.
