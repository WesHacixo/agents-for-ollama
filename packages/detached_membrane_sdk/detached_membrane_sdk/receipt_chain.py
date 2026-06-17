"""Receipt chain state for multi-step detached membrane operations."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CHAIN_SCHEMA_VERSION = "receipt-chain-v0"
MAX_LINKS = 32


def default_chain_path() -> Path:
    tmp = os.environ.get("TMPDIR", "/tmp")
    return Path(os.getenv("MEMBRANE_RECEIPT_CHAIN_PATH", f"{tmp}/detached-membrane-receipt-chain.json"))


def chain_enabled() -> bool:
    return os.getenv("MEMBRANE_CHAIN_RECEIPTS", "").lower() in {"1", "true", "yes"}


def load_receipt_chain(path: Path | None = None) -> dict[str, Any]:
    chain_path = path or default_chain_path()
    if not chain_path.is_file():
        return {"schema_version": CHAIN_SCHEMA_VERSION, "links": []}
    data = json.loads(chain_path.read_text(encoding="utf-8"))
    if data.get("schema_version") != CHAIN_SCHEMA_VERSION:
        return {"schema_version": CHAIN_SCHEMA_VERSION, "links": []}
    return data


def resolve_parent_receipt_id(
    *,
    chain: dict[str, Any] | None,
    fallback: str | None = None,
    enabled: bool = True,
) -> str | None:
    if not enabled or not chain:
        return fallback
    links = chain.get("links") or []
    if not links:
        return fallback
    last = links[-1]
    return last.get("wyrm_trace_ref") or last.get("policy_decision_ref") or fallback


def append_receipt_link(
    chain: dict[str, Any],
    *,
    source_packet_id: str | None,
    return_id: str | None,
    policy_decision_ref: str | None,
    wyrm_trace_ref: str | None,
) -> dict[str, Any]:
    links = list(chain.get("links") or [])
    links.append(
        {
            "source_packet_id": source_packet_id,
            "return_id": return_id,
            "policy_decision_ref": policy_decision_ref,
            "wyrm_trace_ref": wyrm_trace_ref,
        }
    )
    if len(links) > MAX_LINKS:
        links = links[-MAX_LINKS:]
    return {"schema_version": CHAIN_SCHEMA_VERSION, "links": links}


def save_receipt_chain(chain: dict[str, Any], path: Path | None = None) -> Path:
    chain_path = path or default_chain_path()
    chain_path.write_text(json.dumps(chain, indent=2), encoding="utf-8")
    return chain_path
