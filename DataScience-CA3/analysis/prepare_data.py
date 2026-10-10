"""Clean the Enron email network and compute the Unit-5 network metrics for the Tableau dashboard.

Input : data/raw/enron.rda - the `enron` igraph object from the igraphdata R package
        (Johns Hopkins / Priebe et al. version of the Enron corpus made public by FERC and the U.S. DoJ).
Output: data/processed/*.csv (Tableau data sources) and results/summary.json (numbers quoted in the slides).

Usage : python3 analysis/prepare_data.py        (needs: pip install rdata pandas numpy networkx scikit-learn)

Privacy rules applied here, before anything reaches Tableau (see README, "Ethics"):
  * only metadata is used (who emailed whom, when); topic labels derived from message bodies are dropped;
  * only the ten company officers (CEO / President / COO / CFO titles) keep their real names; everyone else
    becomes a role pseudonym such as VP-03, and the detailed job title is reduced to a coarse role group;
  * email addresses never leave this script.
"""
import json
import warnings
from itertools import combinations
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import rdata
from networkx.algorithms.community import girvan_newman, louvain_communities, modularity
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

warnings.filterwarnings("ignore", message="Missing constructor")

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "enron.rda"
OUT = ROOT / "data" / "processed"
RES = ROOT / "results"
SEED = 42

WINDOW = ("1999-01-01", "2002-07-01")          # 1979 stamps are known-bad; 1998 has only 82 rows
CRISIS_START, BANKRUPTCY = pd.Timestamp("2001-08-14"), pd.Timestamp("2001-12-02")

# Seniority tiers derived from the free-text "Note" (job title) attribute.
ROLE_GROUPS = [  # (group, rank, pseudonym prefix)
    ("Executive", 1, "EXE"),
    ("Vice President", 2, "VP"),
    ("Director / MD", 3, "DIR"),
    ("Manager", 4, "MGR"),
    ("Trader", 5, "TRD"),
    ("Employee / Specialist", 5, "EMP"),
    ("Unknown role", 6, "UNK"),
]
ROLE_LABEL = {g: f"{i} {g}" for i, (g, _, _) in enumerate(ROLE_GROUPS, 1)}   # "1 Executive" sorts by seniority
RANK = {g: r for g, r, _ in ROLE_GROUPS}
PREFIX = {g: p for g, _, p in ROLE_GROUPS}

EVENTS = [  # well-documented public milestones of the Enron collapse
    ("2000-08-23", "Share price peaks near $90", "Market"),
    ("2001-01-17", "California rolling blackouts", "Market"),
    ("2001-02-12", "Skilling becomes CEO", "CEO"),
    ("2001-08-14", "Skilling quits; Lay back as CEO", "CEO"),
    ("2001-10-16", "Q3 loss of $618M announced", "Crisis"),
    ("2001-10-22", "SEC inquiry disclosed", "Crisis"),
    ("2001-11-08", "Earnings restated back to 1997", "Crisis"),
    ("2001-11-28", "Dynegy deal fails; junk rating", "Crisis"),
    ("2001-12-02", "Chapter 11 bankruptcy filing", "Crisis"),
    ("2002-01-23", "Lay resigns as Chairman and CEO", "CEO"),
]


def role_group(note: str) -> str:
    n = note.lower()
    if n == "na":
        return "Unknown role"
    if n.startswith(("ceo", "president")) or "chief operating officer" in n or "chief financial officer" in n:
        return "Executive"
    if n.startswith("vice president"):
        return "Vice President"
    if n.startswith(("director", "managing director")):
        return "Director / MD"
    if n.startswith("manager"):
        return "Manager"
    if n.startswith("trader"):
        return "Trader"
    return "Employee / Specialist"          # "Employee, ..." and "In House Lawyer"


def load_raw():
    g = rdata.conversion.convert(rdata.parser.parse_file(RAW))["enron"]
    nodes = pd.DataFrame({k: np.asarray(v) for k, v in g[8][2].items()})
    edges = pd.DataFrame({k: np.asarray(v) for k, v in g[8][3].items()})
    edges["src"], edges["dst"] = g[2].astype(int), g[3].astype(int)   # igraph stores 0-based vertex ids
    edges["Time"] = pd.to_datetime(edges["Time"])
    return nodes, edges


def clean(nodes, edges, log):
    log.append(("Raw sender-recipient records", len(edges)))
    e = edges[(edges.Time >= WINDOW[0]) & (edges.Time < WINDOW[1])]
    log.append(("Outside Jan 1999 - Jun 2002 removed (bogus 1979 stamps)", len(e)))
    e = e[e.Reciptype != "bcc"]
    log.append(("bcc rows removed (every one duplicates a cc row)", len(e)))

    # Entity resolution: 184 addresses belong to fewer people (e.g. three aliases for one lawyer).
    nodes = nodes.copy()
    nodes["person"] = np.where(nodes.Name != "NA", nodes.Name, nodes.Email)
    people = nodes.drop_duplicates("person").reset_index(drop=True)
    pid = {p: i for i, p in enumerate(people.person)}
    addr_to_pid = nodes.person.map(pid).to_numpy()
    e = e.assign(s=addr_to_pid[e.src.to_numpy()], d=addr_to_pid[e.dst.to_numpy()])
    e = e[e.s != e.d]
    log.append(("Self-addressed copies removed (after merging aliases)", len(e)))

    # The same message is stored in several folders of each mailbox: keep one row per sender-recipient-second.
    e = e.sort_values("Reciptype", key=lambda c: c.map({"to": 0, "cc": 1}), kind="stable")
    e = e.drop_duplicates(["s", "d", "Time"]).sort_values(["Time", "s", "d"]).reset_index(drop=True)
    log.append(("Duplicate folder copies removed = unique deliveries", len(e)))

    people["pid"] = range(len(people))
    people["role_group"] = people.Note.map(role_group)
    people["n_addresses"] = people.person.map(nodes.person.value_counts())
    return people, e


def pseudonymise(people, e):
    sent = e.groupby("s").size()
    recv = e.groupby("d").size()
    people["volume"] = people.pid.map(sent).fillna(0) + people.pid.map(recv).fillna(0)
    people["named_officer"] = people.role_group.eq("Executive")
    keys = {}
    for grp, sub in people.sort_values("volume", ascending=False).groupby("role_group", sort=False):
        for i, pid in enumerate(sub.pid, 1):
            keys[pid] = f"{PREFIX[grp]}-{i:02d}"
    people["employee_key"] = people.pid.map(keys)
    people["display_name"] = np.where(people.named_officer, people.Name, people.employee_key)
    return people


def build_graphs(people, e):
    gd = nx.DiGraph()
    gd.add_nodes_from(people.pid)
    for (s, d), w in e.groupby(["s", "d"]).size().items():
        gd.add_edge(s, d, weight=int(w))
    gu = nx.Graph()
    gu.add_nodes_from(people.pid)
    for s, d, w in gd.edges(data="weight"):
        if gu.has_edge(s, d):
            gu[s][d]["weight"] += w
            gu[s][d]["strong"] = True
        else:
            gu.add_edge(s, d, weight=w, strong=False)
    active = [n for n in gu if gu.degree(n) > 0]
    gu = gu.subgraph(active).copy()
    gd = gd.subgraph(active).copy()
    gs = nx.Graph()
    gs.add_nodes_from(gu)
    gs.add_edges_from((a, b, d) for a, b, d in gu.edges(data=True) if d["strong"])
    return gd, gu, gs


def locality(g):
    """Unit-5 locality test: P(y-z edge | x-y and x-z edges) vs. the edge density expected at random."""
    n, m = g.number_of_nodes(), g.number_of_edges()
    tri = sum(nx.triangles(g).values()) // 3
    wedges = sum(d * (d - 1) // 2 for _, d in g.degree())
    possible = n * (n - 1) // 2
    p_closed = 3 * tri / wedges if wedges else np.nan
    return {"nodes": n, "edges": m, "possible_edges": possible, "triangles": tri, "wedges": wedges,
            "p_closed": p_closed, "density": m / possible if possible else np.nan,
            "expected_small": (m - 2) / (possible - 2) if possible > 2 else np.nan}


def girvan_newman_best(gs):
    """Girvan-Newman (edge betweenness) on the strong-tie graph; keep the split with the highest modularity."""
    core = gs.subgraph([n for n in gs if gs.degree(n) > 0]).copy()
    best, best_q, history = None, -1, []
    for k, parts in enumerate(girvan_newman(core), start=2):
        q = modularity(core, parts)
        history.append((len(parts), q))
        if q > best_q:
            best, best_q = [set(p) for p in parts], q
        if len(parts) >= 40:
            break
    return best, best_q, history, core


def community_names(people, comm_of, contacts):
    """Name each community from the job titles inside it (titles are used here only; they are not exported)."""
    names = {}
    for c in sorted(set(comm_of.values())):
        mem = people[people.pid.map(comm_of).eq(c)]
        titles = " | ".join(mem.Note.str.lower())
        hub = mem.assign(k=mem.pid.map(contacts)).sort_values("k").iloc[-1]
        if (mem.role_group == "Executive").sum() >= 5:
            names[c] = "Leadership core"
        elif "pipeline" in titles:
            names[c] = "Gas pipeline & regulatory"
        elif "real time trading" in titles:
            names[c] = "Real-time trading desk"
        elif "logistics" in titles and "trader" in titles:
            names[c] = "Trading & logistics desk"
        elif "logistics" in titles:
            names[c] = "Logistics & regional trading"
        else:
            names[c] = f"Staff cluster around {hub.display_name}"
        if list(names.values()).count(names[c]) > 1:          # keep labels unique
            names[c] += f" ({hub.display_name})"
    return names


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    RES.mkdir(parents=True, exist_ok=True)
    log = []
    nodes, edges = load_raw()
    people, e = clean(nodes, edges, log)
    people = pseudonymise(people, e)

    # Times are kept exactly as stored in the corpus. Hour-of-day is NOT analysed: the recording clock drifts by
    # ~5 h between May and Aug 2001 (see clock_check in summary.json), so time-of-day comparisons are unreliable.
    e["sent_at"] = e.Time
    e["message_id"] = e.groupby(["s", "Time"]).ngroup() + 1
    e["n_recipients"] = e.groupby("message_id").d.transform("size")
    e["period"] = np.select([e.Time < CRISIS_START, e.Time <= BANKRUPTCY],
                            ["1 Pre-crisis", "2 Crisis (Aug-Dec 2001)"], "3 Post-bankruptcy")

    gd, gu, gs = build_graphs(people, e)
    act = people[people.pid.isin(gu.nodes)].copy()

    # ---- node metrics ------------------------------------------------------------------------------------
    btw = nx.betweenness_centrality(gu, normalized=True)
    pr = nx.pagerank(gd, weight="weight", alpha=0.85)
    clu = nx.clustering(gu)
    m = act.set_index("pid")
    m["emails_sent"] = e.groupby("s").size()
    m["emails_received"] = e.groupby("d").size()
    m = m.fillna({"emails_sent": 0, "emails_received": 0})
    m["out_contacts"] = pd.Series(dict(gd.out_degree()))
    m["in_contacts"] = pd.Series(dict(gd.in_degree()))
    m["contacts"] = pd.Series(dict(gu.degree()))
    m["strong_ties"] = pd.Series(dict(gs.degree()))
    m["weak_ties"] = m.contacts - m.strong_ties
    m["betweenness"] = pd.Series(btw)
    m["pagerank"] = pd.Series(pr)
    m["clustering"] = pd.Series(clu)
    m["crisis_share"] = e[e.period.str.startswith("2")].groupby("s").size() / m.emails_sent

    # ---- communities ---------------------------------------------------------------------------------------
    gn_parts, gn_q, gn_hist, core = girvan_newman_best(gs)
    gn_parts = sorted(gn_parts, key=len, reverse=True)
    comm_of = {}
    big = [p for p in gn_parts if len(p) >= 3]
    for i, p in enumerate(big, 1):
        for n in p:
            comm_of[n] = i
    # Girvan-Newman peels leaves off as 1-2 person splits; attach each such person to the community they
    # exchange the most email with (all ties), and leave anyone without such ties unassigned (0).
    leftovers = [n for n in gu if n not in comm_of]
    attached = 0
    for n in leftovers:
        w = {}
        for nb, dat in gu[n].items():
            if nb in comm_of:
                w[comm_of[nb]] = w.get(comm_of[nb], 0) + dat["weight"]
        comm_of[n] = max(w, key=w.get) if w else 0
        attached += bool(w)
    lv = louvain_communities(gu, weight="weight", seed=SEED, resolution=1.0)
    lv_of = {n: i for i, p in enumerate(sorted(lv, key=len, reverse=True), 1) for n in p}
    nodes_cmp = [n for n in gu if comm_of[n] > 0]
    ari = adjusted_rand_score([comm_of[n] for n in nodes_cmp], [lv_of[n] for n in nodes_cmp])
    nmi = normalized_mutual_info_score([comm_of[n] for n in nodes_cmp], [lv_of[n] for n in nodes_cmp])
    act["display_name"] = act.employee_key.where(~act.named_officer, act.Name)
    names = community_names(act, {n: c for n, c in comm_of.items() if c > 0}, dict(gu.degree()))
    def comm_label(c):
        return "C0 Unassigned" if c == 0 else f"C{c} {names[c]}"
    m["community"] = pd.Series({n: comm_label(c) for n, c in comm_of.items()})
    m["community_louvain"] = pd.Series({n: f"L{c}" for n, c in lv_of.items()})

    # ---- layout for the node-link diagram -------------------------------------------------------------
    lay_g = nx.Graph()
    lay_g.add_nodes_from(gu)
    # Community-weighted force layout: ties inside a community pull 3x harder, ties across pull 0.3x,
    # so the communities found above separate visually (a drawing choice only; metrics are unaffected).
    lay_g.add_edges_from((a, b, {"w": np.log1p(d["weight"]) * (3.0 if comm_of[a] == comm_of[b] else 0.3)})
                         for a, b, d in gu.edges(data=True))
    pos = nx.spring_layout(lay_g, weight="w", seed=SEED, k=0.35, iterations=500)
    lay_nodes = list(gu)
    xy = np.array([pos[n] for n in lay_nodes])
    xy = (xy - xy.min(0)) / (xy.max(0) - xy.min(0)) * 100
    # Overlap removal (drawing only): the leadership core collapses into one blob in which circles and the broker
    # labels sit on top of each other. Push pairs apart until they clear a minimum gap that grows with circle size;
    # the six biggest brokers keep extra room for their name labels. Relative positions are otherwise kept.
    btw = m.loc[lay_nodes, "betweenness"].to_numpy()
    r = 4.0 * np.sqrt(btw / btw.max())
    top6 = np.zeros(len(lay_nodes), bool)
    top6[np.argsort(-btw)[:6]] = True
    gap = 2.4 + r[:, None] + r[None, :]
    gap = np.where(top6[:, None] & top6[None, :], np.maximum(gap, 11.0), gap)
    np.fill_diagonal(gap, 0)
    for _ in range(400):
        d = xy[:, None, :] - xy[None, :, :]
        dist = np.hypot(d[..., 0], d[..., 1]) + np.eye(len(lay_nodes))
        push = np.clip(gap - dist, 0, None) / 2
        if push.max() < 0.01:
            break
        xy += (d / dist[..., None] * push[..., None]).sum(1) * 0.5
    xy = (xy - xy.min(0)) / (xy.max(0) - xy.min(0)) * 100
    for n, (x, y) in zip(lay_nodes, xy):
        m.loc[n, "x"], m.loc[n, "y"] = round(x, 3), round(y, 3)

    m["role_rank"] = m.role_group.map(RANK)
    emp_cols = ["employee_key", "display_name", "named_officer", "role_group", "role_rank", "community",
                "community_louvain", "emails_sent", "emails_received", "out_contacts", "in_contacts", "contacts",
                "strong_ties", "weak_ties", "betweenness", "pagerank", "clustering", "crisis_share", "x", "y"]
    emp = m[emp_cols].copy()
    for metric in ("betweenness", "pagerank", "contacts", "emails_sent"):
        emp[f"rank_{metric}"] = emp[metric].rank(ascending=False, method="first").astype(int)
    for c in ("emails_sent", "emails_received"):
        emp[c] = emp[c].astype(int)
    for c in ("betweenness", "pagerank", "clustering", "crisis_share"):
        emp[c] = emp[c].round(5)
    emp_out = emp.assign(role_group=emp.role_group.map(ROLE_LABEL))
    emp_out.sort_values("betweenness", ascending=False).to_csv(OUT / "employees.csv", index=False)

    # ---- deliveries (one row per sender -> recipient copy of a message) ----------------------------------
    info = emp[["display_name", "role_group", "role_rank", "community"]]
    s_info, r_info = info.add_prefix("sender_"), info.add_prefix("recipient_")
    d = e.join(s_info, on="s").join(r_info, on="d")
    d["direction"] = np.select([d.sender_role_rank > d.recipient_role_rank,
                                d.sender_role_rank < d.recipient_role_rank], ["Upward", "Downward"], "Peer")
    d.loc[(d.sender_role_rank == 6) | (d.recipient_role_rank == 6), "direction"] = "Unknown"
    d["same_community"] = np.where(d.sender_community == d.recipient_community, "Within community", "Across communities")
    deliveries = pd.DataFrame({
        "delivery_id": np.arange(1, len(d) + 1),
        "message_id": d.message_id,
        "sent_at": d.sent_at.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "sender": d.sender_display_name, "sender_role": d.sender_role_group.map(ROLE_LABEL),
        "sender_community": d.sender_community,
        "recipient": d.recipient_display_name, "recipient_role": d.recipient_role_group.map(ROLE_LABEL),
        "recipient_community": d.recipient_community,
        "recipient_type": d.Reciptype.str.upper(),
        "n_recipients": d.n_recipients,
        "period": d.period, "direction": d.direction, "community_link": d.same_community,
    })
    deliveries.to_csv(OUT / "deliveries.csv", index=False)

    # ---- node-link diagram rows (two path points per tie + one anchor row per person) ---------------------
    rows = []
    for k, (a, b, dat) in enumerate(sorted(gu.edges(data=True), key=lambda t: -t[2]["weight"]), 1):
        tie = "Strong (two-way)" if dat["strong"] else "Weak (one-way)"
        link = "Within community" if comm_of[a] == comm_of[b] and comm_of[a] > 0 else "Across communities"
        for order, n in ((1, a), (2, b)):
            rows.append((f"T{k:04d}", order, "Tie", emp.loc[n, "display_name"], emp.loc[n, "x"], emp.loc[n, "y"],
                         dat["weight"], tie, link, emp.loc[n, "community"], ROLE_LABEL[emp.loc[n, "role_group"]],
                         emp.loc[n, "betweenness"], emp.loc[n, "contacts"], emp.loc[n, "rank_betweenness"]))
    for n in gu:
        rows.append((f"N-{emp.loc[n, 'employee_key']}", 1, "Person", emp.loc[n, "display_name"], emp.loc[n, "x"],
                     emp.loc[n, "y"], 0, "None", "None", emp.loc[n, "community"], ROLE_LABEL[emp.loc[n, "role_group"]],
                     emp.loc[n, "betweenness"], emp.loc[n, "contacts"], emp.loc[n, "rank_betweenness"]))
    net = pd.DataFrame(rows, columns=["path_id", "path_order", "row_type", "display_name", "x", "y", "tie_emails",
                                      "tie_type", "community_link", "community", "role_group", "betweenness",
                                      "contacts", "rank_betweenness"])
    net.to_csv(OUT / "network_paths.csv", index=False)

    # ---- monthly network snapshots (locality test over time) ---------------------------------------------
    exe = set(people.pid[people.role_group.eq("Executive")])
    monthly = []
    for mon, sub in e.groupby(e.sent_at.dt.to_period("M")):
        gm = nx.Graph()
        gm.add_edges_from(zip(sub.s, sub.d))
        loc = locality(gm)
        pairs = set(zip(sub.s, sub.d))
        monthly.append({
            "month": mon.start_time.strftime("%Y-%m-%d"), "deliveries": len(sub),
            "messages": sub.message_id.nunique(), "active_people": loc["nodes"], "ties": loc["edges"],
            "density": round(loc["density"], 5), "p_closed": round(loc["p_closed"], 5),
            "locality_ratio": round(loc["p_closed"] / loc["density"], 3) if loc["density"] else None,
            "reciprocity": round(sum((b, a) in pairs for a, b in pairs) / len(pairs), 4),
            "executive_share": round((sub.s.isin(exe) | sub.d.isin(exe)).mean(), 4),
            "reliable": "Yes" if loc["nodes"] >= 50 else "No (fewer than 50 active people)",
        })
    monthly = pd.DataFrame(monthly)
    monthly.to_csv(OUT / "monthly_network.csv", index=False)
    long = monthly.melt(id_vars=["month", "reliable", "active_people"], value_vars=["p_closed", "density"],
                        var_name="metric", value_name="value")
    long["metric"] = long.metric.map({"p_closed": "Observed: P(friend-of-friend tie)",
                                      "density": "Expected at random: edge density"})
    long.to_csv(OUT / "monthly_locality_long.csv", index=False)

    ev = pd.DataFrame(EVENTS, columns=["date", "event", "category"])
    ev.insert(0, "event_no", range(1, len(ev) + 1))
    ev["date_label"] = pd.to_datetime(ev.date).dt.strftime("%d %b %Y")
    ev.to_csv(OUT / "events.csv", index=False)

    # ---- period comparison (for the findings slide) -------------------------------------------------------
    periods = {}
    for per, sub in e.groupby("period"):
        gp = nx.Graph()
        gp.add_edges_from(zip(sub.s, sub.d))
        days = (sub.Time.max() - sub.Time.min()).days + 1
        lc = max(nx.connected_components(gp), key=len)
        bt = nx.betweenness_centrality(gp)
        top = sorted(bt, key=bt.get, reverse=True)[:5]
        n_p = gp.number_of_nodes()
        centralisation = sum(max(bt.values()) - v for v in bt.values()) / (n_p - 1)   # Freeman, normalised scores
        periods[per] = {
            "days": days, "deliveries": len(sub), "deliveries_per_week": round(len(sub) / days * 7, 1),
            "active_people": gp.number_of_nodes(), **{k: round(v, 4) for k, v in locality(gp).items()},
            "avg_shortest_path": round(nx.average_shortest_path_length(gp.subgraph(lc)), 3),
            "executive_share_of_traffic": round((sub.s.isin(exe) | sub.d.isin(exe)).mean(), 4),
            "broadcast_share": round((sub.drop_duplicates("message_id").n_recipients >= 5).mean(), 4),
            "cross_community_share": round((deliveries.loc[sub.index, "community_link"] == "Across communities").mean(), 4),
            "betweenness_centralisation": round(centralisation, 4),
            "executives_in_top5_brokers": sum(n in exe for n in top),
            "top_brokers": [emp.loc[n, "display_name"] + f" ({emp.loc[n, 'role_group']})" for n in top],
        }

    # ---- clock check: weekday start-of-day hour (10th percentile) per month exposes the recording-clock drift --
    msgs = e.drop_duplicates("message_id")
    msgs = msgs[msgs.Time.dt.dayofweek < 5]
    clock = msgs.groupby(msgs.Time.dt.to_period("M")).Time.agg(
        n="size", start_hour_p10=lambda t: float(np.percentile(t.dt.hour, 10)), median_hour="median")
    clock = clock[clock.n >= 100]
    clock["median_hour"] = msgs.groupby(msgs.Time.dt.to_period("M")).Time.apply(lambda t: float(t.dt.hour.median()))
    clock.index = clock.index.astype(str)
    clock.reset_index(names="month").to_csv(OUT / "clock_check.csv", index=False)

    # ---- summary -------------------------------------------------------------------------------------------
    whole = locality(gu)
    dirpairs = set(gd.edges())
    comm_sizes = emp.community.value_counts().to_dict()
    top10 = emp.sort_values("betweenness", ascending=False).head(10)
    summary = {
        "clock_check": {m: r["start_hour_p10"] for m, r in clock.iterrows()},
        "source": "igraphdata::enron (JHU, Priebe et al. 2005) - Enron corpus released by FERC/DoJ",
        "cleaning_log": log,
        "addresses": int(len(nodes)), "people": int(len(people)), "active_people": int(gu.number_of_nodes()),
        "messages": int(e.message_id.nunique()), "deliveries": int(len(e)),
        "date_range": [e.sent_at.min().strftime("%Y-%m-%d"), e.sent_at.max().strftime("%Y-%m-%d")],
        "peak_month": monthly.loc[monthly.deliveries.idxmax()].to_dict(),
        "ties_undirected": whole["edges"], "directed_pairs": len(dirpairs),
        "strong_ties": gs.number_of_edges(), "weak_ties": whole["edges"] - gs.number_of_edges(),
        "reciprocity": round(sum((b, a) in dirpairs for a, b in dirpairs) / len(dirpairs), 4),
        "locality_whole": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in whole.items()},
        "avg_shortest_path": round(nx.average_shortest_path_length(gu.subgraph(max(nx.connected_components(gu), key=len))), 3),
        "diameter": nx.diameter(gu.subgraph(max(nx.connected_components(gu), key=len))),
        "girvan_newman": {"graph": "strong ties", "nodes": core.number_of_nodes(), "edges": core.number_of_edges(),
                          "best_modularity": round(gn_q, 4), "n_parts_at_best": len(gn_parts),
                          "communities_ge3": len(big), "leftovers": len(leftovers), "leftovers_attached": attached,
                          "history_head": [(k, round(q, 4)) for k, q in gn_hist[:25]]},
        "louvain": {"n": len(lv), "modularity_weighted_full": round(modularity(gu, lv, weight="weight"), 4)},
        "gn_vs_louvain": {"ARI": round(ari, 3), "NMI": round(nmi, 3)},
        "community_sizes": comm_sizes,
        "top10_betweenness": top10[["display_name", "role_group", "community", "betweenness", "contacts"]].to_dict("records"),
        "role_group_counts": emp.role_group.value_counts().to_dict(),
        "direction_share": deliveries[deliveries.direction != "Unknown"].direction.value_counts(normalize=True).round(4).to_dict(),
        "cross_community_share": round((deliveries.community_link == "Across communities").mean(), 4),
        "recipient_type_share": deliveries.recipient_type.value_counts(normalize=True).round(4).to_dict(),
        "periods": periods,
        "executive_traffic": {
            "sent": int(emp[emp.role_group.eq("Executive")].emails_sent.sum()),
            "received": int(emp[emp.role_group.eq("Executive")].emails_received.sum())},
    }
    (RES / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps({k: summary[k] for k in ("cleaning_log", "people", "active_people", "messages", "deliveries",
                                              "strong_ties", "weak_ties", "reciprocity", "locality_whole",
                                              "girvan_newman", "louvain", "gn_vs_louvain", "community_sizes")},
                     indent=1, default=str))


if __name__ == "__main__":
    main()
