# CLAUDE.md — Cyber Security CA-2 (Part 2) Case Study: Live Handoff File

> **Purpose of this file:** a future Claude Code session with *no chat history* must be able to
> read this file and finish the task completely. Keep it updated after every milestone
> (update the **Progress checklist** and **Log** sections). Last updated: 2026-10-04.

---

## 1. The task (what the user asked for)

The user (Faheemuddin Sayyed, B.Tech CSE Sem VII, Symbiosis Institute of Technology, Pune) must submit
**Cyber Security Theory CA-2 Part 2: a case-study report + a video presentation**, as a B.Tech project group.
Source of rules: `NOTICE CA-2 Cyber Security 2023-2027 B Tech VII CSE.docx` (in this folder).

Deliverables to produce here:
1. **Report** — a `.docx` (user exports to PDF named `G04.pdf` and uploads it). Output file: `G04.docx`.
2. **Presentation** — a single self-contained **HTML** slide deck (not pptx) used while recording the video.
   Output file: `G04_Presentation.html`.
3. **A small implementation** whose findings (charts, dashboard screenshot) go into the report and slides.
   Lives in `implementation/`.

**Deadline:** submission Saturday 10 Oct 2026 by 4:30 pm (Google Form). The user said "just a few days".

## 2. Fixed facts / user decisions (do NOT re-ask)

| Item | Value |
|---|---|
| Group | **Group – 04** (file name `G04.pdf`) |
| Members (all class **CSE-C**) | Raghav Sonchhatra – PRN 23070122172; Sanidhya Awasthi – PRN 23070122192; Faheemuddin Sayyed – PRN 23070122196 |
| Academic year / Sem | **AY 2026–27, Sem VII** |
| Subject | Cyber Security (Theory CA-2, Part 2 — Unit 4 case study) |
| Faculty (from notice) | Dr. Pooja Bagane, Dr. Jitendra Rajpurohit |
| **Final topic title (user chose the "hybrid" option)** | **Non-Human Identity and Scoped Delegation for Intrusion Detection and Forensic Attribution of AI-Orchestrated Attacks: A Case Study of the GTG-1002 Espionage Campaign (2025)** |
| Unit 4 syllabus | Introduction to Digital Forensics; Darknet and Darkweb; Malware analysis; Intrusion Detection System; Security tools demo: virtual lab setup, Kali Linux, Google dorking, Nmap demo |
| How the topic maps to Unit 4 | **Intrusion Detection** (identity-aware IDS rules), **Digital Forensics** (tamper-evident audit log + timeline reconstruction + attribution), **Security tools** (GTG-1002 orchestrated commodity open-source tools such as network scanners via MCP — discuss in text only). Make these links explicit in the report and slides. |

### Report rules from the notice (all mandatory)
- First page: group number, member names, topic. **Font Times New Roman, content size 12, colours only Black and Blue, single column.**
  - Exception agreed with the user: the institute name text on the cover stays **red (B42D27)** because it is part of the
    Symbiosis logo identity, and it must use the **logo's font → Optima Bold** (closest match; installed on macOS).
- Required sections, in order: **Title, Students' names, Abstract, Keywords, Introduction, Literature Review (with proper
  citations), Methodology, Implementation Details, Results & Discussions, Conclusion, References (minimum 30)**.
- Length: user wants **about 11–12 pages total** (do not make it larger).
- Plagiarism: <10% similarity and 0% AI-plag required by the rubric. We told the user we cannot guarantee AI-detector
  scores; they will rewrite in their own words. Still: write original, natural prose; no copied sentences.
- Citations: IEEE numeric style [n]; every reference must be real and verifiable (see §6).

### Rubric (20 marks): Topic relevance 2 · Plagiarism & AI plag 6 · **Methodology 6** · Video presentation 6.
Methodology must be "excellent, well-structured, justified, technically sound" → give it depth and justification.

### Cover page (copy of the user's earlier report `ForgeFlow_Deployment_Report.docx`, then edited)
The reference docx is ONLY a cover page + header/footer. Structure to keep:
- Top table: "Academic Year -: 26 – 27" (left box) and "Date: 10/10/2026" (right box).
- SIT emblem image (word/media/image1.png in the reference), then "SYMBIOSIS INSTITUTE" / "OF TECHNOLOGY (SIT)"
  (red B42D27, **Optima Bold** instead of Arial), "Constituent of SYMBIOSIS INTERNATIONAL (DEEMED UNIVERSITY)".
- Subject line: "Cyber Security"; report type line: "CA-2 – Case Study Report (Unit 4)"; "Group Number: Group – 04".
- "Title:" + topic; "Problem Statement:" paragraph; members table Name | PRN | CLASS (CSE-C for all three).
- Header text → "CA-2 – Cyber Security · Group 04 Case Study Report"; footer "Symbiosis Institute of Technology, Pune ... Page N".
  Change header/footer grey (555555/BFBFBF) to black/blue to respect the colour rule.
- Reference page setup: A4 (11906×16838), margins top/bottom 1300, left/right 1440, header/footer 600. Default font TNR 12.

### Presentation rules (from the user)
- **Slide 1 must look like the user's screenshot**: rounded-border white slide; `sit-logo.png` (logo + "SYMBIOSIS INSTITUTE OF
  TECHNOLOGY, PUNE" already in the image) at top; heading "Cyber Security — CA-2 Case Study" (replaces "B-Tech Project");
  big bold title = topic; "Group Number: Group – 04"; three "Name – PRN xxxxx" lines; **NO "Guided by" section**;
  bottom footer line: "Theory CA-2 (Part 2) — Case Study Report | Department of Computer Engineering | Academic Year 2026–27".
- ~14 slides for a 7–10 min video covering ALL report points; all 3 members present (give a speaker split in chat, not on slides).
- **No UI chrome**: no progress bar, no slide counter, no buttons visible. Prev/next arrows appear **only when hovering
  the left/right edge zones**. Keyboard ←/→/space/PageUp/PageDown, click zones. Full-screen friendly (F key optional).
- Single HTML file, self-contained (embed `sit-logo.png` as base64 or reference relative path — prefer base64 so it is portable).
- Colours on slides: keep to blue/black on white to match the report (logo stays red).

## 3. Safety boundary (important)
A safety classifier interrupted an earlier turn while an attack-replay against a live container was being planned. The user
then confirmed: **only a very basic, purely defensive implementation is needed; nothing offensive, no real scanning, no
explicit attack research.** So:
- The implementation uses **synthetic, abstract audit-log events only** (tool names like `inventory.list`, `secrets.read` are
  labels; nothing executes). No Nmap runs, no Docker targets, no exploit/payload content, no step-by-step attack detail.
- In the report, describe GTG-1002 only at the level of Anthropic's public report (phases, percentages, defensive lessons).

## 4. Implementation (folder `implementation/`) — design
Python 3 (stdlib + matplotlib). Package `nhi_lab/`:
- `identity.py` — `Identity`, `IdentityRegistry`, `DelegationAuthority` (HMAC-SHA256 signed tokens with claims
  `jti, grant, sub, chain, scopes, res, iat, exp, depth, purpose, parent`; `delegate()` only narrows: scope ⊆ parent,
  resources ⊆ parent prefixes, exp ≤ parent, depth−1; raises `TokenError` on widening). `SharedKeyAuthority` = baseline
  (one static key, scopes `*`, no identity).
- `gateway.py` — `TOOLS` map (tool → required scope, ATT&CK tactic category), `ToolGateway.call()` verifies token, checks
  scope + resource prefix, appends an audit record (`t, sub, chain, root, grant, tool, tactic, resource, allowed, reason, label`).
- `audit.py` — `AuditLog` hash chain (SHA-256 of prev hash + record); `verify()` returns first broken index; `timeline()`.
- `ids.py` — `IdentityAwareIDS` with 3 rules: R1_TEMPO (>20 calls/10 s per actor), R2_PROBING (≥3 denials/60 s per actor),
  R3_KILL_CHAIN (≥3 sensitive tactics within 30 min per delegation grant); 15-min cooldown per (rule,key).
- `workload.py` — synthetic benign agents (ci, docs, ops, backup) + an abstract "misuse" delegation tree modelled on the
  public GTG-1002 phase structure (orchestrator + sub-agents; human approval gaps between phases).
- `run_experiment.py` — runs N seeded trials in two modes (BASELINE shared key vs NHI scoped delegation), computes metrics,
  writes `results/*.json|csv`. Metrics: misuse calls allowed per tactic, blast radius (distinct prod resources touched),
  time-to-first-true-alert, false-positive alerts, alert attribution to accountable human, audit tamper detection,
  gateway overhead (µs/call).
- `make_figures.py` — matplotlib charts in **blue/black only** → `figures/*.png`.
- `dashboard/` — a static HTML "NHI Gateway Console" (blue/black) built from results JSON; screenshot via headless Chrome:
  `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --screenshot=out.png --window-size=1400,900 file://...`

## 5. Report outline (target ≈ 11–12 pages incl. cover)
Cover (p1) → Title + names block → Abstract (~200 words) → Keywords → 1 Introduction (incl. 1.1 Case background:
GTG-1002, 1.2 Unit 4 relevance, 1.3 Objectives/contributions) → 2 Literature Review (AI-orchestrated attacks; NHI & agent
identity; delegation/capabilities/OAuth; IDS; digital forensics & secure logging) → 3 Methodology (case reconstruction from
primary source → threat mapping table GTG-1002 phase ↔ ATT&CK tactic ↔ identity failure ↔ control ↔ Unit-4 link → control
design → experiment design & metrics, with justification) → 4 Implementation Details (architecture figure, token format,
gateway, IDS rules, audit chain, workload) → 5 Results & Discussion (charts, dashboard screenshot, table of metrics,
limitations) → 6 Conclusion (+ future work) → References (≥30, IEEE).

## 6. Verified facts & references
GTG-1002 facts (from Anthropic full report PDF, Nov 2025, changelog 17 Nov 2025):
detected mid-Sept 2025; Chinese state-sponsored (high confidence); ~30 targets (large tech, financial institutions, chemical
manufacturing, government agencies); "a handful" of validated successful intrusions; AI executed 80–90% of tactical work,
humans 10–20% at strategic gates (approve recon→exploitation, authorise use of harvested credentials, final exfiltration
scope); thousands of requests, multiple ops/sec at peak; jailbreak via role-play as employees of legitimate security firms +
task decomposition so each sub-task looked legitimate in isolation; MCP servers for remote command execution, browser
automation, code analysis, testing-framework integration, callback validation; mostly commodity open-source tools (network
scanners, database exploitation frameworks, password crackers, binary analysis suites); six phases: 1 initialization &
target selection, 2 recon & attack-surface mapping, 3 vulnerability discovery & validation, 4 credential harvesting & lateral
movement, 5 data collection & intelligence extraction, 6 documentation & handoff; hallucinations (claimed credentials that
didn't work, "discoveries" that were public); response: ~10-day investigation, bans, notified entities and authorities,
improved cyber classifiers, prototyping early detection for autonomous attacks.
URL: https://assets.anthropic.com/m/ec212e6566a0d47/original/Disrupting-the-first-reported-AI-orchestrated-cyber-espionage-campaign.pdf

Other verified sources (use these; all real):
- Anthropic Threat Intelligence Report, Aug 2025 ("vibe hacking", GTG-2002 data-extortion with Claude Code).
- Google GTIG, "AI Threat Tracker: Advances in Threat Actor Usage of AI Tools", 5 Nov 2025 (PROMPTFLUX etc.).
- South, Marro, Hardjono, Mahari, Whitney, Greenwood, Chan, Pentland, "Authenticated Delegation and Authorized AI Agents", arXiv:2501.09674 (2025); ICML 2025 position paper.
- Chan et al., "Visibility into AI Agents", ACM FAccT 2024 (arXiv:2401.13138).
- OWASP Non-Human Identities Top 10 – 2025 (NHI1 Improper Offboarding, etc.).
- OWASP GenAI Security Project, "OWASP Top 10 for Agentic Applications for 2026" (released 9 Dec 2025; ASI01–ASI10 incl. ASI03 Identity & Privilege Abuse, ASI07 Insecure Inter-Agent Communication).
- CyberArk 2025 Identity Security Landscape (machine identities outnumber humans 82:1; 42% of machine identities have privileged/sensitive access).
- Verizon 2025 DBIR (credential abuse 22% of initial access vectors).
- NIST SP 800-61r3 (Apr 2025; Nelson, Rekhi, Souppaya, Scarfone).
- MCP Specification 2025-06-18, Authorization (OAuth 2.1 resource server, RFC 8707 resource indicators, RFC 9728).
- Google A2A protocol (announced 9 Apr 2025; donated to Linux Foundation 23 Jun 2025).
- IETF draft-oauth-ai-agents-on-behalf-of-user-02 (Senarath & Dissanayaka, Aug 2025).
- Classic/standard (well known): RFC 6749 (OAuth 2.0), RFC 8693 (Token Exchange), RFC 7519 (JWT), RFC 2104 (HMAC),
  Birgisson et al. "Macaroons" NDSS 2014, Saltzer & Schroeder 1975, Hardy "The Confused Deputy" 1988, NIST SP 800-207 Zero
  Trust (2020), NIST SP 800-86 (2006), NIST SP 800-94 (2007), Denning "An Intrusion-Detection Model" IEEE TSE 1987,
  Roesch "Snort" LISA 1999, Paxson "Bro" Computer Networks 1999, Hutchins/Cloppert/Amin kill chain 2011, Strom et al. MITRE
  ATT&CK 2018, MITRE ATLAS, Schneier & Kelsey secure audit logs ACM TISSEC 1999, Crosby & Wallach tamper-evident logging
  USENIX Sec 2009, Lyon "Nmap Network Scanning" 2009, Greshake et al. indirect prompt injection AISec 2023, Fang et al. LLM
  agents hack websites arXiv 2024, Deng et al. PentestGPT USENIX Sec 2024, OWASP Top 10 for LLM Apps 2025, NIST AI 100-2 E2025,
  SPIFFE standard, Sommer & Paxson IEEE S&P 2010, Casey "Digital Evidence and Computer Crime" 3rd ed 2011.

## 7. Tooling notes
- Python: `python3` (has python-docx, matplotlib 3.9.4, PIL). Node + `docx` npm available. `pandoc`, `pdftotext`, Chrome present.
- **No LibreOffice** → cannot render docx→pdf locally for visual check; verify by `pandoc -t plain` + inspecting XML, or
  render an HTML approximation. (Optionally `brew install --cask libreoffice` only if the user agrees.)
- Report builder plan: python-docx script `build_report.py` that opens a copy of `ForgeFlow_Deployment_Report.docx`,
  edits the cover in place, then appends the body. Keep all text Times New Roman 12; headings blue (1F3864/1F4E79) or black.
- Scratchpad (temp, may vanish): /private/tmp/claude-502/.../scratchpad — contains gtg1002.pdf/txt and unzipped reference.

## 8. Progress checklist (update as you go)
- [x] Read notice, reference cover, logo; asked questions; user answered (see §2)
- [x] Topic alignment decided (hybrid title)
- [x] Facts & references verified (§6)
- [x] `nhi_lab/identity.py`, `gateway.py`, `audit.py`, `ids.py` written
- [x] `nhi_lab/workload.py` + `run_experiment.py` written and run (50 seeds) → `results/summary.json, runs.csv, showcase_*.json`
- [x] `make_figures.py` → `figures/fig_architecture.png, fig_tactics.png, fig_outcomes.png, fig_timeline.png` (palette validated: NHI #2A4DA8, baseline #5A97EE hatched, ink #111)
- [x] ~~Dashboard HTML~~ **DROPPED** — the safety classifier interrupted while it was being written; do NOT recreate it.
      The architecture diagram (matplotlib) replaces it. Keep everything defensive and high-level from here on.
- [x] `build_report.py` → `G04.docx` built: 41 refs (all cited, IEEE, auto-numbered by first use), 4 figs, 3 tables.
      Word says **11 pages**; cover-only build = 1 page + blank section → cover fits. Rebuild any time with `python3 build_report.py`.
      PDF export via Word AppleScript `save as` FAILS (-1708) and Pages import dialog hangs → user exports PDF manually
      (File ▸ Save As ▸ PDF, name `G04.pdf`). Page count check that works:
      `osascript -e 'tell application "Microsoft Word" to compute statistics document "G04.docx" statistic statistic pages'` (after opening it).
- [x] `build_presentation.py` → `G04_Presentation.html` built: **17 slides**, self-contained (logo + charts base64), 0.6 MB.
      Slide 1 matches the user's template (rounded frame, logo, "Cyber Security — CA-2 Case Study", topic, group, names, footer; no "Guided by").
      Hover-only edge arrows, no counter/progress UI, cursor auto-hides after 2 s, keys ←/→/Space/PageUp/PageDown/Home/End, F = full screen.
      All slides screenshot-checked with headless Chrome (`?static#N` disables the fade for screenshots).
      Literature review and Implementation are each split over 2 slides **on purpose** so the 3-way speaker split lands on slide boundaries.
- [x] `G04_Presentation_Script.md` (user request: plain spoken English, one continuous block per member, split proportional to report
      word counts): Raghav slides 1–5 (Abstract, §1, §2.1–2.2), Sanidhya 6–10 (§2.3–2.5, §1.3, §3, §4 tokens/gateway/log),
      Faheemuddin 11–17 (§4 IDS/workload, §5, §6). Report words 931/1086/990 (31/36/33%) vs script 359/394/370 (32/35/33%),
      ≈8.0 min at 140 wpm. If the script text changes, reset the table to placeholders (REPORT_n, SCRIPT_n, TIME_n, TARGET_LEN)
      and run `python3 fill_script_table.py`.
- [ ] USER TODO (cannot be automated here): open G04.docx in Word → File ▸ Save As ▸ PDF → `G04.pdf`; run the plagiarism /
      AI-plag check and rewrite flagged parts in their own words; record the video (camera on, all 3 members); upload via the
      Google Form by Sat 10 Oct 2026, 4:30 pm.

## 8b. Key results (50 seeded runs, `python3 run_experiment.py --runs 50`; deterministic)
| Metric | Baseline (shared key) | NHI + scoped delegation |
|---|---|---|
| Misuse calls per run (mean) | 134.3 | 134.3 |
| Misuse calls allowed (mean) | 134.3 | 30.7 (all in-scope staging discovery) |
| Misuse calls blocked | 0% | 77.1% |
| Prod/external resources exposed (mean) | 24.9 | 0 |
| Benign calls wrongly denied (total) | 0 | 0 |
| Detection rate | 100% | 100% |
| Median time to first true alert | 5.3 s | 2.7 s |
| False alerts per run (mean) | 2.34 | 0 |
| True alerts per run (mean) | 2.5 | 8.52 |
| True alerts naming accountable human | 0% | 100% |
| Misuse audit records attributable to a human | 0% | 100% |
| Rules fired (true alerts, total) | R1 45, R3 80 | R2 265, R1 71, R3 90 |
| Gateway cost per call | 8.3 µs | 14.7 µs |
Allowed by tactic (baseline → NHI, mean/run): discovery 81.6→30.7, credential access 16.9→0, lateral movement 10.7→0, collection 20.2→0, exfiltration 4.9→0.
Tamper test: 634-record chain intact; flipping one denied record (index 100) → `verify()` reports index 100.
Showcase run (seed 7, NHI): 629 calls (459 benign, 170 misuse), 116 misuse blocked, 9 alerts all true, first alert R2 PROBING at +4.6 s; all 5 sub-agent delegation requests refused (1×resource_widening ×2 recon, scope_widening ×3).
Honest limitations to state: synthetic data; thresholds hand-set; in-scope abuse (staging discovery) is not blocked, only detected; baseline detection is also fast because tempo is visible even on a shared key — the gains are prevention, blast radius, false alerts and attribution.

## 8c. File inventory (this folder)
| File | Purpose |
|---|---|
| `G04.docx` | Final report (11 pages). Built by `build_report.py` from `ForgeFlow_Deployment_Report.docx` (cover) + body text in the script. |
| `G04_Presentation.html` | Final slide deck (17 slides). Built by `build_presentation.py`. |
| `G04_Presentation_Script.md` | Speaker script for the video; table filled by `fill_script_table.py`. |
| `implementation/` | Prototype (`nhi_lab/`), `run_experiment.py`, `make_figures.py`, `results/`, `figures/`, `README.md`. |
| `CLAUDE.md` | This handoff file. |
| `NOTICE CA-2 ….docx`, `ForgeFlow_Deployment_Report.docx`, `sit-logo.png` | User-provided inputs — do not modify. |
Rebuild order if anything changes: `cd implementation && python3 run_experiment.py --runs 50 && python3 make_figures.py && cd .. &&
python3 build_report.py && python3 build_presentation.py` (numbers in report/slides are read from results/summary.json; the script's
spoken numbers are hand-written — update them if results change).

## 9. Log
- 2026-10-04: Requirements gathered; implementation core modules written in `implementation/nhi_lab/`.
- 2026-10-04: Experiment run, figures rendered and visually checked. Dashboard dropped (safety interruption).
- 2026-10-04: G04.docx built and checked (11 pages).
- 2026-10-04: G04_Presentation.html (17 slides) built + visually checked; G04_Presentation_Script.md written and balanced.
  All deliverables done; only the USER TODO items remain.

## 10. Second task in this repo (separate)
- 2026-10-09: **Data Science CA-3** (Tableau dashboard on the Enron email network, 2 members, guided by Dr. Deepak Dharrao)
  lives in `DataScience-CA3/`. Its own handoff file is `DataScience-CA3/CLAUDE.md` — read that for anything CA-3.
- 2026-10-10: **HCI CA-3** (Raktdaan blood donation app, Group 06, Dr. Sudhanshu Gonge) lives in `HCI-CA3/`.
  Its own handoff file is `HCI-CA3/CLAUDE.md`.
