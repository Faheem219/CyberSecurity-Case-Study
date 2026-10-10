"""Render the findings charts used in the presentation (figures/*.png).

Usage: python3 analysis/make_figures.py      (run prepare_data.py first)
Palette: categorical slots validated with the dataviz validator (adjacent CVD dE >= 9.1); three light slots fall
below 3:1 contrast, so every multi-colour chart carries direct labels or a legend as secondary encoding.
"""
import json
from pathlib import Path

import matplotlib
import matplotlib.dates
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "data" / "processed"
FIG = ROOT / "figures"
S = json.loads((ROOT / "results" / "summary.json").read_text())

INK, INK2, MUTED, GRID, SURF = "#111418", "#4a5160", "#8a909c", "#e3e6ec", "#ffffff"
BLUE, ORANGE, GREY = "#2a78d6", "#eb6834", "#b9bec8"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 15, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 1, "axes.axisbelow": True,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "legend.frameon": False,
})


def save(fig, name):
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / f"{name}.png", dpi=110, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def community_colours(emp):
    order = sorted(emp.community.unique(), key=lambda c: int(c.split()[0][1:]))
    return {c: (CAT[i - 1] if (i := int(c.split()[0][1:])) > 0 else GREY) for c in order}


def timeline():
    d = pd.read_csv(P / "deliveries.csv", parse_dates=["sent_at"])
    wk = d.set_index("sent_at").resample("W-MON", label="left", closed="left").size()
    wk = wk["1999-06-01":"2002-03-31"]
    ev = pd.read_csv(P / "events.csv", parse_dates=["date"])
    fig, ax = plt.subplots(figsize=(14, 5.4))
    ax.axvspan(pd.Timestamp("2001-08-14"), pd.Timestamp("2001-12-02"), color="#eef3fc", zorder=0)
    ax.text(pd.Timestamp("2001-10-08"), wk.max() * 1.12, "Crisis window", ha="center", color=INK2, fontsize=13)
    ax.fill_between(wk.index, wk.values, color=BLUE, alpha=0.10, linewidth=0)
    ax.plot(wk.index, wk.values, color=BLUE, lw=2, solid_joinstyle="round")
    keep = {"Skilling becomes CEO": (0.86, "left"), "Skilling quits; Lay back as CEO": (0.62, "right"),
            "Q3 loss of $618M announced": (1.0, "right"), "Chapter 11 bankruptcy filing": (0.80, "left"),
            "California rolling blackouts": (0.95, "right")}
    for _, r in ev.iterrows():
        if r.event not in keep:
            continue
        h, side = keep[r.event]
        y = wk.max() * h
        ax.plot([r.date, r.date], [0, y], color=MUTED, lw=1)
        ax.plot(r.date, y, "o", ms=7, color=INK, mec=SURF, mew=2)
        off = pd.Timedelta(days=9) * (1 if side == "left" else -1)
        ax.text(r.date + off, y, r.event, ha=side, va="center", fontsize=12.5, color=INK)
    ax.set_ylabel("Deliveries per week")
    ax.set_ylim(0, wk.max() * 1.2)
    ax.margins(x=0.01)
    ax.grid(axis="x", visible=False)
    save(fig, "fig_timeline")


def network():
    emp = pd.read_csv(P / "employees.csv")
    net = pd.read_csv(P / "network_paths.csv")
    col = community_colours(emp)
    pos = emp.set_index("display_name")[["x", "y"]]
    fig, ax = plt.subplots(figsize=(10.5, 8.4))
    ties = net[net.row_type == "Tie"]
    for pid, t in ties.groupby("path_id", sort=False):
        if t.tie_type.iloc[0].startswith("Weak"):
            continue
        a, b = t.display_name.iloc[0], t.display_name.iloc[1]
        same = t.community_link.iloc[0] == "Within community"
        c = col[t.community.iloc[0]] if same else "#9aa0aa"
        ax.plot(pos.loc[[a, b], "x"], pos.loc[[a, b], "y"], color=c, lw=0.7, alpha=0.30 if same else 0.18, zorder=1)
    size = 40 + 2600 * np.sqrt(emp.betweenness / emp.betweenness.max())
    ax.scatter(emp.x, emp.y, s=size, c=emp.community.map(col), edgecolors=SURF, linewidths=1.8, zorder=2)
    for c, sub in emp.groupby("community"):                       # direct labels = secondary encoding
        if c.startswith("C0") or len(sub) < 5:
            continue
        ax.text(sub.x.median(), sub.y.median(), c.split(" ")[0], ha="center", va="center", fontsize=14,
                color=INK, fontweight="bold", zorder=6,
                bbox=dict(boxstyle="round,pad=0.25", fc=SURF, ec=GRID, alpha=0.9))
    handles = [plt.Line2D([], [], marker="o", ls="", ms=10, mfc=v, mec=SURF, label=k) for k, v in col.items()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2, fontsize=13,
              labelcolor=INK)
    ax.set_xticks([]), ax.set_yticks([])
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    save(fig, "fig_network")


def locality():
    m = pd.read_csv(P / "monthly_network.csv", parse_dates=["month"])
    m = m[m.reliable.eq("Yes")]
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.plot(m.month, m.p_closed, color=BLUE, lw=2, label="P(y-z tie | x-y and x-z ties)  - observed")
    ax.plot(m.month, m.density, color=ORANGE, lw=2, label="Edge density  - expected if ties were random")
    for ser, c in ((m.p_closed, BLUE), (m.density, ORANGE)):
        ax.plot(m.month.iloc[-1], ser.iloc[-1], "o", ms=8, color=c, mec=SURF, mew=2)
        ax.text(m.month.iloc[-1] + pd.Timedelta(days=12), ser.iloc[-1], f"{ser.iloc[-1]:.2f}", va="center",
                color=INK, fontsize=13)
    ax.set_ylim(0, 0.6)
    ax.set_ylabel("Probability")
    ax.legend(loc="upper left", fontsize=13, labelcolor=INK)
    ax.grid(axis="x", visible=False)
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(bymonth=(1, 7)))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %Y"))
    save(fig, "fig_locality")


def brokers():
    emp = pd.read_csv(P / "employees.csv").nlargest(10, "betweenness").iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 5.6))
    role = emp.role_group.str.split(" ", n=1).str[1]
    c = np.where(role.eq("Executive"), BLUE, GREY)
    ax.barh(emp.display_name + "  ·  " + role.str.replace(" / Specialist", ""), emp.betweenness,
            height=0.55, color=c)
    for y, v in enumerate(emp.betweenness):
        ax.text(v + 0.0015, y, f"{v:.3f}", va="center", fontsize=12.5, color=INK)
    ax.set_xlabel("Betweenness centrality (share of shortest paths passing through the person)")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=BLUE, label="Executive (named officer)"),
                       plt.Rectangle((0, 0), 1, 1, color=GREY, label="Other roles (pseudonymised)")],
              loc="lower right", fontsize=12.5, labelcolor=INK)
    ax.set_xlim(0, emp.betweenness.max() * 1.18)
    save(fig, "fig_brokers")


def periods():
    per = S["periods"]
    names = ["Pre-crisis\n(Jan 99-Aug 01)", "Crisis\n(Aug-Dec 01)", "Post-bankruptcy\n(Dec 01-Jun 02)"]
    keys = list(per)
    panels = [("Deliveries per week", [per[k]["deliveries_per_week"] for k in keys], "{:.0f}"),
              ("Share of traffic involving an executive", [per[k]["executive_share_of_traffic"] * 100 for k in keys],
               "{:.0f}%"),
              ("Broadcast messages (5+ recipients)", [per[k]["broadcast_share"] * 100 for k in keys], "{:.1f}%")]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.9))
    for ax, (title, vals, fmt) in zip(axes, panels):
        ax.bar(names, vals, width=0.5, color=BLUE)
        for x, v in enumerate(vals):
            ax.text(x, v * 1.02, fmt.format(v), ha="center", va="bottom", fontsize=15, color=INK, fontweight="bold")
        ax.set_title(title, fontsize=15, color=INK, loc="left")
        ax.set_ylim(0, max(vals) * 1.22)
        ax.grid(axis="x", visible=False)
        ax.tick_params(axis="x", labelsize=12.5)
    fig.tight_layout(w_pad=3)
    save(fig, "fig_periods")


def clock():
    c = pd.read_csv(P / "clock_check.csv")
    c["month"] = pd.to_datetime(c.month)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.axvspan(pd.Timestamp("2001-04-01"), pd.Timestamp("2001-09-01"), color="#eef3fc", zorder=0)
    ax.text(pd.Timestamp("2001-06-15"), 13.2, "clock drifts ~5 h", ha="center", color=INK2, fontsize=13)
    ax.plot(c.month, c.start_hour_p10, color=BLUE, lw=2, marker="o", ms=6, mec=SURF, mew=1.5)
    ax.set_ylim(0, 14)
    ax.set_yticks(range(0, 15, 2), [f"{h:02d}:00" for h in range(0, 15, 2)])
    ax.set_ylabel("Start of the working day\n(10th-percentile hour)")
    ax.grid(axis="x", visible=False)
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(bymonth=(1, 7)))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %Y"))
    save(fig, "fig_clock")


if __name__ == "__main__":
    for f in (timeline, network, locality, brokers, periods, clock):
        f()
    print("figures ->", sorted(p.name for p in FIG.glob("*.png")))
