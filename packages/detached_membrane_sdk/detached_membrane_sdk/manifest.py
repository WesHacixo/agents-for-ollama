"""Detached membrane manifest checksum verification (CP0-inspired contract spine)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


MANIFEST_REL_PATH = Path("packages/detached_membrane_sdk/spec/detached-membrane-manifest.v1.json")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def artifact_checksum_records(root: Path, artifacts: list[dict[str, Any]]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for entry in artifacts:
        rel = entry["path"]
        file_path = root / rel
        if not file_path.is_file():
            raise FileNotFoundError(f"missing manifest artifact: {rel}")
        records.append({"path": rel, "sha256": sha256_file(file_path)})
    records.sort(key=lambda item: item["path"])
    return records


def compute_artifacts_checksum(records: list[dict[str, str]]) -> str:
    canonical = json.dumps(records, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def verify_manifest(manifest_path: Path, root: Path) -> tuple[bool, list[str]]:
    """Return (ok, reasons) for manifest integrity and declared checksum."""
    reasons: list[str] = []
    manifest = load_manifest(manifest_path)
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        return False, ["manifest artifacts list is missing or empty"]

    declared = manifest.get("declared_checksum")
    if not isinstance(declared, str) or not declared:
        return False, ["manifest declared_checksum is missing"]

    try:
        records = artifact_checksum_records(root, artifacts)
    except FileNotFoundError as exc:
        return False, [str(exc)]

    actual = compute_artifacts_checksum(records)
    if actual != declared:
        reasons.append(
            f"checksum mismatch: declared={declared} actual={actual} "
            "(run ./scripts/refresh_membrane_manifest_checksum.sh after intentional edits)"
        )
    else:
        reasons.append(f"checksum match: {actual}")

    for invariant in manifest.get("invariants", []):
        inv_id = invariant.get("id", "unknown")
        text = invariant.get("text", "")
        if not text:
            reasons.append(f"invariant {inv_id}: missing text")
        else:
            reasons.append(f"invariant {inv_id}: declared")

    ok = actual == declared
    return ok, reasons


def refresh_declared_checksum(manifest_path: Path, root: Path) -> str:
    manifest = load_manifest(manifest_path)
    records = artifact_checksum_records(root, manifest["artifacts"])
    checksum = compute_artifacts_checksum(records)
    manifest["declared_checksum"] = checksum
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return checksum
