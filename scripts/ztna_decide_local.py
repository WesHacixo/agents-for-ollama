#!/usr/bin/env python3
"""Local ZTNA decision helper for detached membrane scripts."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import uuid


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


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


def issue_receipt(args: argparse.Namespace) -> int:
    policy = _load_json(args.policy)
    identity_ref = args.identity_ref
    action = args.action
    resource = args.resource

    allowed = _identity_allowed(policy, identity_ref) and _policy_allows(policy, action, resource)
    ttl = int(policy.get("ttl_seconds_default", 900))
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
    decision = "allow" if allowed else policy.get("default_decision", "deny")

    base = f"{identity_ref}|{action}|{resource}|{args.context_ref}|{decision}|{expires_at.isoformat()}"
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
        "context_ref": args.context_ref,
        "issued_at": _iso_now(),
        "expires_at": expires_at.isoformat(),
        "token_id": f"ztna_{uuid.uuid4().hex[:12]}",
    }
    Path(args.out).write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if allowed else 2


def verify_receipt(args: argparse.Namespace) -> int:
    receipt = _load_json(args.receipt)
    now = datetime.now(timezone.utc)
    expires_at = _parse_iso(receipt["expires_at"])

    if receipt.get("decision") != "allow":
        print("FAIL: ZTNA decision is not allow")
        return 1
    if now > expires_at:
        print("FAIL: ZTNA decision expired")
        return 1
    if receipt.get("action") != args.action:
        print("FAIL: ZTNA action mismatch")
        return 1
    if receipt.get("resource") != args.resource:
        print("FAIL: ZTNA resource mismatch")
        return 1
    if args.context_ref and receipt.get("context_ref") != args.context_ref:
        print("FAIL: ZTNA context_ref mismatch")
        return 1
    print("PASS: ZTNA receipt valid")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Local ZTNA decision utility.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    issue = sub.add_parser("issue", help="Issue a local ZTNA decision receipt")
    issue.add_argument("--policy", required=True)
    issue.add_argument("--identity-ref", required=True)
    issue.add_argument("--action", required=True)
    issue.add_argument("--resource", required=True)
    issue.add_argument("--context-ref", required=True)
    issue.add_argument("--out", required=True)

    verify = sub.add_parser("verify", help="Verify an existing local ZTNA decision receipt")
    verify.add_argument("--receipt", required=True)
    verify.add_argument("--action", required=True)
    verify.add_argument("--resource", required=True)
    verify.add_argument("--context-ref", default="")

    args = parser.parse_args()
    if args.cmd == "issue":
        return issue_receipt(args)
    return verify_receipt(args)


if __name__ == "__main__":
    raise SystemExit(main())
