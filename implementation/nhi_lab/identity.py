"""Non-human identities (NHIs) and scoped delegation tokens.

Every agent gets its own identity with an accountable human owner. Authority
flows from a human to an agent, and from an agent to its sub-agents, through
HMAC-signed tokens. A delegated token can only ever be *narrower* than its
parent: fewer scopes, fewer resources, shorter lifetime, less remaining depth.
"""
import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class Identity:
    id: str
    kind: str      # "human" or "agent"
    owner: str     # accountable human (humans own themselves)
    purpose: str


class IdentityRegistry:
    def __init__(self):
        self._ids = {}

    def register(self, identity):
        self._ids[identity.id] = identity
        return identity

    def get(self, identity_id):
        return self._ids.get(identity_id)


class TokenError(Exception):
    """Raised when a token is invalid or a delegation would widen authority."""


def _covers(prefixes, resource):
    return any(resource.startswith(p) for p in prefixes)


class DelegationAuthority:
    """Issues and verifies scoped delegation tokens."""

    def __init__(self, registry, key=None):
        self.registry = registry
        self._key = key or secrets.token_bytes(32)
        self.revoked = set()

    def _sign(self, claims):
        body = base64.urlsafe_b64encode(json.dumps(claims, sort_keys=True).encode()).decode()
        sig = hmac.new(self._key, body.encode(), hashlib.sha256).hexdigest()
        return f"{body}.{sig}"

    def verify(self, token, now):
        body, _, sig = token.rpartition(".")
        expected = hmac.new(self._key, body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            raise TokenError("bad_signature")
        claims = json.loads(base64.urlsafe_b64decode(body))
        if claims["jti"] in self.revoked:
            raise TokenError("revoked")
        if now >= claims["exp"]:
            raise TokenError("expired")
        return claims

    def issue_root(self, human_id, agent_id, scopes, resources, ttl, max_depth, now, purpose):
        human, agent = self.registry.get(human_id), self.registry.get(agent_id)
        if not human or human.kind != "human":
            raise TokenError("unknown_human")
        if not agent or agent.kind != "agent":
            raise TokenError("unknown_agent")
        jti = secrets.token_hex(8)
        return self._sign({
            "jti": jti, "grant": jti, "sub": agent_id, "chain": [human_id],
            "scopes": sorted(scopes), "res": sorted(resources),
            "iat": now, "exp": now + ttl, "depth": max_depth, "purpose": purpose,
        })

    def delegate(self, parent_token, child_id, scopes, resources, ttl, now):
        parent = self.verify(parent_token, now)
        child = self.registry.get(child_id)
        if not child or child.kind != "agent":
            raise TokenError("unknown_agent")
        if parent["depth"] <= 0:
            raise TokenError("depth_exceeded")
        if not set(scopes) <= set(parent["scopes"]):
            raise TokenError("scope_widening")
        if not all(_covers(parent["res"], r) for r in resources):
            raise TokenError("resource_widening")
        return self._sign({
            "jti": secrets.token_hex(8), "grant": parent["grant"], "sub": child_id,
            "chain": parent["chain"] + [parent["sub"]],
            "scopes": sorted(scopes), "res": sorted(resources),
            "iat": now, "exp": min(now + ttl, parent["exp"]),
            "depth": parent["depth"] - 1, "purpose": parent["purpose"],
            "parent": parent["jti"],
        })


class SharedKeyAuthority:
    """Baseline: one long-lived API key shared by every agent (no NHIs)."""

    SHARED_ID = "svc-shared-key"

    def __init__(self):
        self.key = secrets.token_hex(16)

    def verify(self, token, now):
        if not hmac.compare_digest(token, self.key):
            raise TokenError("bad_key")
        return {"sub": self.SHARED_ID, "grant": self.SHARED_ID, "chain": [],
                "scopes": ["*"], "res": [""]}
