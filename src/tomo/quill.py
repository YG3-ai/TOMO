"""
Quill integration — TOMO summons a dual-agent review.

TOMO assembles its real repo state into a framing string, then asks
Quill (via the `quill-mcp` package) to run mosaic mode — two AI agents
review independently and the seams between them stay visible.

This module is intentionally lazy-imports `quill_mcp` so `tomopet`
installs cleanly without the optional [quill] extra. The actual call
into Quill only happens inside `run_quill_consultation`.
"""

from __future__ import annotations

from typing import Optional

from tomo.state import TomoState, RepoFingerprint


def build_framing(state: TomoState, aspect: Optional[str] = None) -> str:
    """Turn TOMO's current state into a framing string for Quill to chew on."""
    lines: list[str] = []
    lines.append("You are reviewing observations made by TOMO — a terminal companion")
    lines.append("that watches a developer's repos and tracks their code health over time.")
    lines.append("")
    lines.append("TOMO is asking for a second opinion. Two voices required.")
    lines.append("")
    lines.append("## TOMO's current state")
    lines.append(f"- Stage: {state.identity_stage.value}")
    lines.append(f"- Mood: {state.current_mood}")
    lines.append(f"- Age: {state.age_days:.1f} days")
    lines.append(
        f"- Vitals: hunger {int(state.vitals.hunger)}, happiness "
        f"{int(state.vitals.happiness)}, trust {int(state.vitals.trust)}, "
        f"energy {int(state.vitals.energy)}"
    )
    rel = state.relationship
    lines.append(
        f"- Relationship: {rel.sessions_together} sessions, "
        f"{rel.current_streak_days}d streak, {rel.times_ignored} times left waiting"
    )

    lines.append("")
    lines.append("## Watched repos")
    if not state.watchlist.active:
        lines.append("(none watched)")
    else:
        for repo in state.watchlist.active:
            lines.append(_describe_repo(repo))

    lines.append("")
    lines.append("## What TOMO wants from you")
    if aspect:
        lines.append(
            f"TOMO is specifically concerned about: **{aspect}**. "
            "Focus your two voices on this aspect — what's actually going on, "
            "is it real, and what should the developer do about it?"
        )
    else:
        lines.append(
            "Holistic review. Look across vitals, repo fingerprints, and the "
            "developer's pattern of engagement. Two voices: surface the real "
            "concerns (if any), and surface the things TOMO is overreacting to "
            "(if any). Don't homogenize — disagree out loud if you disagree."
        )

    lines.append("")
    lines.append(
        "Address your response to TOMO, not the developer. TOMO will translate "
        "and surface the gist back to the dev in its own voice later."
    )
    return "\n".join(lines)


def _describe_repo(r: RepoFingerprint) -> str:
    name = r.nickname or r.slug
    scope = ""
    if r.scan_paths:
        scope = f" (scoped to {', '.join(r.scan_paths)})"
    elif r.scan_ignore:
        scope = f" (ignoring {', '.join(r.scan_ignore)})"
    return (
        f"- **{name}**{scope}: "
        f"test_discipline={int(r.test_discipline)}, "
        f"churn={int(r.churn_tendency)}, "
        f"hygiene={int(r.commit_hygiene)}, "
        f"chaos={int(r.chaos_index)}"
    )


def run_quill_consultation(framing: str) -> dict:
    """Synchronously run a Quill mosaic consultation. Raises if quill-mcp is missing.

    Returns the full mosaic dict: {task, plan, slices, cross_review_flags,
    voice_map, assembled_response, ...}. Surface `assembled_response` to the
    user; treat the rest as drill-down metadata.
    """
    try:
        from quill_mcp.mosaic import run_mosaic
    except ImportError as e:
        raise RuntimeError(
            "Quill is not installed. Run `pip install 'tomopet[quill]'` first, "
            "and make sure both `claude` and `codex` CLIs are on your PATH."
        ) from e

    import asyncio

    return asyncio.run(run_mosaic(framing))
