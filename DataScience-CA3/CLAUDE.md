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
| Dashboard size | **1900 × 1220 fixed** (user request) |
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
- **Second test (2026-10-10):** the file now loaded, but every sheet that used a parameter was removed with "The
  worksheet does not have a valid data source". Cause: the worksheet `<datasources>` listed `Parameters` *first*,
  and Tableau takes the first entry as the primary data source. Also missing: the data-source-level
  `<datasource-dependencies datasource='Parameters'>` block. Both were fixed by mirroring the genuine Superstore
  workbook inside dapi `samples/show_workbook_info/geocoding.twbx`, which has a CSV textscan source, parameter-driven
  worksheets and dashboards. Dashboards now list only `Parameters`.
- **Lint scripts** (scratchpad; they are easy to recreate): a dialect lint (element/attribute pairs vs genuine
  files) and an order lint (child order vs genuine files). Both are clean, apart from the axis `fold`/`synchronized`
  and the `path` encoding, which are in the official schema.
- **Third test (2026-10-10): the workbook opens.** Both dashboards render real data. Problems seen:
  - My colour maps were ignored, and Tableau used its default "Tableau 10" palette. Genuine data sources declare a
    `column-instance` for every field their style maps; that is now added before `<layout>`.
  - The KPI custom labels were ignored. Genuine panes pair `customized-label` with the
    `mark-labels-show=true` style; that is now added.
  - **The "Network Graph" sheet was missing from dashboard 2.** The cause is unknown, and the warning text was not
    reported. The dual-axis (`+`, `fold`, `synchronized`) and `path` syntax is confirmed by
    github.com/tomohiro-ono-works/tabsdk (verified against real workbooks; it ships a sample saved by Tableau
    2026.2.1, which is version 18.1 with the same manifest style as ours). Next step: ask the user whether a
    "Network Graph" tab exists and what warning appears.
- **Fourth test (2026-10-10):** colours and KPI tiles are fixed. The Network Graph is still missing, and the user
  reported no warning text.
- **Decision:** dashboard 2 now shows a **"People Map"** instead: a single-pane Circle scatter on employees.csv
  (x/y layout positions, size = betweenness, colour = community, broker labels, Community parameter filter).
  It is built only from constructs found in genuine files; the dialect lint finds 0 unmatched pairs in the main
  workbook. The network data source, the "Ties shown" parameter and the dual-axis sheet moved to the optional
  `tableau/Enron_Network_Ties_test.twbx`, which has sheets A dual-axis, B ties only and C people only. That lets
  the user report which ones survive, without risking the main dashboards.
- Event categories were shortened ("Leadership" became "Leaders", later "CEO"), the event and heat-map row headers widened
  (header width style), and the README, deck, form answers and viva notes now describe the People Map.
- **Fifth test (2026-10-10).**
  - The Overview dashboard is fully correct: colours, KPIs, events and heat-map.
  - The People Map was **blank on dashboard 2**, with no title and no legend.
  - Test workbook: A (dual axis) loaded with the correct marks cards but showed "No data available" and no title.
    B (ties, Line + path + Keep filter + gridline style) and C (people, Circle + size) render.
  - The only constructs shared by the two blank sheets and absent from every rendering sheet were **tooltip
    encodings** (`role_group`, AVG(contacts)) and **mark-transparency**.
  - Fix: the People Map now uses only proven constructs (C's circle sheet plus the Keep filter, text label and
    `mark-labels-show`). **Do not re-add tooltip encodings or mark-transparency** unless the test grid proves them.
- **Test workbook rebuilt as a one-screenshot bisection.** One "Test grid" dashboard holds:
  - T1: dual axis, 2021 pane layout (default pane + id 1, 2).
  - T2: dual axis, 2026/tabsdk pane layout (ground pane id 1 + axis panes id 2, 3).
  - T3: people + tooltips.
  - T4: people + transparency.

  None of these have tooltips, transparency or a size format unless that is the thing being tested. If T1 or T2
  renders, swap it in for the People Map on dashboard 2.
- **Events table.** It truncated on the user's display, so "Leaders" became "CEO" and two event texts were shortened
  (≤ 31 chars). The When and Event header widths are now 106 and 262, and the Overview's right column is 450 px.
- **Screenshots.**
  - The user's Tableau runs on a high-DPI Windows screen, and they had set both dashboards to Custom 1900 × 1220.
  - `screenshots/overview.png` is an interim crop of their screenshot. It still shows the old truncated events table.
  - Ask for **Dashboard ▸ Export Image…** PNGs of both dashboards for the final deck.
- **Redesign at 1900 × 1220 (user request, 2026-10-10).** Constant `W, H` in `build_workbook.py`.
  - Overview: KPI row of 150 px. Left: timeline 480 px, then heat-map and locality side by side. Right column of
    560 px: Period and Sender-role controls, the period legend, Key Events, and a "What the data shows" text box.
    Its numbers are read from `results/summary.json`.
  - Network: three columns. People Map (flex). A 290 px column with the Community control, the community legend,
    a role-group legend (newly added, for the two bar charts), and "How to read" and "What it shows" text boxes.
    A 640 px column with Rank-by, Top People and Community Composition.
  - Larger type: dashboard title 20, sheet titles 14/10, KPI numbers 32. The test grid adds T5 (mark `size` format).
- **Git — standing rule (user, 2026-10-10): push every change directly to `main`.** Commit on
  `claude/fervent-ritchie-8z9wsy`, which is kept equal to `main`, then `git push origin HEAD:main` and push the
  branch too. The user also commits to `main` themselves, so fetch first and make sure the push is a
  fast-forward. Use `GIT_LFS_SKIP_SMUDGE=1`, because `main` tracks large videos in LFS.
- **Sixth test (2026-10-10): exported images (Dashboard ▸ Export Image, 1900 × 1220).**
  - Test grid: **T1 and T2 (dual-axis ties + people) render; T3 (tooltip fields) was silently dropped**, which
    confirms the cause of every blank sheet. T4 (transparency) and T5 (size format) render.
  - Tableau did **not** keep the zone widths. Columns were re-sized to fit their content: text boxes widened their
    column and the map shrank. Genuine files pin sizes with `fixed-size='px' is-fixed='true'` on the child (px
    along the parent's direction) and `layout-strategy-id='distribute-evenly'` on rows of equal tiles. Both are
    now emitted (`Z(size=…)`, `Z(even=True)`).
  - The broker labels overlapped in the dense leadership core.
- **Changes after test 6.**
  - Dashboard 2 now shows **"Email Network Map"**: the T1 dual-axis structure on `network_paths.csv`. Pane 1 is a
    Line (ties, transparency 150); pane 2 is Circle with community colour, betweenness size, Broker-label text and
    size 1.6. It has the "Ties shown" (Parameter 4) control, and the colour legend uses `pane-specification-id='2'`.
  - The People Map is kept as a spare sheet, not on any dashboard.
  - The test workbook was deleted.
  - Layout: after the spring layout, an overlap-removal step pushes circles apart, and the top 6 brokers get
    ≥ 11 units for labels (`prepare_data.py`). Only x/y changed; every metric is identical. `network_paths.csv`
    gained `rank_betweenness`.
  - Heat-map: short column labels (calc "Recipient role (short)") and `cell` width 76 / height 30.
  - Deck: `screenshots/overview.png` = the user's clean export (11.png). Slide 9 is still a wireframe, waiting
    for an export of the new network dashboard.
- **Never use on Tableau 2026.2.3:** fields on the Tooltip shelf. Anything else used here is proven.
- **Seventh test (2026-10-10): both dashboards render as designed.** The network map shows ties, communities and
  broker labels; the pinned widths hold. The user's exports are now `screenshots/overview.png` (15.png) and
  `screenshots/network.png` (14.jpg); deck slides 8–9 show them.
  - Cosmetic leftovers: each KPI tile shows a thin vertical scrollbar, because the 32 pt number plus title is
    taller than the 150 px band. The Key Events table shows a horizontal scrollbar. Fix if asked: KPI band
    ~175 px or KPI font 28; events Event width ~280.
- **Status:** the Tableau work is done. Remaining user TODO: publish to Tableau Public (downloads off) and rehearse.

**`build_presentation.py`.** Builds a 16-slide deck. If `screenshots/overview.png` and `screenshots/network.png`
exist they are embedded; otherwise slides 8 and 9 show HTML wireframes. All slides were screenshot-checked with
Playwright Chromium.

## Status / TODO
- [x] Data, analysis, figures, workbook, deck, Google Form answers, README, viva notes
- [ ] **USER:** re-test the rebuilt `.twbx` (18.1 dialect) in Tableau Desktop 2026.2.3. If it fails, ask for the exact error list (Tableau prints line:column) and map each one onto `Enron_Email_Network.twb`. The fallback manual-build table is in the README.
- [ ] **USER:** publish to Tableau Public with downloads off. Save the screenshots to `screenshots/`, then re-run `build_presentation.py` (or Claude does it).
- [ ] **USER:** rehearse. Suggested split: Faheemuddin slides 1–8, Sanidhya slides 9–16.
