"""
TOMO mood engine.
Mood is always derived from vitals + relationship + repo health.
Never stored — always computed fresh.
TOMO adapts to your repo's personality but doesn't directly mirror it.
"""

from datetime import datetime, timezone
from tomo.state import TomoState
from tomo.sprites import Stage


def derive_mood(state: TomoState) -> str:
    """
    Compute TOMO's current mood from state.
    Returns one of: happy, hungry, anxious, aloof, impressed, dormant, sass
    """
    vitals = state.vitals
    rel = state.relationship
    stage = state.identity_stage

    # Dormant — very low energy or trust broken
    if vitals.energy < 10:
        return "dormant"

    # Hungry — top priority signal
    if vitals.hunger < 25:
        return "hungry"

    # Egg doesn't have opinions yet
    if stage == Stage.EGG:
        return "happy"

    # Baby is mostly just happy or hungry
    if stage == Stage.BABY:
        return "hungry" if vitals.hunger < 40 else "happy"

    # From child onwards — more nuanced
    # Aloof — teen/adult, high sass, been ignored
    if stage in (Stage.TEEN, Stage.ADULT):
        if rel.times_ignored > 3 and state.personality.sass > 60:
            return "aloof"

    # Anxious — repo health problems detected
    # Check across watched repos for bad signals
    any_anxiety = False
    for repo in state.watchlist.active:
        if repo.churn_tendency > 70:
            any_anxiety = True
        if repo.test_discipline < 30:
            any_anxiety = True
        if repo.chaos_index > 75:
            any_anxiety = True

    if any_anxiety and vitals.happiness < 60:
        return "anxious"

    # Impressed — rare, trust must be high, happiness high
    if vitals.trust > 80 and vitals.happiness > 85 and stage == Stage.ADULT:
        # Only 20% chance even when conditions are met — keeps it rare
        import random
        if random.random() < 0.2:
            return "impressed"

    # Sass — teen/adult with moderate neglect
    if stage in (Stage.TEEN, Stage.ADULT) and rel.times_ignored > 1:
        if state.personality.sass > 50:
            return "sass"

    # Default: happy
    return "happy"


def update_vitals_for_session(state: TomoState) -> TomoState:
    """Called at the start of a coding session — TOMO wakes up."""
    now = datetime.now(timezone.utc)

    # Calculate hours since last seen
    hours_away = 0.0
    if state.relationship.last_seen:
        delta = now - state.relationship.last_seen
        hours_away = delta.total_seconds() / 3600

    # Hunger drains over time — 8 hours = empty
    hunger_drain = min(hours_away * 12.5, 100)
    state.vitals.hunger = max(0, state.vitals.hunger - hunger_drain)

    # Session restores energy and happiness
    state.vitals.energy = min(100, state.vitals.energy + 20)
    state.vitals.happiness = min(100, state.vitals.happiness + 10)

    # Hunger restored by presence
    state.vitals.hunger = min(100, state.vitals.hunger + 30)

    # Trust grows slowly with each session
    state.vitals.trust = min(100, state.vitals.trust + 2)

    # Attachment grows
    state.personality.attachment = min(100, state.personality.attachment + 3)

    # Sass grows with age and neglect
    if hours_away > 24:
        state.personality.sass = min(100, state.personality.sass + 5)
        state.relationship.times_ignored += 1

    # Streak tracking
    if state.relationship.last_seen:
        delta_days = (now - state.relationship.last_seen).days
        if delta_days <= 1:
            state.relationship.current_streak_days += 1
        else:
            state.relationship.current_streak_days = 1

    state.relationship.longest_streak_days = max(
        state.relationship.longest_streak_days,
        state.relationship.current_streak_days,
    )

    # Session count
    state.relationship.sessions_together += 1
    state.relationship.last_seen = now

    # Update age
    if state.born_at:
        state.age_days = (now - state.born_at).total_seconds() / 86400

    # Update mood
    state.current_mood = derive_mood(state)

    return state


def check_evolution(state: TomoState) -> tuple[TomoState, bool]:
    """
    Check if TOMO should evolve.
    Returns (updated_state, did_evolve).
    Evolution is time + milestones, not just code health.
    """
    stage = state.identity_stage
    sessions = state.relationship.sessions_together
    age = state.age_days
    trust = state.vitals.trust
    did_evolve = False

    new_stage = stage

    if stage == Stage.EGG and sessions >= 1:
        new_stage = Stage.BABY
        did_evolve = True

    elif stage == Stage.BABY and sessions >= 5 and age >= 2:
        new_stage = Stage.CHILD
        did_evolve = True
        state.evolution.milestones_hit.append("hatched_into_child")

    elif stage == Stage.CHILD and sessions >= 15 and age >= 7 and trust >= 20:
        new_stage = Stage.TEEN
        did_evolve = True
        state.evolution.milestones_hit.append("became_teen")

    elif stage == Stage.TEEN and sessions >= 30 and age >= 21 and trust >= 50:
        new_stage = Stage.ADULT
        did_evolve = True
        state.evolution.milestones_hit.append("became_adult")

    if did_evolve:
        state.identity_stage = new_stage
        # Hint at next stage
        hints = {
            Stage.BABY:  "keep showing up...",
            Stage.CHILD: "earn some trust...",
            Stage.TEEN:  "consistency matters...",
            Stage.ADULT: "you made it.",
        }
        state.evolution.next_evolution_hint = hints.get(new_stage, "")

    return state, did_evolve
