"""Local ZTNA decision helpers (pure Python, no subprocess)."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _load_policy(policy_path: Path) -> dict[str, Any]:
    return json.loads(policy_path.read_text(encoding="utf-8"))


def _policy_allows(policy: dict[str, Any], action: str, resource: str) -> bool:
    for rule in policy.get("rules", []):
        if rule.get("action") != action:
            continue
        if resource in rule.get("allowed_resources", []) and rule.get("allow"):
            return True
    return False


def _identity_allowed(policy: dict[str, Any], identity_ref: str) -> bool:
    prefixes = policy.get("identity", {}).get("trusted_prefixes", [])
    return any(identity_ref.startswith(prefix) for prefix in prefixes)


def issue_receipt(
    *,
    policy_path: Path,
    identity_ref: str,
    action: str,
    resource: str,
    context_ref: str,
    out_path: Path | None = None,
) -> dict[str, Any]:
    policy = _load_policy(policy_path)
    allowed = _identity_allowed(policy, identity_ref) and _policy_allows(policy, action, resource)
    ttl = int(policy.get("ttl_seconds_default", 900))
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
    decision = "allow" if allowed else policy.get("default_decision", "deny")

    base = f"{identity_ref}|{action}|{resource}|{context_ref}|{decision}|{expires_at.isoformat()}"
    decision_ref = "ztna_decision_" + hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]
    receipt = {
        "object": "LocalZTNADecisionReceipt",
        "schema_version": "local-ztna-0_1",
        "policy_id": policy.get("policy_id", "unknown"),
        "decision_ref": decision_ref,
        "decision": decision,
        "identity_ref": identity_ref,
        "action": action,
        "resource": resource,
        "context_ref": context_ref,
        "issued_at": _iso_now(),
        "expires_at": expires_at.isoformat(),
        "token_id": f"ztna_{uuid.uuid4().hex[:12]}",
    }
    if out_path is not None:
        out_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    if not allowed:
        raise ValueError("ZTNA policy denied membrane_propose for cas_return_packet")
    return receipt


def verify_receipt(
    *,
    receipt: dict[str, Any],
    action: str,
    resource: str,
    context_ref: str = "",
) -> bool:
    now = datetime.now(timezone.utc)
    expires_at = _parse_iso(receipt["expires_at"])
    if receipt.get("decision") != "allow":
        return False
    if now > expires_at:
        return False
    if receipt.get("action") != action:
        return False
    if receipt.get("resource") != resource:
        return False
    if context_ref and receipt.get("context_ref") != context_ref:
        return False
    return True
