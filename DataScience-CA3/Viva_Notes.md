# Viva notes — likely questions, short answers

**Why this dataset?** It is a real corporate email network, and "email networks" are one of the social-network
types in Unit 5. It is also a well-known data-ethics case for Unit 6: private emails were made public by a
regulator.

**What exactly is a node and an edge?** A node is a person (149 after merging email aliases; 148 active). A
directed edge A→B means A emailed B, weighted by the number of emails. In the undirected graph, a tie is
*strong* if the emails go both ways (816 ties) and *weak* if they go one way only (972 ties).

**Why did 125,409 records become 34,374?**
- Every CC recipient also appears as BCC, so the BCC rows are copies.
- The same email is stored in several folders, which creates identical sender–recipient–time rows.
- Some people mailed themselves.
- 256 rows had impossible dates (1979).

That is 73% of the records removed.

**How did you test "is it a social network"?** With the Unit 5 locality test. For any person x with contacts y
and z, how likely is it that y and z are also connected? Observed: 0.42. A random graph with the same density
would give 0.16 (edges ÷ possible edges). Since 0.42 > 0.16, the graph shows social-network locality. It also holds
month by month.

**What is betweenness, and why use it?** It is the share of shortest paths between all pairs that pass through a
person. A high value means the person is a broker: information has to flow through them. Our top brokers are Sally
Beck (COO), an untitled employee (UNK-13) and John Lavorato (CEO, Enron America).

**How does Girvan–Newman work?**
1. Compute the betweenness of every edge.
2. Remove the edge with the highest betweenness; edges between communities carry the most shortest paths.
3. Recompute and repeat. The graph gradually splits apart.

We kept the split with the highest modularity (Q = 0.52), which gave 7 communities with at least 3 members.
Louvain gives a similar result (NMI 0.62).

**Why only strong ties for Girvan–Newman?** One-way emails (newsletters, single requests) blur the communities. Unit
5 defines strong ties as two-way communication, so we use those for the community structure.

**Why no hour-of-day chart?** The data showed the working day "starting" at 05:00 in 2000 but at 11:00 in late
2001. People did not suddenly start work six hours later. The timestamps recorded in the corpus drift over 2001.
Showing it would have produced a false "after-hours email doubled" finding.

**How is the network drawn in Tableau?** Tableau has no built-in network chart.
- In Python we computed a force-directed layout, giving each person x and y coordinates.
- Each tie is exported as two rows (start and end) with a path order.
- A *dual-axis* chart draws the ties as lines and the people as circles on top, sized by betweenness and coloured
  by community.

**Creator vs Viewer?**
- **Creator** (US$75 per user per month, Standard): connects to data, builds and publishes. It includes Desktop and
  Prep Builder.
- **Viewer** (US$15): can only view and interact (filters, highlights, parameters, comments). Viewers cannot edit,
  publish or download the full data.
- **For us:** the two of us need Creator; faculty and reviewers need Viewer. Every site needs at least one Creator.
- **Tableau Public:** free, but everything published there is public.

**Is it ethical to use this data?** It is legal and widely used in research. But the employees never consented,
and being "already public" does not remove the harm (Zimmer 2010). What we did:
- Used metadata only.
- Pseudonymised everyone except 10 officers who are public figures in the case.
- Reduced job titles to coarse role groups.
- Removed email addresses.
- Turned off downloads on Tableau Public.

The risk that remains is re-identification from network position (Narayanan & Shmatikov 2009).

**Limitations?**
- Only about 150 mailboxes are included, so this is not the whole company.
- 32% of job titles are missing.
- Volume reflects what was kept in the seized mailboxes.
- The timestamps drift.
- The Girvan–Newman result depends on using strong ties.
