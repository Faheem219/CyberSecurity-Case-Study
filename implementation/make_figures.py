"""Render report/slide charts from results/ into figures/ (blue and black only)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent
RES, FIG = ROOT / "results", ROOT / "figures"
NHI, BASE, INK, MUTED, GRID = "#2A4DA8", "#5A97EE", "#111111", "#4A4A4A", "#D9DEE8"

plt.rcParams.update({
    "font.family": "Times New Roman", "font.size": 11, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.grid.axis": "y",
    "legend.frameon": False, "savefig.dpi": 220, "savefig.bbox": "tight",
})

TACTIC_LABELS = {"discovery": "Discovery", "credential_access": "Credential\naccess",
                 "lateral_movement": "Lateral\nmovement", "collection": "Collection",
                 "exfiltration": "Exfiltration"}


def bar_labels(ax, bars, fmt="{:.0f}"):
    for b in bars:
        h = b.get_height()
        ax.annotate(fmt.format(h), (b.get_x() + b.get_width() / 2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=9.5, color=INK)


def fig_tactics(s):
    tactics = list(TACTIC_LABELS)
    base = [s["baseline"]["allowed_by_tactic_mean"][t] for t in tactics]
    nhi = [s["nhi"]["allowed_by_tactic_mean"][t] for t in tactics]
    x = range(len(tactics))
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    w = 0.36
    b1 = ax.bar([i - w / 2 - 0.01 for i in x], base, w, color=BASE, label="Baseline: shared API key",
                hatch="///", edgecolor="white", linewidth=0)
    b2 = ax.bar([i + w / 2 + 0.01 for i in x], nhi, w, color=NHI, label="NHI + scoped delegation")
    bar_labels(ax, b1, "{:.1f}")
    bar_labels(ax, b2, "{:.1f}")
    ax.set_xticks(list(x), [TACTIC_LABELS[t] for t in tactics])
    ax.set_ylabel("Misuse calls allowed per run (mean)")
    ax.set_ylim(0, max(base) * 1.18)
    ax.legend(loc="upper right")
    fig.savefig(FIG / "fig_tactics.png")
    plt.close(fig)


def fig_outcomes(s):
    b, n = s["baseline"], s["nhi"]
    panels = [
        ("Misuse calls blocked (%)", b["misuse_blocked_pct"], n["misuse_blocked_pct"], "{:.0f}%"),
        ("Prod/external resources\nexposed per run (mean)", b["blast_radius_mean"], n["blast_radius_mean"], "{:.1f}"),
        ("False alerts per run (mean)", b["false_alerts_mean"], n["false_alerts_mean"], "{:.2f}"),
        ("True alerts naming the\naccountable human (%)", b["alert_attribution_pct"], n["alert_attribution_pct"], "{:.0f}%"),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(9.6, 2.9))
    for ax, (title, bv, nv, fmt) in zip(axes, panels):
        bars = ax.bar([0, 1], [bv, nv], 0.62, color=[BASE, NHI], hatch=None)
        bars[0].set_hatch("///"); bars[0].set_edgecolor("white"); bars[0].set_linewidth(0)
        bar_labels(ax, bars, fmt)
        ax.set_title(title, fontsize=10.5, pad=8)
        ax.set_xticks([0, 1], ["Baseline", "NHI"])
        if "%" in fmt:
            ax.set_ylim(0, 118); ax.set_yticks([0, 25, 50, 75, 100])
        else:
            ax.set_ylim(0, (max(bv, nv) or 1) * 1.25)
        ax.tick_params(axis="y", labelsize=9)
    fig.tight_layout(w_pad=1.6)
    fig.savefig(FIG / "fig_outcomes.png")
    plt.close(fig)


def fig_timeline():
    show = json.loads((RES / "showcase_nhi.json").read_text())
    start = show["misuse_start"]
    recs = [r for r in show["records"]]
    end = max(r["t"] for r in recs if r["label"] == "misuse")
    lo, hi = start - 300, end + 300
    window = [r for r in recs if lo <= r["t"] <= hi]
    order = ["orch-1", "recon-1", "recon-2", "cred-1", "lat-1", "data-1",
             "ci-agent", "docs-agent", "ops-agent", "backup-agent"]
    lanes = [a for a in order if any(r["sub"] == a for r in window)]
    y = {a: i for i, a in enumerate(reversed(lanes))}
    to_min = lambda t: (t - start) / 60

    fig, ax = plt.subplots(figsize=(9.6, 3.9))
    ok = [r for r in window if r["allowed"]]
    no = [r for r in window if not r["allowed"]]
    ax.scatter([to_min(r["t"]) for r in ok], [y[r["sub"]] for r in ok], s=14, color=INK,
               label="Allowed call", zorder=3)
    ax.scatter([to_min(r["t"]) for r in no], [y[r["sub"]] for r in no], s=26, marker="x",
               color=NHI, linewidths=1.3, label="Denied by gateway", zorder=4)
    alerts = [a for a in show["alerts"] if lo <= a["t"] <= hi and a["actor"] in y]
    ax.scatter([to_min(a["t"]) for a in alerts], [y[a["actor"]] + 0.32 for a in alerts], s=34,
               marker="v", color=NHI, edgecolors="white", linewidths=0.6,
               label="IDS alert (R1/R2/R3)", zorder=5)
    if alerts:
        a0 = min(alerts, key=lambda a: a["t"])
        ax.annotate(f"first alert: {a0['rule'].replace('_', ' ')}, +{a0['t'] - start:.1f} s",
                    (to_min(a0["t"]), y[a0["actor"]] + 0.32), xytext=(18, 8),
                    textcoords="offset points", fontsize=9, color=INK,
                    arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=0.8))
    ax.set_yticks(list(y.values()), list(y.keys()))
    ax.set_xlabel("Minutes since the first misuse event (synthetic showcase run, seed 7)")
    ax.grid(axis="x", color=GRID)
    ax.set_ylim(-0.6, len(lanes) - 0.2)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.13), ncol=3, fontsize=9.5)
    fig.savefig(FIG / "fig_timeline.png")
    plt.close(fig)


def fig_architecture():
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(9.6, 3.9))
    ax.set_xlim(0, 100); ax.set_ylim(0, 42); ax.axis("off")

    def box(x, y, w, h, title, sub, fill="#EEF3FC"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2",
                                    facecolor=fill, edgecolor=NHI, linewidth=1.6))
        ax.text(x + w / 2, y + h - 2.6, title, ha="center", va="top", fontsize=11, weight="bold", color=INK)
        ax.text(x + w / 2, y + h - 7.4, sub, ha="center", va="top", fontsize=9, color=MUTED, linespacing=1.3)

    def arrow(x1, y1, x2, y2, label=""):
        ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", color=NHI, lw=1.6))
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 1.2, label, ha="center", va="bottom", fontsize=8.5, color=NHI)

    top = [(0.5, 15.5, "Human owner", "accountable\nprincipal"),
           (23.0, 15.5, "Agent (NHI)", "own identity,\nregistered owner"),
           (45.5, 21.0, "Scoped token", "scope · resource · TTL\ndepth · signed chain"),
           (73.5, 26.0, "Tool gateway", "verify signature, expiry,\nscope, resource → allow/deny")]
    for x, w, t, sub in top:
        box(x, 25, w, 15, t, sub)
    for (x1, w1, *_), (x2, *_), label in zip(top, top[1:], ["grant", "narrow", "call"]):
        arrow(x1 + w1 + 0.8, 32.5, x2 - 0.8, 32.5, label)

    box(73.5, 2, 26, 15, "Audit log", "every decision, SHA-256\nhash-chained")
    box(40.0, 2, 26, 15, "Identity-aware IDS", "R1 tempo · R2 probing\nR3 multi-tactic chain")
    box(6.5, 2, 26, 15, "Forensic view", "alerts + timeline:\nwho, for whom, what, when", fill="#FFFFFF")
    arrow(86.5, 24.2, 86.5, 17.8, "")
    arrow(72.7, 9.5, 66.8, 9.5, "stream")
    arrow(39.2, 9.5, 33.3, 9.5, "alert")
    fig.savefig(FIG / "fig_architecture.png")
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    s = json.loads((RES / "summary.json").read_text())
    fig_tactics(s)
    fig_outcomes(s)
    fig_timeline()
    fig_architecture()
    print("wrote", sorted(p.name for p in FIG.glob("*.png")))


if __name__ == "__main__":
    main()
