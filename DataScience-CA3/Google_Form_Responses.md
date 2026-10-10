# CA-3 Google Form — responses to paste

## 1) Title of the Problem Statement

Enron Email Network Analytics: An Interactive Tableau Dashboard of Communication Patterns, Communities and Privacy Risks during a Corporate Collapse (1999–2002)

## 2) Objectives

1. To acquire a real-world, publicly released dataset — the Enron email network (184 employee email addresses, 125,409 sender–recipient records, 1999–2002) — and document its source.
2. To clean and prepare the data by removing duplicate and artefact records, merging the different email addresses of the same person, and checking the timestamps.
3. To model the email traffic as a social network graph (directed and undirected, weighted, with strong and weak ties).
4. To test whether the email graph shows the locality property of social networks (friends of friends being connected more often than chance).
5. To identify the most important people and information brokers using centrality measures (degree, betweenness, PageRank).
6. To detect communities in the network with the Girvan–Newman algorithm and validate them with modularity and the Louvain method.
7. To compare communication volume, hierarchy and network structure across the pre-crisis, crisis and post-bankruptcy periods.
8. To design and build an interactive Tableau dashboard that applies data-visualisation principles and presents the insights clearly.
9. To compare the Tableau Creator and Tableau Viewer licences and explain their relevance to building and sharing this dashboard.
10. To analyse the privacy, security and ethical issues of the dataset and apply privacy-by-design measures (pseudonymisation, data minimisation, metadata-only analysis).

## 3) How each objective is achieved (techniques)

1. **Data acquisition:** downloaded the `enron` graph from the igraphdata R package (the Johns Hopkins version of the CMU Enron corpus released by the US regulator FERC) and loaded the R `.rda` file into Python (pandas) with the `rdata` library: a people table (name, job title) and an email table (sender, recipient, time, To/CC/BCC). Source, size and citation are documented.
2. **Data cleaning (Python, pandas):** kept January 1999 – June 2002 (removed impossible 1979 dates); removed BCC rows (each one duplicates a CC row); entity resolution merged 184 addresses into 149 people; removed self-addressed copies; removed identical sender–recipient–time rows (the same email stored in several folders). Result: 34,374 unique deliveries and 20,074 messages; 73% of the raw records were duplicates or artefacts. A month-by-month check of the start-of-day hour exposed a ~5-hour timestamp drift in 2001, so hour-of-day analysis was excluded.
3. **Graph modelling (NetworkX):** built a directed weighted graph (weight = number of emails) and an undirected graph. Following Unit 5, ties are labelled strong (emails in both directions) or weak (one direction only). Computed density, reciprocity (63%), average path length (2.0) and diameter (4).
4. **Locality test (Unit 5):** computed P(y–z edge | x–y and x–z edges) as closed triples ÷ all connected triples (triangle counting) and compared it with the edge density, which is what a random graph would give. Result: 0.42 vs 0.16 overall, and higher in every month with 50+ active people, so the graph behaves like a social network.
5. **Centrality analysis:** computed degree (number of contacts), betweenness centrality (how often a person lies on shortest paths, i.e. acts as a broker), PageRank (weighted, directed) and the clustering coefficient for every person. People are ranked by each measure, and the top brokers are compared across periods.
6. **Community detection:** ran the Girvan–Newman algorithm (repeatedly removing the edge with the highest edge betweenness) on the strong-tie graph and kept the split with the highest modularity (Q = 0.52, 7 communities). Cross-checked with the Louvain method (NMI 0.62). Communities are named from the job titles inside them, e.g. leadership core, gas pipeline & regulatory, trading desks.
7. **Period comparison:** split the timeline at public events (Skilling's resignation on 14 Aug 2001; the bankruptcy on 2 Dec 2001). For each period, compared deliveries per week (163 → 541), the share of traffic involving executives (17% → 22% → 24%), the share of broadcast emails (5+ recipients) and the top brokers. Monthly network snapshots track change over time.
8. **Tableau dashboard:** exported 5 tidy CSV data sources and built a workbook with 11 sheets and 2 dashboards.
   - **Overview dashboard:** KPI tiles, a weekly area chart coloured by period, a sender-role × recipient-role heat-map, a monthly locality line chart and a key-events table.
   - **Network dashboard:** a people map that places every employee by a force-directed layout of the email network (circles sized by betweenness, coloured by community, top brokers labelled), a Top-15 bar chart switched by a parameter, and a community composition chart.
   - **Interactivity:** parameter drop-downs (period, sender role, ranking metric, community) that filter the views, highlight actions and tooltips.
   - **Design principles:** overview first, then filter, then detail (Shneiderman); a Z-pattern layout; one meaning per colour with a colour-blind-checked palette; sorted bars; no pie charts; less non-data ink.
9. **Licence comparison:** compared the licences using Tableau's official site-role and licensing documentation and its published price list (Tableau Cloud, per user per month, billed yearly).
   - **Creator (US$75 Standard / US$115 Enterprise):** Tableau Desktop, Prep Builder and web authoring; can connect to data, build and publish.
   - **Viewer (US$15 / US$35):** can only view and interact (filters, highlights, parameters, comments, subscriptions); cannot edit, publish or download full data.
   - **For this dashboard:** the 2 analysts need Creator; faculty and reviewers need only Viewer. Explorer sits in between, and Tableau Public is free but makes everything public.
10. **Privacy, security and ethics:** assessed the dataset with the Unit 6 framework: data collection and secondary reuse, storage and security, the "public data" question, re-identification and consent, and emerging risks such as AI models trained on Enron emails.
    - **Measures applied:** metadata only (no message text or topic labels); real names only for the 10 company officers, with everyone else pseudonymised (e.g. VP-03); job titles reduced to 7 role groups; email addresses removed.
    - **Publishing:** data download disabled when publishing to Tableau Public; least-privilege Viewer access recommended in an organisation.
    - **Transparency:** data-quality limits reported openly.
