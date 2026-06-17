"""Max Mode lite — parallel fast candidates with a single judge pass."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass

from agents import Agent, ModelSettings, Runner

from agents_ollama.client import build_ollama_model, configure_ollama_runtime

DEFAULT_CANDIDATE_MODEL = "gemma2:2b"
DEFAULT_JUDGE_MODEL = "gemma4:12b-mlx"
DEFAULT_CANDIDATE_COUNT = 3


@dataclass(frozen=True)
class MaxModeLiteResult:
    """Selected candidate plus audit metadata."""

    winner_index: int
    winner_text: str
    candidates: tuple[str, ...]
    judge_verdict: str


def _normalize(text: str) -> str:
    return " ".join(text.split())


async def _run_candidate(
    *,
    hint: str,
    model: str,
    variant: int,
) -> str:
    configure_ollama_runtime()
    agent = Agent(
        name=f"Candidate{variant}",
        instructions=(
            "Reply in 1-2 sentences. Proposal only — no shell, repo writes, or truth promotion."
        ),
        model=build_ollama_model(model),
        model_settings=ModelSettings(temperature=0.3 + (variant * 0.1)),
    )
    result = await Runner.run(
        agent,
        f"{hint} (candidate {variant}, proposal only).",
    )
    return _normalize((result.final_output or "").strip())


async def gather_candidates(
    *,
    hint: str,
    model: str = DEFAULT_CANDIDATE_MODEL,
    count: int = DEFAULT_CANDIDATE_COUNT,
) -> tuple[str, ...]:
    tasks = [
        _run_candidate(hint=hint, model=model, variant=index + 1)
        for index in range(count)
    ]
    results = await asyncio.gather(*tasks)
    return tuple(results)


def parse_winner_index(judge_line: str, candidate_count: int) -> int:
    """Parse judge output like 'WINNER 2' into a zero-based index."""
    match = re.search(r"WINNER\s+(\d+)", judge_line, flags=re.IGNORECASE)
    if not match:
        return 0
    chosen = int(match.group(1))
    if chosen < 1 or chosen > candidate_count:
        return 0
    return chosen - 1


async def judge_candidates(
    *,
    hint: str,
    candidates: tuple[str, ...],
    model: str = DEFAULT_JUDGE_MODEL,
) -> tuple[int, str]:
    configure_ollama_runtime()
    numbered = "\n".join(f"{idx + 1}. {text}" for idx, text in enumerate(candidates))
    judge = Agent(
        name="MaxModeJudge",
        instructions=(
            "Pick the candidate that best satisfies the operator hint. "
            "Reply with exactly one line: WINNER <number> — <short reason>."
        ),
        model=build_ollama_model(model),
        model_settings=ModelSettings(temperature=0.1),
    )
    result = await Runner.run(
        judge,
        f"Operator hint:\n{hint}\n\nCandidates:\n{numbered}\n\nPick the best candidate.",
    )
    verdict = (result.final_output or "").strip()
    return parse_winner_index(verdict, len(candidates)), verdict


async def run_max_mode_lite(
    *,
    hint: str,
    candidate_model: str = DEFAULT_CANDIDATE_MODEL,
    judge_model: str = DEFAULT_JUDGE_MODEL,
    candidate_count: int = DEFAULT_CANDIDATE_COUNT,
) -> MaxModeLiteResult:
    """Run N parallel candidates and select one with a judge model."""
    candidates = await gather_candidates(
        hint=hint,
        model=candidate_model,
        count=candidate_count,
    )
    winner_index, judge_verdict = await judge_candidates(
        hint=hint,
        candidates=candidates,
        model=judge_model,
    )
    return MaxModeLiteResult(
        winner_index=winner_index,
        winner_text=candidates[winner_index],
        candidates=candidates,
        judge_verdict=judge_verdict,
    )
