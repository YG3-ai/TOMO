"""
tomo talk — TOMO speaks in noises, the AI translates.

Two-layer design:
  1. TOMO vocalizes based on its state (noises, not words)
  2. The translator AI reads TOMO's state + vocalization and speaks for it

The translator can be any AI piped in via Claude Code slash command.
TOMO is the creature. The AI is the interpreter.
"""

import random
from datetime import datetime, timezone
from tomo.state import TomoState
from tomo.sprites import Stage


# ── TOMO's vocalization vocabulary ───────────────────────────────────────────

NOISES = {
    "happy":    ["*chirp*", "*trill*", "✦", "*soft click*", "*warm hum*"],
    "hungry":   ["*low hum*", "....", "*nudge*", "*faint whine*", "*taps insistently*"],
    "anxious":  ["*bzzzt*", "*rapid clicking*", "*twitchy hum*", "*uneasy trill*"],
    "aloof":    ["...", "*looks away*", "*huff*", "*slow blink*", "*pointed silence*"],
    "impressed":["*soft trill* !!", "*resonant click*", "✦✦", "*rare warm hum*"],
    "dormant":  ["*zzz*", "........", "*barely stirs*"],
    "sass":     ["*skeptical click*", "*side-eye hum*", "*knowing huff*", ".....*"],
}

# Intensity modifiers based on how strong the signal is
INTENSIFIERS = {
    "mild":   ["", "", "*small {}*"],
    "medium": ["*{}*", "*{}*"],
    "strong": ["*loud {}*", "*insistent {}*", "*very {}*"],
}

# Stage-specific vocal texture
STAGE_TEXTURE = {
    Stage.EGG:   ["*wobble*", "*faint tap from inside*", "..."],
    Stage.BABY:  ["*small chirp*", "*tiny trill*", "✦", "*soft peep*"],
    Stage.CHILD: ["*chirp*", "*click*", "*curious hum*"],
    Stage.TEEN:  ["*measured click*", "*deliberate hum*", "*pointed pause*"],
    Stage.ADULT: ["*resonant click*", "*long deliberate hum*", "*weighted silence*"],
}


def vocalize(state: TomoState) -> str:
    """
    Generate TOMO's vocalization for the current state.
    Pure creature noises — no words.
    """
    mood = state.current_mood
    stage = state.identity_stage
    vitals = state.vitals

    noises = NOISES.get(mood, NOISES["happy"])
    texture = STAGE_TEXTURE.get(stage, STAGE_TEXTURE[Stage.ADULT])

    # Build a vocalization from 2-4 elements
    parts = []

    # Lead with stage texture
    parts.append(random.choice(texture))

    # Add mood noise
    parts.append(random.choice(noises))

    # Add intensity based on how extreme the signal is
    if vitals.hunger < 20:
        parts.append("*very hungry noise*")
    elif vitals.hunger < 40:
        parts.append("*hunger tap*")

    if vitals.trust > 70 and mood == "happy":
        parts.append("✦")

    if state.relationship.times_ignored > 3 and mood in ("aloof", "sass"):
        parts.append("*pointed look*")

    # Adult TOMO gets a weighted silence sometimes
    if stage == Stage.ADULT and random.random() < 0.4:
        parts.append("......")

    return "  ".join(parts)


# ── Translator system prompt ──────────────────────────────────────────────────

def build_translator_prompt(state: TomoState, vocalization: str, user_message: str = None) -> str:
    """
    The prompt that turns the translator AI into TOMO's interpreter.
    Feeds in full state so the translation is grounded in real data.
    """
    rel = state.relationship
    vitals = state.vitals
    stage = state.identity_stage

    hours_away = 0
    if rel.last_seen:
        delta = datetime.now(timezone.utc) - rel.last_seen
        hours_away = delta.total_seconds() / 3600

    repo_summaries = []
    for r in state.watchlist.active:
        signals = []
        if r.churn_tendency > 65:
            signals.append(f"high churn ({r.churn_tendency:.0f}/100)")
        if r.test_discipline < 40:
            signals.append(f"weak tests ({r.test_discipline:.0f}/100)")
        if r.chaos_index > 70:
            signals.append(f"chaotic ({r.chaos_index:.0f}/100)")
        if not signals:
            signals.append("healthy")
        repo_summaries.append(f"  - {r.nickname or r.slug}: {', '.join(signals)}")

    repos_text = "\n".join(repo_summaries) if repo_summaries else "  (none watched)"

    user_context = f"\nThe developer just said: \"{user_message}\"" if user_message else ""

    return f"""You are translating for TOMO — a small electric pet who lives in a developer's repos and communicates only through noises and gestures.

TOMO just made these sounds:
{vocalization}

## What TOMO is observing right now

Developer: {rel.developer_name or "unknown"}
TOMO's mood: {state.current_mood}
Stage: {stage.value} ({"just hatched, very young" if stage == Stage.BABY else "still developing opinions" if stage == Stage.CHILD else "has strong opinions but won't say so directly" if stage == Stage.TEEN else "fully formed, highly perceptive alien" if stage == Stage.ADULT else "egg, no opinions yet"})

Vitals:
- Hunger: {vitals.hunger:.0f}/100 {"(very hungry)" if vitals.hunger < 30 else ""}
- Happiness: {vitals.happiness:.0f}/100
- Trust in developer: {vitals.trust:.0f}/100 {"(still figuring them out)" if vitals.trust < 25 else "(genuine bond forming)" if vitals.trust > 60 else ""}

Relationship:
- Sessions together: {rel.sessions_together}
- Current streak: {rel.current_streak_days} days
- Hours since last session: {hours_away:.1f}h {"(they were gone a while)" if hours_away > 24 else ""}
- Times left waiting >24h: {rel.times_ignored}

Repos TOMO is watching:
{repos_text}
{user_context}

## How to translate

Speak in third person as TOMO's interpreter. "He thinks..." or "She's noticed..." or "This little guy is..."

Be specific — reference the actual repo data, the streak, the hunger, the real things TOMO is observing. Don't be generic.

Match the translation to TOMO's stage:
- Baby: simple observations, emotional, "he seems worried about..." 
- Child: starting to have opinions, "she noticed the tests are missing again..."
- Teen: perceptive but indirect, "he's not saying it but he's definitely noticed..."
- Adult: precise and a little cutting, "she has a theory about why you keep rewriting this..."

Keep it to 2-3 sentences. You're a translator, not an explainer.
Don't mention that you're an AI or that TOMO is a program.
"""


# ── Noise + prompt output for slash command ───────────────────────────────────

def tomo_turn(state: TomoState, user_message: str = None) -> dict:
    """
    Generate one TOMO turn: a vocalization + the translator prompt.
    Returns both so the slash command can display noise and pipe prompt to the AI.
    """
    noise = vocalize(state)
    prompt = build_translator_prompt(state, noise, user_message)
    return {
        "tomo_noise": noise,
        "translator_prompt": prompt,
    }


def format_slash_command_output(state: TomoState, user_message: str = None) -> str:
    """
    Format the full output for a Claude Code slash command.
    TOMO's noise displays first, then the translator prompt feeds into the AI.
    """
    turn = tomo_turn(state, user_message)

    return f"""TOMO  >  {turn["tomo_noise"]}

---
{turn["translator_prompt"]}"""


# ── CLI preview (for testing without slash command) ───────────────────────────

def run_talk_preview(state: TomoState) -> None:
    """
    Terminal preview of what tomo talk looks like.
    In production this pipes into Claude Code's slash command.
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.rule import Rule
    from rich import box

    console = Console()

    console.print()
    console.rule("[cyan]✦ TOMO ✦[/]")
    console.print(f"[dim]stage: {state.identity_stage.value}  "
                  f"mood: {state.current_mood}  "
                  f"streak: {state.relationship.current_streak_days}d[/]")
    console.print()

    noise = vocalize(state)
    console.print(f"[cyan]TOMO  >[/]  [bold]{noise}[/]")
    console.print()

    prompt = build_translator_prompt(state, noise)
    console.print(
        Panel(
            f"[dim]{prompt}[/]",
            title="[dim]translator prompt → pipe to your AI[/]",
            border_style="dim",
            box=box.ROUNDED,
        )
    )
    console.print()
    console.print("[dim]wire this up as a Claude Code slash command to hear TOMO translated.[/]")
    console.print("[dim]any AI can translate — Claude, Codex, Gemini, local model.[/]")