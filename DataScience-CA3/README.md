# Data Science CA-3 — Enron Email Network Analytics (Tableau case study)

**Members:** Faheemuddin Sayyed (PRN 23070122196) · Sanidhya Awasthi (PRN 23070122192) — **Guided by:** Dr. Deepak Dharrao
**Assignment:** Case-study-based Tableau dashboard + presentation & viva (Units 5 and 6), AY 2026–27.

**Problem statement.** When Enron collapsed in 2001, US regulators made the internal email of about 150 employees
public. The raw data is noisy (duplicates, aliases, bad timestamps) and sensitive (real names). We turn its
*metadata* (who emailed whom, when) into an interactive Tableau dashboard. The dashboard shows how communication
volume, communities and key people changed before, during and after the crisis, while protecting the employees'
privacy.

## What is in this folder

| Path | What it is |
|---|---|
| `tableau/Enron_Email_Network.twbx` | **The Tableau workbook** (data packaged inside). Open this one. |
| `tableau/Enron_Email_Network.twb` | Same workbook as plain XML (source; it needs the CSVs in `tableau/Data/enron/`, created by the build script). |
| `CA3_Presentation.html` | The slide deck (16 slides, self-contained; open in Chrome, press **F** for full screen). |
| `Google_Form_Responses.md` | Text to paste into the CA-3 Google Form (title, 10 objectives, techniques). |
| `Viva_Notes.md` | Likely viva questions with short answers. |
| `data/raw/enron.rda` | Original dataset (igraphdata `enron` graph, 0.2 MB). |
| `data/processed/*.csv` | Cleaned, pseudonymised tables used by Tableau. |
| `analysis/prepare_data.py` | Cleaning, privacy rules and all network metrics → CSVs + `results/summary.json`. |
| `analysis/make_figures.py` | Findings charts for the slides → `figures/*.png`. |
| `tableau/build_workbook.py` | Generates the `.twb`/`.twbx` and validates the XML against Tableau's official schema. |
| `build_presentation.py` | Builds `CA3_Presentation.html`. |

Git LFS was **not** needed: the raw dataset is 0.2 MB, and all processed CSVs together come to about 6 MB.

## 1. Open the dashboard in Tableau

1. Install **Tableau Public** (free, tableau.com/products/public/download) or Tableau Desktop (any recent
   version; tested target: Desktop 2026.2.3). The workbook is written in the classic 18.1 format that Tableau
   2021 saved, which every later version opens and upgrades. Tableau may ask to upgrade it on save; say yes.
2. Double-click `tableau/Enron_Email_Network.twbx`. You should see two dashboards, **1 Overview** and **2 Network**, plus 11 sheets.
3. Quick check:
   - **1 Overview:** the *Period* and *Sender role* drop-downs (parameter controls) change the KPIs, the volume chart and the heat-map.
   - **2 Network:** the *Rank people by* drop-down switches the Top-15 chart; *Community* filters the People Map. Clicking a bar highlights that person on the map.
4. If Tableau ever says it cannot find a data file, point it to the matching CSV in `data/processed/`. The file names are the same.

### Publish to Tableau Public and take screenshots

1. **File ▸ Save to Tableau Public As…**, sign in, and name it e.g. *Enron Email Network Analytics*.
2. On the published page, open the viz settings and **turn off "Allow workbook and its data to be downloaded"**.
   This is part of our privacy argument.
3. Take a full-window screenshot of each dashboard. Save them as `screenshots/overview.png` and
   `screenshots/network.png`, then run `python3 build_presentation.py`. Slides 8 and 9 then show the real
   dashboards instead of the layout wireframes. You can also just send the two screenshots to Claude.

### Optional: the full node-link graph (ties + people)

`tableau/Enron_Network_Ties_test.twbx` is a small separate workbook with the email *ties* drawn as lines: a
dual-axis "ties + people" sheet and two single-layer variants. Tableau 2026.2.3 dropped the ties sheet from the
main workbook without a visible reason, so it was moved out to keep the main dashboards safe. If you open it, note
which of the three tabs survive. The full node-link figure is also on slide 12 of the deck.

### If the generated workbook does not open (fallback, ~30 min by hand)

Connect each CSV in `data/processed/` as a separate data source (Connect ▸ Text file), then build:

| Sheet | Data source | How to build |
|---|---|---|
| KPI tiles (×4) | deliveries | Text mark. Use SUM(Deliveries) where Deliveries = `1`; COUNTD(message_id); COUNTD(sender); and Cross-community share = `SUM(IF [community_link]="Across communities" THEN 1 ELSE 0 END)/SUM([Deliveries])`. |
| Email Volume Timeline | deliveries | Columns: continuous WEEK(sent_at). Rows: SUM(Deliveries). Area mark. Colour: period. |
| Communication Flow by Role | deliveries | Rows: sender_role. Columns: recipient_role. Square mark. Colour and Label: SUM(Deliveries). |
| Locality Test by Month | monthly_locality_long | Columns: continuous MONTH(month). Rows: SUM(value). Colour: metric. Filter: reliable = Yes. |
| Key Events | events | Rows: event_no, date_label, event. Text: category. |
| People Map | employees | Columns: AVG(x). Rows: AVG(y). Circle mark. Detail = display_name, Colour = community, Size = AVG(betweenness), Label = *Broker label* (`IF [rank_betweenness] <= 6 THEN [display_name] ELSE "" END`). Fix both axes to -4…104 and hide them. |
| Top People | employees | Parameter *Rank people by* (Betweenness, PageRank, Contacts, Emails sent). *Selected metric* = CASE on the parameter. Rows: display_name, sorted descending by the metric. Columns: SUM(Selected metric). Colour: role_group. Filter *Selected rank* ≤ 15. |
| Community Composition | employees | Rows: community. Columns: CNT(employee_key). Colour: role_group. |

Dashboards: **1 Overview** has the KPIs on top, the timeline, and the heat-map and locality chart below, with the Period / Sender-role controls and key events on the right. **2 Network** has the graph on the left and the parameter, Top People and Community Composition on the right. Add a highlight action on *Person*.

## 2. Reproduce everything

```bash
pip install -r requirements.txt
python3 analysis/prepare_data.py           # cleaning + metrics  -> data/processed, results/summary.json
python3 analysis/make_figures.py           # slide charts        -> figures/
python3 tableau/build_workbook.py         # Tableau workbook    -> tableau/
python3 build_presentation.py              # deck                -> CA3_Presentation.html
```

**Why the classic format?** A first version used Tableau's new 2026.1 "ManifestByVersion" format and passed the
official schema (github.com/tableau/tableau-document-schemas), but Tableau Desktop 2026.2.3 refused to load it
(error D2E8DA72: its loader expects attributes the published schema does not mention). The generator now mirrors,
element by element, workbooks genuinely saved by Tableau 2021.x, and dashboard filtering uses parameters instead of
shared filter groups.

## 3. Method in brief

1. **Clean.** Keep Jan 1999 – Jun 2002, drop BCC rows (each one copies a CC row), merge 184 addresses into 149 people, and remove self-addressed copies and folder duplicates. This leaves **34,374** deliveries and **20,074** messages; 73% of the raw records were removed.
2. **Check quality.** The start-of-day hour drifts by ~5 h between Apr and Sep 2001 (`data/processed/clock_check.csv`), so hour-of-day analysis is excluded.
3. **Protect.** Use metadata only. Real names are kept only for the 10 officers (CEO/President/COO/CFO titles); everyone else becomes a role pseudonym such as `VP-03`, and titles are reduced to 7 role groups.
4. **Graph.** Build directed and undirected weighted graphs, with strong (two-way) and weak (one-way) ties: 816 strong and 972 weak.
5. **Unit 5 metrics.**
   - Locality test: P(y–z tie given x–y and x–z ties) = **0.42**, against a density of **0.16**.
   - Centrality: degree, betweenness and PageRank.
   - Communities: **Girvan–Newman** (best modularity 0.52, 7 communities), cross-checked with Louvain (NMI 0.62).
6. **Periods.** Pre-crisis (to 13 Aug 2001), crisis (14 Aug – 2 Dec 2001) and post-bankruptcy.

## 4. Key findings

- Crisis traffic is **3.3×** the pre-crisis rate (163 → 541 deliveries a week). The peak month is October 2001, when the $618M loss was announced.
- Traffic involving an executive rises from **17% → 22% → 24%**. Broadcast emails (5+ recipients) rise from 3.3% → 5.6%.
- Two of the top four brokers have no recorded job title. During the crisis, the top three brokers were all executives.
- The 7 communities match real business units: a leadership core, gas pipeline & regulatory, and several trading desks.

## 5. Ethics, privacy and security (Unit 6)

**Issues:**
- No consent from the employees, and secondary reuse of data released for a legal investigation.
- The "public data" fallacy: being public does not make every reuse acceptable.
- Re-identification through names, titles and network position.
- Metadata alone exposes hierarchy and relationships.
- Enron emails are inside public AI training corpora.

**Measures:**
- Data minimisation: metadata only.
- Pseudonymisation and coarse role groups; no email addresses in any exported file.
- Downloads switched off on Tableau Public.
- Least-privilege Viewer access in an organisation.
- Limitations reported honestly.

## Sources

- Klimt & Yang, "The Enron corpus", ECML 2004.
- Priebe, Conroy, Marchette & Park, "Scan statistics on Enron graphs", CMOT 11(3), 2005. Dataset: igraphdata `enron`.
- Girvan & Newman, PNAS 2002.
- Freeman, Sociometry 1977.
- Leskovec, Rajaraman & Ullman, *Mining of Massive Datasets*, ch. 10.
- Tableau Help, "Permissions, Site Roles, and Licenses".
