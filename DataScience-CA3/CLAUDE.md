# CLAUDE.md — Data Science CA-3 (Tableau case study): handoff file

> Separate task from the Cyber Security case study in the repo root. A future session with no chat history must be
> able to finish from this file. Last updated: 2026-10-10.

## Task (user: Faheemuddin Sayyed)
CA-3 for Data Science, based on Unit 5 (*Mining social-network graphs*) and Unit 6 (*Data ethics, privacy*).
Deadline: final submission and presentation between 5 and 12 Oct 2026. Requirements:
- Choose a real public dataset and write a problem statement and objectives.
- Build an interactive Tableau dashboard that applies visualisation principles.
- Compare Tableau Creator and Viewer licences.
- Discuss privacy, security and ethics.
- Deliver a short HTML deck in the same format as `../G04_Presentation.html`.
- Give answers for the Google Form: title, 8–10 objectives, and the techniques behind each.

## Fixed decisions (do NOT re-ask)
| Item | Value |
|---|---|
| Members | **Faheemuddin Sayyed – PRN 23070122196**, **Sanidhya Awasthi – PRN 23070122192** (only these two) |
| Faculty | **"Guided by: Dr. Deepak Dharrao"** on slide 1 |
| Group number | **Leave it out** |
| Dataset | **Enron email network**: igraphdata `enron` (JHU / Priebe et al. 2005), `data/raw/enron.rda` from raw.githubusercontent.com/igraph/igraphdata |
| Tableau route | Claude **generates a `.twbx`**; the user opens it in Tableau (they have **Desktop 2026.2.3**), publishes, and sends screenshots |
| Title | *Enron Email Network Analytics: An Interactive Tableau Dashboard of Communication Patterns, Communities and Privacy Risks during a Corporate Collapse (1999–2002)* |

**Environment facts.**
- The cloud environment's network policy blocks tableau.com, Kaggle, SNAP and CMU.
- GitHub raw, PyPI and npm work.
- Tableau Public has no publishing API, so Claude cannot publish or render Tableau views.

## Pipeline and outputs (all done, all reproducible)
`python3 analysis/prepare_data.py && python3 analysis/make_figures.py && python3 tableau/build_workbook.py && python3 build_presentation.py`

**`prepare_data.py`.**
- Cleaning: 125,409 raw → window → drop BCC (duplicates of CC) → merge aliases (184 addresses → 149 people) → drop self-mail → drop folder duplicates → **34,374 deliveries / 20,074 messages**.
- Privacy: only the 10 officers (CEO/President/COO/CFO) keep real names; everyone else becomes a pseudonym (`VP-03`); roles become numbered groups ("1 Executive" … "7 Unknown role").
- Metrics: betweenness, PageRank, clustering, strong/weak ties, Unit-5 locality test, Girvan–Newman on strong ties (best modularity) with leftovers attached by majority weight, a Louvain cross-check, community-weighted spring layout, period metrics and monthly snapshots.

**Key numbers (`results/summary.json`).**
- Graph: 148 nodes, 1,788 ties (816 strong / 972 weak), reciprocity 0.63.
- Locality test: p_closed 0.42 vs density 0.16.
- Communities: GN Q = 0.52 with 7 communities; Louvain NMI 0.62.
- Deliveries per week: pre-crisis 163, crisis 541, post-bankruptcy 129.
- Executive share of traffic: 17% → 22% → 24%. Broadcast share: 3.3% → 5.6% → 4.9%.

**Data-quality finding.** Recorded timestamps drift by ~5 h between Apr and Sep 2001 (`clock_check.csv`). The
apparent "after-hours doubled" result was this artefact, so **hour-of-day analysis was removed on purpose**. Do not
re-add it.

**`tableau/build_workbook.py`** (rewritten 2026-10-10).
- **Attempt 1 failed in real Tableau.** The 26.1 format with `<ManifestByVersion/>` passed the official XSD, but
  Tableau Desktop 2026.2.3 refused it with error D2E8DA72. Its loader demanded `layout@dim-percentage`,
  `worksheet@number` plus a `<worksheet-number>` child, and `mark@type`, and it also reported errors inside its own
  internal schema (Sort-G, ShelfSorts-G). **Do not go back to the 26.1 / ManifestByVersion dialect.**
- **Now: classic `version='18.1'`, `source-build='2021.3.3 (20213.21.1018.0949)'`.**
  - Manifest: ObjectModelEncapsulateLegacy, ObjectModelTableType, SchemaViewerObjectModel (`_.fcp.*.true...` forms), SheetIdentifierTracking, WindowsPersistSimpleIdentifiers.
  - Data sources: `_.fcp.ObjectModelEncapsulateLegacy.false/true...relation` pair, a fcp `object-id`, a fcp `object-graph`, and a layout with `_.fcp.SchemaViewerObjectModel.false...dim-percentage`.
  - Dashboard zones use `type=` (not `type-v2`); no explain-data, no sizing-mode.
  - All of this is mirrored from genuine Tableau-saved files (tsc `WorkbookWithoutExtract.twb` 2021.3; dapi `filtering.twb` 2021.1, `shapes_test.twb` 2021.2; `RESTAPISample.twb` 10.0).
- **Version-sensitive constructs avoided.**
  - No `filter-group`: dashboard filtering uses 5 parameters (Rank by, Period, Sender role, Ties shown, Community) plus a "Keep/Drop" calculated field filtered to "Keep" on each sheet.
  - No sort element: the Top-15 rows use a "Rank" label calc (`01. Name`).
- **Checks.** A dialect lint against the genuine samples left only standard constructs unflagged-by-sample (textscan `columns`, list-parameter `members`, `path` encoding, text zones, axis `fold`). The semantic cross-reference check finds 0 problems.
- **Status:** awaiting the user's second test in Tableau.

**`build_presentation.py`.** Builds a 16-slide deck. If `screenshots/overview.png` and `screenshots/network.png`
exist they are embedded; otherwise slides 8 and 9 show HTML wireframes. All slides were screenshot-checked with
Playwright Chromium.

## Status / TODO
- [x] Data, analysis, figures, workbook, deck, Google Form answers, README, viva notes
- [ ] **USER:** re-test the rebuilt `.twbx` (18.1 dialect) in Tableau Desktop 2026.2.3. If it fails, ask for the exact error list (Tableau prints line:column) and map each one onto `Enron_Email_Network.twb`. The fallback manual-build table is in the README.
- [ ] **USER:** publish to Tableau Public with downloads off. Save the screenshots to `screenshots/`, then re-run `build_presentation.py` (or Claude does it).
- [ ] **USER:** rehearse. Suggested split: Faheemuddin slides 1–8, Sanidhya slides 9–16.
