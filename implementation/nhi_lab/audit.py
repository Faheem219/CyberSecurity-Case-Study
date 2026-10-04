"""Tamper-evident audit log: each record carries the SHA-256 of its predecessor."""
import hashlib
import json

GENESIS = "0" * 64


def _digest(prev_hash, record):
    payload = json.dumps(record, sort_keys=True).encode()
    return hashlib.sha256(prev_hash.encode() + payload).hexdigest()


class AuditLog:
    def __init__(self):
        self.records = []

    def append(self, record):
        prev = self.records[-1]["hash"] if self.records else GENESIS
        body = {k: v for k, v in record.items() if k not in ("prev", "hash")}
        entry = {**body, "prev": prev, "hash": _digest(prev, body)}
        self.records.append(entry)
        return entry

    def verify(self):
        """Return the index of the first broken record, or None if the chain is intact."""
        prev = GENESIS
        for i, entry in enumerate(self.records):
            body = {k: v for k, v in entry.items() if k not in ("prev", "hash")}
            if entry["prev"] != prev or entry["hash"] != _digest(prev, body):
                return i
            prev = entry["hash"]
        return None

    def timeline(self, root=None):
        """Forensic view: records for one accountable human, oldest first."""
        rows = self.records if root is None else [r for r in self.records if r["root"] == root]
        return sorted(rows, key=lambda r: r["t"])
