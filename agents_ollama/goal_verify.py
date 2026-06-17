"""Goal verification guard before CAS return emission."""

from __future__ import annotations

import re

from agents import Agent, ModelSettings, Runner
from pydantic import BaseModel, Field

from agents_ollama.client import build_ollama_model, configure_ollama_runtime

DEFAULT_GOAL_MODEL = "gemma2:2b"


class GoalVerdict(BaseModel):
    """Fast-model assessment of whether an operator hint was satisfied."""

    satisfied: bool
    gap: str = Field(default="", description="What is missing if not satisfied")
    verdict_line: str = Field(default="", description="Raw YES/NO line from classifier")


def parse_goal_verdict_line(line: str) -> GoalVerdict:
    """Parse classifier output into a structured verdict."""
    stripped = line.strip()
    upper = stripped.upper()
    satisfied = upper.startswith("YES")
    gap = ""
    if not satisfied:
        if ":" in stripped:
            gap = stripped.split(":", 1)[1].strip()
        elif " - " in stripped:
            gap = stripped.split(" - ", 1)[1].strip()
        else:
            gap = stripped
    return GoalVerdict(satisfied=satisfied, gap=gap, verdict_line=stripped)


async def verify_goal(
    *,
    operator_hint: str,
    agent_output: str,
    model: str = DEFAULT_GOAL_MODEL,
) -> GoalVerdict:
    """Ask a fast local model whether the operator hint was satisfied."""
    configure_ollama_runtime()
    classifier = Agent(
        name="GoalVerifier",
        instructions=(
            "You verify whether an agent output satisfies an operator hint. "
            "Reply with exactly one line: YES or NO, then a short gap note if NO. "
            "Examples: 'YES' or 'NO: missing weather summary for Tokyo'."
        ),
        model=build_ollama_model(model),
        model_settings=ModelSettings(temperature=0.0),
    )
    prompt = (
        f"Operator hint:\n{operator_hint}\n\n"
        f"Agent output:\n{agent_output}\n\n"
        "Was the hint satisfied?"
    )
    result = await Runner.run(classifier, prompt)
    line = (result.final_output or "").strip()
    if not re.match(r"^(YES|NO)\b", line, flags=re.IGNORECASE):
        return GoalVerdict(
            satisfied=False,
            gap="classifier returned ambiguous verdict",
            verdict_line=line,
        )
    return parse_goal_verdict_line(line)
