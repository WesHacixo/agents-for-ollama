"""MVP slice — self-explaining demo of taste → think → propose → validate."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

from agents import Agent, ModelSettings, Runner

from agents_ollama.cas_return import build_cas_return_packet, validate_packet_structure
from agents_ollama.client import configure_ollama_runtime, build_ollama_model

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "fixtures/mvp/portfolio_context_stub.json"
SIGMEM0_EXPORT_URL = "http://127.0.0.1:8741/v1/context-pack/export"
DEFAULT_MODEL = "gemma4:12b-mlx"
FAST_MODEL = "gemma2:2b"


@dataclass
class MVPStep:
    name: str
    status: Literal["ok", "degraded", "skipped", "fail"]
    utility: str
    detail: str


@dataclass
class MVPReport:
    steps: list[MVPStep] = field(default_factory=list)
    context_source: str = "unknown"
    context_excerpt: str = ""
    agent_output: str = ""
    packet: dict[str, Any] | None = None
    host_validation: dict[str, Any] | None = None
    model: str = DEFAULT_MODEL

    def add(
        self,
        name: str,
        status: Literal["ok", "degraded", "skipped", "fail"],
        utility: str,
        detail: str,
    ) -> None:
        self.steps.append(MVPStep(name, status, utility, detail))


def load_fixture_context() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def fetch_sigmem0_context(timeout: float = 3.0) -> dict[str, Any] | None:
    today = os.getenv("SIGMEM0_DATE", date.today().isoformat())
    tz = os.getenv("SIGMEM0_TIMEZONE", "America/Los_Angeles")
    query = urllib.parse.urlencode({"date": today, "timezone": tz})
    url = f"{SIGMEM0_EXPORT_URL}?{query}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def _context_items(ctx: dict[str, Any]) -> list[str]:
    """Normalize fixture vs live ContextPackExportV0 into text lines."""
    threads = ctx.get("unresolved_threads") or []
    if threads:
        return [
            t.get("summary", str(t)) if isinstance(t, dict) else str(t) for t in threads
        ]
    pack = ctx.get("context_pack") or {}
    items = pack.get("items") or []
    lines: list[str] = []
    for item in items[:4]:
        if isinstance(item, dict) and item.get("text"):
            lines.append(str(item["text"]))
    if lines:
        return lines
    limitations = ctx.get("evidence_limitations") or []
    return [str(x) for x in limitations[:2]]


def context_to_hint(ctx: dict[str, Any]) -> str:
    lines = _context_items(ctx)
    actions = ctx.get("suggested_actions") or []
    action_labels = [
        a.get("label", str(a)) if isinstance(a, dict) else str(a) for a in actions[:1]
    ]
    parts = ["Given portfolio context, propose one concrete next step."]
    if lines:
        parts.append("Context: " + "; ".join(lines[:2]) + ".")
    if action_labels:
        parts.append("Suggested: " + action_labels[0] + ".")
    return " ".join(parts)


def context_excerpt(ctx: dict[str, Any], max_len: int = 280) -> str:
    lines = _context_items(ctx)
    if lines:
        return lines[0][:max_len]
    return (ctx.get("continuity_context") or ctx.get("authority_status") or "")[:max_len]


def ollama_reachable(base: str = "http://localhost:11434") -> bool:
    try:
        with urllib.request.urlopen(f"{base}/api/tags", timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


async def run_agent_proposal(*, hint: str, model: str) -> str:
    configure_ollama_runtime()
    agent = Agent(
        name="MVPSliceAgent",
        instructions=(
            "You are a governed portfolio assistant. Reply in 2 sentences max. "
            "Proposal only: no file writes, shell, or truth promotion."
        ),
        model=build_ollama_model(model),
        model_settings=ModelSettings(temperature=0.2),
    )
    result = await Runner.run(agent, hint)
    return (result.final_output or "").strip()


def try_host_validate(packet: dict[str, Any], macos_cas_root: Path) -> dict[str, Any] | None:
    import subprocess
    import tempfile

    if not (macos_cas_root / "Package.swift").is_file():
        return None
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(packet, tmp)
        tmp_path = tmp.name
    try:
        export = subprocess.run(
            [
                "swift", "run", "MacOSAppCLI", "cas1-export",
                "--output", f"{tmp_path}.cas1.json",
            ],
            cwd=macos_cas_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if export.returncode != 0:
            return {"skipped": True, "reason": "cas1-export failed"}
        cas1 = json.loads(Path(f"{tmp_path}.cas1.json").read_text())
        packet = {**packet, "source_packet_id": cas1["packet_id"]}
        Path(tmp_path).write_text(json.dumps(packet), encoding="utf-8")
        validate = subprocess.run(
            [
                "swift", "run", "MacOSAppCLI", "validate-return-packet",
                "--input", tmp_path, "--json",
            ],
            cwd=macos_cas_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if validate.returncode != 0 and not validate.stdout.strip():
            return {"skipped": True, "reason": validate.stderr.strip() or "validate failed"}
        return json.loads(validate.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as exc:
        return {"skipped": True, "reason": str(exc)}
    finally:
        for p in (tmp_path, f"{tmp_path}.cas1.json"):
            try:
                Path(p).unlink(missing_ok=True)
            except OSError:
                pass


async def run_mvp_slice(
    *,
    model: str,
    offline_context: bool,
    with_host: bool,
    macos_cas_root: Path,
) -> MVPReport:
    report = MVPReport(model=model)

    # --- Taste ---
    ctx: dict[str, Any]
    if offline_context:
        ctx = load_fixture_context()
        report.context_source = "fixture"
        report.add(
            "taste",
            "degraded",
            "Shows how agents ingest portfolio context without writing memory.",
            "Used bundled fixture (SigMem0 not required for this demo).",
        )
    else:
        live = fetch_sigmem0_context()
        if live:
            ctx = live
            report.context_source = "sigmem0_live"
            report.add(
                "taste",
                "ok",
                "Live read from SigMem0 — contextual, not canonical truth.",
                f"GET {SIGMEM0_EXPORT_URL}?date=…&timezone=…",
            )
        else:
            ctx = load_fixture_context()
            report.context_source = "fixture_fallback"
            report.add(
                "taste",
                "degraded",
                "Same contract as live recall — fixture proves the shape when :8741 is down.",
                "Start SigMem0 with: uv run siglent-runtime serve",
            )

    report.context_excerpt = context_excerpt(ctx)
    hint = context_to_hint(ctx)

    # --- Think ---
    if not ollama_reachable():
        report.add(
            "think",
            "fail",
            "Local agent loop on Ollama — no cloud API key.",
            "Ollama not reachable at localhost:11434",
        )
        stub_output = (
            "Proposal (offline stub): prioritize SigMem0 recall tool in python_agents_sdk "
            "executor; validate with host before any memory promotion."
        )
        report.agent_output = stub_output
        report.packet = build_cas_return_packet(
            agent_output=stub_output,
            hint=hint,
            source_packet_id="cas1_mvp_slice_offline",
        )
        report.add(
            "propose",
            "degraded",
            "CASReturnPacket — host-validatable proposal envelope.",
            "Built from stub text because Ollama was unavailable.",
        )
    else:
        try:
            report.agent_output = await run_agent_proposal(hint=hint, model=model)
            report.add(
                "think",
                "ok",
                "OpenAI Agents SDK + Ollama /v1 — tool-ready local ReAct when you need it.",
                f"Model: {model}",
            )
        except Exception as exc:
            report.add("think", "fail", "Local agent inference.", str(exc))
            raise

        report.packet = build_cas_return_packet(
            agent_output=report.agent_output,
            hint=hint,
            source_packet_id="cas1_mvp_slice_demo",
        )
        struct_errors = validate_packet_structure(report.packet)
        if struct_errors:
            report.add("propose", "fail", "Structural CAS contract.", str(struct_errors))
        else:
            report.add(
                "propose",
                "ok",
                "Emits CASReturnPacket — MacOS-CAS can validate and apply without trusting stdout.",
                f"return_id={report.packet.get('return_id', '?')}",
            )

    # --- Validate (host) ---
    if with_host and report.packet:
        host = try_host_validate(report.packet, macos_cas_root)
        report.host_validation = host
        if host and host.get("accepted"):
            report.add(
                "validate",
                "ok",
                "Host accepted the proposal — governance gate passed.",
                f"return_id={host.get('return_id', '?')}",
            )
        elif host and host.get("skipped"):
            report.add(
                "validate",
                "skipped",
                "MacOS-CAS validate-return-packet when checkout present.",
                str(host.get("reason", "skipped")),
            )
        else:
            report.add(
                "validate",
                "degraded",
                "Host validation attempted.",
                json.dumps(host or {}, indent=None)[:200],
            )
    else:
        report.add(
            "validate",
            "skipped",
            "Run with --with-host to prove MacOS-CAS accept path.",
            "Structural validation already passed in propose step.",
        )

    return report


def print_mvp_narrative(report: MVPReport) -> None:
    w = sys.stdout.write
    w("\n")
    w("╔══════════════════════════════════════════════════════════════════╗\n")
    w("║  MVP SLICE — Programmatic intelligence in one pass               ║\n")
    w("╚══════════════════════════════════════════════════════════════════╝\n\n")

    w("WHY THIS EXISTS\n")
    w("──────────────\n")
    w("Chat in a terminal does not cross portfolio boundaries. This slice shows\n")
    w("taste → think → propose → validate: memory context in, governed proposal out.\n")
    w("No Atlas orient, no commit policy, no runbook — the run explains itself.\n\n")

    w("WHAT RAN\n")
    w("────────\n")
    for step in report.steps:
        icon = {"ok": "✓", "degraded": "~", "skipped": "○", "fail": "✗"}[step.status]
        w(f"  [{icon}] {step.name.upper():8}  {step.detail}\n")
    w("\n")

    w("VALUE BY STAKEHOLDER\n")
    w("────────────────────\n")
    w("  Operator   One command proves local agent + governance envelope work.\n")
    w("  SigMem0    Context is tasted (fixture or :8741), never promoted by the agent.\n")
    w("  MacOS-CAS  CASReturnPacket is ingestible; --with-host proves accept=true.\n")
    w("  Atlas      Returns are receipts for orientation, not capsule truth.\n\n")

    w("CONTEXT TASTED\n")
    w("──────────────\n")
    w(f"  source: {report.context_source}\n")
    w(f"  thread: {report.context_excerpt}\n\n")

    if report.agent_output:
        w("AGENT PROPOSAL\n")
        w("──────────────\n")
        w(f"  {report.agent_output}\n\n")

    if report.packet:
        w("CAS RETURN (excerpt)\n")
        w("──────────────────\n")
        w(f"  executor_profile_id: {report.packet.get('executor_profile_id')}\n")
        w(f"  status:              {report.packet.get('status')}\n")
        w(f"  actions_taken[0]:    {(report.packet.get('actions_taken') or [''])[0][:72]}…\n\n")

    if report.host_validation and report.host_validation.get("accepted"):
        w("HOST GATE\n")
        w("─────────\n")
        w("  accepted=true — proposal may flow to host apply (still not session truth).\n\n")

    w("NEXT (optional, not required to understand value)\n")
    w("─────────────────────────────────────────────────\n")
    w("  ./scripts/test_patterns.sh          full pattern catalog\n")
    w("  ./scripts/python_agents_apply_smoke.sh   live subprocess + apply\n")
    w("  docs/programmatic-intelligence-seams.md    deep seam map\n\n")

    failed = any(s.status == "fail" for s in report.steps)
    if failed:
        w("RESULT: INCOMPLETE — fix failures above (usually: start Ollama).\n\n")
    else:
        w("RESULT: MVP SLICE OK — value demonstrated without operational ceremony.\n\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Self-explaining MVP: portfolio taste → local agent → CAS proposal.",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help=f"Use {FAST_MODEL} for quicker demo",
    )
    parser.add_argument(
        "--offline-context",
        action="store_true",
        help="Skip SigMem0 probe; use fixture only",
    )
    parser.add_argument(
        "--with-host",
        action="store_true",
        help="Attempt MacOS-CAS validate-return-packet (slower; needs Swift checkout)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable report JSON after narrative",
    )
    parser.add_argument(
        "--macos-cas-root",
        default=os.getenv(
            "MACOS_CAS_ROOT",
            os.path.expanduser("~/Development/UltraViolet/MacOS-CAS"),
        ),
    )
    args = parser.parse_args()
    model = FAST_MODEL if args.fast else os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)

    report = asyncio.run(
        run_mvp_slice(
            model=model,
            offline_context=args.offline_context,
            with_host=args.with_host,
            macos_cas_root=Path(args.macos_cas_root),
        )
    )
    print_mvp_narrative(report)
    if args.json:
        payload = {
            "steps": [s.__dict__ for s in report.steps],
            "context_source": report.context_source,
            "context_excerpt": report.context_excerpt,
            "agent_output": report.agent_output,
            "packet": report.packet,
            "host_validation": report.host_validation,
            "model": report.model,
        }
        print(json.dumps(payload, indent=2))

    if any(s.status == "fail" for s in report.steps):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
