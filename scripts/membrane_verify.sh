#!/usr/bin/env bash
# Detached membrane verify: host-validate proposal and emit a concise verdict.
set -euo pipefail

MACOS_CAS="${MACOS_CAS_ROOT:-$HOME/Development/UltraViolet/MacOS-CAS}"
INPUT_JSON="${1:-${TMPDIR:-/tmp}/detached-membrane-return.json}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STRICT_LEGALITY="${STRICT_LEGALITY:-false}"
BHRTPROJ="${BHRT_PROJECTION_OUT:-${TMPDIR:-/tmp}/detached-membrane-bhrt-projection.json}"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "Usage: $0 [packet.json]"
  echo "Validate a detached membrane CAS return packet with MacOS-CAS host checks."
  echo "Env: STRICT_LEGALITY=true enables additional legality assertions."
  exit 0
fi

if [[ ! -f "$INPUT_JSON" ]]; then
  echo "FAIL: input packet not found at $INPUT_JSON" >&2
  echo "Usage: $0 [packet.json]" >&2
  exit 1
fi

if [[ ! -d "$MACOS_CAS" ]]; then
  echo "FAIL: MacOS-CAS not found at $MACOS_CAS" >&2
  exit 1
fi

ACK_JSON="${TMPDIR:-/tmp}/detached-membrane-ack.json"

(cd "$MACOS_CAS" && swift run MacOSAppCLI validate-return-packet --input "$INPUT_JSON" --json 2>/dev/null) > "$ACK_JSON"

python3 - <<PY
import json
import sys
from pathlib import Path

sys.path.insert(0, "$ROOT/packages/detached_membrane_sdk")
from detached_membrane_sdk.bhrt_projection import project_bhrt_packet
from detached_membrane_sdk.layered_verify import evaluate_layers
from detached_membrane_sdk.pim0_emit import emit_pim0_from_proposal
from detached_membrane_sdk.receipt_chain import (
    append_receipt_link,
    chain_enabled,
    default_chain_path,
    load_receipt_chain,
    resolve_parent_receipt_id,
    save_receipt_chain,
)
import subprocess

ack = json.loads(Path("$ACK_JSON").read_text(encoding="utf-8"))
packet = json.loads(Path("$INPUT_JSON").read_text(encoding="utf-8"))
ztna = packet.get("ztna", {})
receipt_path = ztna.get("receipt_path")
if not receipt_path:
    raise SystemExit("FAIL: missing ztna.receipt_path in packet")
if not Path(receipt_path).exists():
    raise SystemExit(f"FAIL: ztna receipt not found at {receipt_path}")

verify_cmd = [
    "python3",
    "$ROOT/scripts/ztna_decide_local.py",
    "verify",
    "--receipt",
    receipt_path,
    "--action",
    "membrane_propose",
    "--resource",
    "cas_return_packet",
    "--context-ref",
    packet.get("source_packet_id", ""),
]
verify_proc = subprocess.run(verify_cmd, capture_output=True, text=True)
if verify_proc.returncode != 0:
    raise SystemExit("FAIL: ztna verification failed: " + verify_proc.stdout + verify_proc.stderr)

if "$STRICT_LEGALITY" == "true":
    if packet.get("status") != "proposed":
        raise SystemExit("FAIL: strict legality requires status=proposed")
    if packet.get("authority_status") != "advisory_only":
        raise SystemExit("FAIL: strict legality requires authority_status=advisory_only")
    if packet.get("execution_permitted") is not False:
        raise SystemExit("FAIL: strict legality requires execution_permitted=false")
    if not packet.get("source_packet_id"):
        raise SystemExit("FAIL: strict legality requires source_packet_id")
    if not packet.get("actions_taken"):
        raise SystemExit("FAIL: strict legality requires non-empty actions_taken")
    if not ztna.get("policy_decision_ref"):
        raise SystemExit("FAIL: strict legality requires policy_decision_ref")
    if ztna.get("decision_ttl_seconds", 0) <= 0:
        raise SystemExit("FAIL: strict legality requires positive decision_ttl_seconds")

layered = evaluate_layers(
    packet=packet,
    ztna=ztna,
    host_ack=ack,
    ztna_verify_ok=verify_proc.returncode == 0,
    strict_legality="$STRICT_LEGALITY" == "true",
)
host_accepted = bool(ack.get("accepted", False))

result = {
    "object": "DetachedMembraneVerification",
    "packet_file": "$INPUT_JSON",
    "accepted": host_accepted and layered.get("accepted", False),
    "errors": ack.get("errors", []),
    "status": packet.get("status"),
    "authority_status": packet.get("authority_status", "advisory_only"),
    "execution_permitted": bool(packet.get("execution_permitted", False)),
    "executor_profile_id": packet.get("executor_profile_id"),
    "policy_decision_ref": ztna.get("policy_decision_ref"),
    "layer_reasons": layered.get("layer_reasons", []),
}

print(json.dumps(result, indent=2))

pim0_envelope = emit_pim0_from_proposal(packet=packet)
chain = load_receipt_chain() if chain_enabled() else None
parent_receipt_id = resolve_parent_receipt_id(
    chain=chain,
    fallback=ztna.get("policy_decision_ref"),
    enabled=chain_enabled(),
)
bhrt_projection = project_bhrt_packet(
    packet=packet,
    verification=result,
    ztna=ztna,
    pim0_envelope=pim0_envelope,
    parent_receipt_id=parent_receipt_id,
)
result["wyrm_trace_ref"] = bhrt_projection.get("wyrm_trace_ref")
result["parent_receipt_id"] = parent_receipt_id
if chain_enabled():
    updated = append_receipt_link(
        chain or load_receipt_chain(),
        source_packet_id=packet.get("source_packet_id"),
        return_id=packet.get("return_id"),
        policy_decision_ref=ztna.get("policy_decision_ref"),
        wyrm_trace_ref=bhrt_projection.get("wyrm_trace_ref"),
    )
    chain_path = save_receipt_chain(updated)
    result["receipt_chain_path"] = str(chain_path)
    result["receipt_chain_depth"] = len(updated.get("links") or [])
Path("$BHRTPROJ").write_text(json.dumps(bhrt_projection, indent=2), encoding="utf-8")
Path("${TMPDIR:-/tmp}/detached-membrane-pim0-envelope.json").write_text(
    json.dumps(pim0_envelope, indent=2), encoding="utf-8"
)
if result["accepted"]:
    raise SystemExit(0)
raise SystemExit(1)
PY
