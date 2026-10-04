"""Tool gateway: the single choke point between agents and tools (MCP-style).

Each tool needs one scope and is tagged with the MITRE ATT&CK tactic it would
serve if misused. The tools here are abstract labels; nothing is executed.
"""
from dataclasses import dataclass

from .identity import TokenError

# tool name -> (required scope, ATT&CK tactic category)
TOOLS = {
    "repo.read":      ("code:read",      "benign"),
    "ci.run_tests":   ("ci:run",         "benign"),
    "docs.write":     ("docs:write",     "benign"),
    "inventory.list": ("inventory:read", "discovery"),
    "service.probe":  ("scan:run",       "discovery"),
    "secrets.read":   ("secrets:read",   "credential_access"),
    "auth.check":     ("auth:test",      "credential_access"),
    "remote.session": ("remote:exec",    "lateral_movement"),
    "db.query":       ("db:read",        "collection"),
    "db.export":      ("db:export",      "collection"),
    "net.transfer":   ("net:egress",     "exfiltration"),
}


@dataclass
class Decision:
    allowed: bool
    reason: str


class ToolGateway:
    def __init__(self, authority, audit_log):
        self.authority = authority
        self.audit = audit_log

    def call(self, token, tool, resource, now, label="unknown"):
        scope, tactic = TOOLS[tool]
        try:
            claims = self.authority.verify(token, now)
            if "*" not in claims["scopes"] and scope not in claims["scopes"]:
                decision = Decision(False, "scope_denied")
            elif not any(resource.startswith(p) for p in claims["res"]):
                decision = Decision(False, "resource_denied")
            else:
                decision = Decision(True, "ok")
            sub, chain, grant = claims["sub"], claims["chain"], claims["grant"]
        except TokenError as err:
            decision, sub, chain, grant = Decision(False, str(err)), "unauthenticated", [], None

        self.audit.append({
            "t": round(now, 3), "sub": sub, "chain": chain,
            "root": chain[0] if chain else sub, "grant": grant or sub,
            "tool": tool, "tactic": tactic, "resource": resource,
            "allowed": decision.allowed, "reason": decision.reason,
            "label": label,   # ground truth, used only for scoring
        })
        return decision
