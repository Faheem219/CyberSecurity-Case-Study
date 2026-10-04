"""Identity-aware intrusion detection over the gateway's audit stream.

Three simple rules. They are deliberately basic; the point of the study is
what the *same* rules can see when every call carries a distinct identity.

  R1 TEMPO      one actor makes more calls in a short window than a human could
  R2 PROBING    one actor keeps hitting permission walls (repeated denials)
  R3 KILL_CHAIN one delegation grant spans several ATT&CK tactics quickly
"""
from collections import defaultdict, deque

SENSITIVE = {"discovery", "credential_access", "lateral_movement",
             "collection", "exfiltration", "privilege_escalation"}


class IdentityAwareIDS:
    def __init__(self, tempo_limit=20, tempo_window=10.0, deny_limit=3,
                 deny_window=60.0, chain_tactics=3, chain_window=1800.0,
                 cooldown=900.0):
        self.tempo_limit, self.tempo_window = tempo_limit, tempo_window
        self.deny_limit, self.deny_window = deny_limit, deny_window
        self.chain_tactics, self.chain_window = chain_tactics, chain_window
        self.cooldown = cooldown
        self._calls = defaultdict(deque)     # actor -> recent call records
        self._denials = defaultdict(deque)   # actor -> recent denied records
        self._tactics = defaultdict(dict)    # grant -> {tactic: last record}
        self._last_alert = {}
        self.alerts = []

    @staticmethod
    def _trim(window, now, span):
        while window and now - window[0]["t"] > span:
            window.popleft()

    def _raise(self, rule, key, rec, evidence):
        last = self._last_alert.get((rule, key))
        if last is not None and rec["t"] - last < self.cooldown:
            return
        self._last_alert[(rule, key)] = rec["t"]
        self.alerts.append({
            "rule": rule, "t": rec["t"], "actor": rec["sub"], "root": rec["root"],
            "chain": rec["chain"], "evidence": [e["label"] for e in evidence],
        })

    def observe(self, rec):
        actor, now = rec["sub"], rec["t"]

        calls = self._calls[actor]
        calls.append(rec)
        self._trim(calls, now, self.tempo_window)
        if len(calls) > self.tempo_limit:
            self._raise("R1_TEMPO", actor, rec, list(calls))

        if not rec["allowed"]:
            denials = self._denials[actor]
            denials.append(rec)
            self._trim(denials, now, self.deny_window)
            if len(denials) >= self.deny_limit:
                self._raise("R2_PROBING", actor, rec, list(denials))

        if rec["tactic"] in SENSITIVE:
            grant = rec.get("grant", rec["root"])
            seen = self._tactics[grant]
            seen[rec["tactic"]] = rec
            recent = [r for r in seen.values() if now - r["t"] <= self.chain_window]
            if len(recent) >= self.chain_tactics:
                self._raise("R3_KILL_CHAIN", grant, rec, recent)
