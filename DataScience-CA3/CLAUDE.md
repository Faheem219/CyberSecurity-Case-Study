# CLAUDE.md — Data Science CA-3 (Tableau case study): handoff file

> Separate task from the Cyber Security case study in the repo root. A future session with no chat history must be
> able to finish from this file. Last updated: 2026-10-09.

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
| Tableau route | Claude **generates a `.twbx`**; the user opens it in Tableau Public/Desktop **2026.1+**, publishes, and sends screenshots |
| Title | *Enron Email Network Analytics: An Interactive Tableau Dashboard of Communication Patterns, Communities and Privacy Risks during a Corporate Collapse (1999–2002)* |

**Environment facts.**
- The cloud environment's network policy blocks tableau.com, Kaggle, SNAP and CMU.
- GitHub raw, PyPI and npm work.
- Tableau Public has no publishing API, so Claude cannot publish or render Tableau views.

## Pipeline and outputs (all done, all reproducible)
`python3 analysis/prepare_data.py && python3 analysis/make_figures.py && python3 tableau/build_workbook.py --xsd <xsd> && python3 build_presentation.py`

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

**`tableau/build_workbook.py`.**
- Writes the TWB in the **26.1 format** (`<ManifestByVersion/>`): 5 CSV (textscan) data sources plus a Parameters data source, 11 worksheets and 2 dashboards ("1 Overview", "2 Network").
- Includes 2 highlight actions, filters shared through `filter-group`, and a dual-axis network (panes with `x-axis-name` plus an axis `fold`).
- **Validates (PASS)** against the official XSD from github.com/tableau/tableau-document-schemas (schemas/2026_1). Stub schemas are needed for the `user` and `xml` namespaces; see the README.
- A semantic cross-reference check found 0 problems.
- The workbook has **not yet been opened in real Tableau**: only the user can do that.

**`build_presentation.py`.** Builds a 16-slide deck. If `screenshots/overview.png` and `screenshots/network.png`
exist they are embedded; otherwise slides 8 and 9 show HTML wireframes. All slides were screenshot-checked with
Playwright Chromium.

## Status / TODO
- [x] Data, analysis, figures, workbook (XSD-valid), deck, Google Form answers, README, viva notes
- [ ] **USER:** open the `.twbx` in Tableau 2026.1+. If anything fails, send the exact error and fix `build_workbook.py`. The fallback manual-build table is in the README.
- [ ] **USER:** publish to Tableau Public with downloads off. Save the screenshots to `screenshots/`, then re-run `build_presentation.py` (or Claude does it).
- [ ] **USER:** rehearse. Suggested split: Faheemuddin slides 1–8, Sanidhya slides 9–16.
