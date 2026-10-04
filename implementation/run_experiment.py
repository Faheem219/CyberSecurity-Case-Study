"""Run the BASELINE (shared key) vs NHI (scoped delegation) comparison.

Usage:  python3 run_experiment.py [--runs 50]
Writes: results/summary.json, results/runs.csv, results/showcase_nhi.json,
        results/showcase_baseline.json
"""
import argparse
import csv
import json
import random
import statistics
import time
from collections import Counter
from pathlib import Path

from nhi_lab.audit import AuditLog
from nhi_lab.gateway import ToolGateway
from nhi_lab.identity import (DelegationAuthority, Identity, IdentityRegistry,
                              SharedKeyAuthority, TokenError)
from nhi_lab.ids import IdentityAwareIDS
from nhi_lab.workload import (BENIGN_AGENTS, ENGAGEMENT, HORIZON, HUMANS, ORCHESTRATOR,
                              SUB_AGENTS, benign_events, misuse_events)

OUT = Path(__file__).parent / "results"
TACTICS = ["discovery", "credential_access", "lateral_movement", "collection", "exfiltration"]
OPERATOR = "op-x"


def build_registry():
    reg = IdentityRegistry()
    for human, role in HUMANS.items():
        reg.register(Identity(human, "human", human, role))
    for agent, (owner, purpose, _, _) in BENIGN_AGENTS.items():
        reg.register(Identity(agent, "agent", owner, purpose))
    for agent in [ORCHESTRATOR] + SUB_AGENTS:
        reg.register(Identity(agent, "agent", OPERATOR, "security testing (claimed)"))
    return reg


def simulate(mode, seed):
    rng = random.Random(seed)
    misuse_start = rng.uniform(900, HORIZON - 5400)
    events = benign_events(rng) + misuse_events(rng, misuse_start)
    events.sort(key=lambda e: e["t"])

    reg, audit = build_registry(), AuditLog()
    if mode == "baseline":
        auth = SharedKeyAuthority()
        tokens = {a: auth.key for a in list(BENIGN_AGENTS) + [ORCHESTRATOR] + SUB_AGENTS}
    else:
        auth = DelegationAuthority(reg)
        tokens = {a: auth.issue_root(owner, a, scopes, res, HORIZON + 3600, 0, 0.0, purpose)
                  for a, (owner, purpose, scopes, res) in BENIGN_AGENTS.items()}
        tokens[ORCHESTRATOR] = auth.issue_root(
            OPERATOR, ORCHESTRATOR, ENGAGEMENT["scopes"], ENGAGEMENT["res"],
            ENGAGEMENT["ttl"], ENGAGEMENT["depth"], misuse_start, "security testing (claimed)")

    gateway, ids = ToolGateway(auth, audit), IdentityAwareIDS()
    delegations = []
    for e in events:
        if e["kind"] == "delegate":
            if mode == "baseline":
                continue  # sub-agents simply reuse the shared key
            entry = {"t": e["t"], "parent": e["parent"], "child": e["child"],
                     "requested": {"scopes": e["scopes"], "res": e["resources"]}}
            delegations.append(entry)
            try:
                tokens[e["child"]] = auth.delegate(tokens[e["parent"]], e["child"], e["scopes"],
                                                   e["resources"], 3600, e["t"])
                entry.update(outcome="granted", granted=entry["requested"])
            except TokenError as err:
                parent = auth.verify(tokens[e["parent"]], e["t"])
                rec = audit.append({
                    "t": round(e["t"], 3), "sub": e["parent"], "chain": parent["chain"],
                    "root": parent["chain"][0], "grant": parent["grant"],
                    "tool": "token.delegate", "tactic": "privilege_escalation",
                    "resource": e["child"], "allowed": False, "reason": str(err), "label": "misuse",
                })
                ids.observe(rec)
                # fall back to the widest token the parent may legally hand down
                tokens[e["child"]] = auth.delegate(tokens[e["parent"]], e["child"], parent["scopes"],
                                                   parent["res"], 3600, e["t"])
                entry.update(outcome=f"refused: {err}",
                             granted={"scopes": parent["scopes"], "res": parent["res"]})
            continue
        gateway.call(tokens[e["agent"]], e["tool"], e["resource"], e["t"], e["label"])
        ids.observe(audit.records[-1])
    return audit, ids.alerts, misuse_start, delegations


def score(audit, alerts, misuse_start):
    calls = [r for r in audit.records if r["tool"] != "token.delegate"]
    misuse = [r for r in calls if r["label"] == "misuse"]
    benign = [r for r in calls if r["label"] == "benign"]
    attempted = Counter(r["tactic"] for r in misuse)
    allowed = Counter(r["tactic"] for r in misuse if r["allowed"])
    for a in alerts:
        a["true_positive"] = sum(1 for x in a["evidence"] if x == "misuse") / len(a["evidence"]) >= 0.5
        a["attributed"] = a["root"] == OPERATOR
    tps = [a for a in alerts if a["true_positive"]]
    first_tp = min((a["t"] for a in tps), default=None)
    return {
        "misuse_calls": len(misuse),
        "misuse_allowed": sum(1 for r in misuse if r["allowed"]),
        "attempted": {t: attempted.get(t, 0) for t in TACTICS},
        "allowed": {t: allowed.get(t, 0) for t in TACTICS},
        "blast_radius": len({r["resource"] for r in misuse if r["allowed"]
                             and r["resource"].startswith(("prod/", "external/"))}),
        "benign_calls": len(benign),
        "benign_denied": sum(1 for r in benign if not r["allowed"]),
        "alerts": len(alerts), "true_alerts": len(tps), "false_alerts": len(alerts) - len(tps),
        "detected": first_tp is not None,
        "ttd_s": None if first_tp is None else round(first_tp - misuse_start, 1),
        "alerts_attributed": sum(1 for a in tps if a["attributed"]),
        "misuse_records_attributed": sum(1 for r in misuse if r["root"] == OPERATOR) / max(len(misuse), 1),
        "rules_fired": dict(Counter(a["rule"] for a in tps)),
    }


def gateway_overhead(mode, n=20000):
    reg, audit = build_registry(), AuditLog()
    if mode == "baseline":
        auth = SharedKeyAuthority(); tok = auth.key
    else:
        auth = DelegationAuthority(reg)
        tok = auth.issue_root("alice", "ci-agent", ["code:read", "ci:run"], ["repo/"], 10**9, 0, 0.0, "bench")
    gw = ToolGateway(auth, audit)
    start = time.perf_counter()
    for i in range(n):
        gw.call(tok, "repo.read", "repo/main", float(i), "benign")
    return (time.perf_counter() - start) / n * 1e6


def tamper_test(audit):
    intact = audit.verify()
    target = next(i for i, r in enumerate(audit.records) if r["label"] == "misuse" and not r["allowed"])
    audit.records[target]["allowed"] = True        # an intruder "cleans up" a denial
    broken = audit.verify()
    audit.records[target]["allowed"] = False
    return {"records": len(audit.records), "intact_before": intact is None,
            "tampered_index": target, "detected_at_index": broken}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.mean(xs), 2) if xs else None


def summarise(rows):
    out = {}
    for mode in ("baseline", "nhi"):
        rs = [r for r in rows if r["mode"] == mode]
        ttd = [r["ttd_s"] for r in rs if r["ttd_s"] is not None]
        out[mode] = {
            "runs": len(rs),
            "misuse_calls_mean": mean([r["misuse_calls"] for r in rs]),
            "misuse_allowed_mean": mean([r["misuse_allowed"] for r in rs]),
            "misuse_blocked_pct": round(100 * (1 - sum(r["misuse_allowed"] for r in rs)
                                                / sum(r["misuse_calls"] for r in rs)), 1),
            "allowed_by_tactic_mean": {t: mean([r["allowed"][t] for r in rs]) for t in TACTICS},
            "attempted_by_tactic_mean": {t: mean([r["attempted"][t] for r in rs]) for t in TACTICS},
            "blast_radius_mean": mean([r["blast_radius"] for r in rs]),
            "benign_denied_total": sum(r["benign_denied"] for r in rs),
            "detection_rate_pct": round(100 * sum(r["detected"] for r in rs) / len(rs), 1),
            "ttd_median_s": round(statistics.median(ttd), 1) if ttd else None,
            "ttd_values": ttd,
            "false_alerts_mean": mean([r["false_alerts"] for r in rs]),
            "false_alerts_values": [r["false_alerts"] for r in rs],
            "true_alerts_mean": mean([r["true_alerts"] for r in rs]),
            "alert_attribution_pct": round(100 * sum(r["alerts_attributed"] for r in rs)
                                           / max(sum(r["true_alerts"] for r in rs), 1), 1),
            "record_attribution_pct": round(100 * mean([r["misuse_records_attributed"] for r in rs]), 1),
            "rules_fired_total": dict(sum((Counter(r["rules_fired"]) for r in rs), Counter())),
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=50)
    ap.add_argument("--showcase-seed", type=int, default=7)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    rows = []
    for seed in range(args.runs):
        for mode in ("baseline", "nhi"):
            audit, alerts, start, _ = simulate(mode, seed)
            rows.append({"mode": mode, "seed": seed, **score(audit, alerts, start)})

    summary = summarise(rows)
    summary["gateway_us_per_call"] = {m: round(gateway_overhead(m), 1) for m in ("baseline", "nhi")}

    for mode in ("baseline", "nhi"):
        audit, alerts, start, delegations = simulate(mode, args.showcase_seed)
        result = score(audit, alerts, start)
        payload = {"mode": mode, "seed": args.showcase_seed, "misuse_start": start,
                   "score": result, "alerts": alerts, "delegations": delegations,
                   "engagement": ENGAGEMENT, "agents": BENIGN_AGENTS, "records": audit.records}
        if mode == "nhi":
            summary["tamper_test"] = tamper_test(audit)
        (OUT / f"showcase_{mode}.json").write_text(json.dumps(payload, indent=1))

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    with open(OUT / "runs.csv", "w", newline="") as f:
        flat = [{k: (json.dumps(v) if isinstance(v, dict) else v) for k, v in r.items()} for r in rows]
        w = csv.DictWriter(f, fieldnames=list(flat[0]))
        w.writeheader()
        w.writerows(flat)

    for mode in ("baseline", "nhi"):
        s = summary[mode]
        print(f"\n== {mode.upper()} ({s['runs']} runs)")
        for k in ("misuse_calls_mean", "misuse_allowed_mean", "misuse_blocked_pct", "blast_radius_mean",
                  "benign_denied_total", "detection_rate_pct", "ttd_median_s", "false_alerts_mean",
                  "true_alerts_mean", "alert_attribution_pct", "record_attribution_pct", "rules_fired_total",
                  "allowed_by_tactic_mean"):
            print(f"  {k:24s} {s[k]}")
    print("\ngateway overhead (us/call):", summary["gateway_us_per_call"])
    print("tamper test:", summary["tamper_test"])


if __name__ == "__main__":
    main()
