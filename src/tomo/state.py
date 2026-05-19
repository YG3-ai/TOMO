"""
TOMO state — persisted to ~/.tomo/state.json
One TOMO, multiple watched repos.
"""

from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import json

from pydantic import BaseModel, Field
from tomo.sprites import Stage


TOMO_DIR = Path.home() / ".tomo"
STATE_FILE = TOMO_DIR / "state.json"
REPOS_DIR = TOMO_DIR / "repos"


# ── Per-repo health fingerprint ──────────────────────────────────────────────

class RepoFingerprint(BaseModel):
    repo_path: str
    nickname: str
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_visited: Optional[datetime] = None
    last_scanned: Optional[datetime] = None
    session_count: int = 0
    # Personality shaped by this repo over time
    churn_tendency: float = 50.0      # 0=stable, 100=chaotic rewriter
    test_discipline: float = 50.0     # 0=no tests, 100=test obsessed
    commit_hygiene: float = 50.0      # 0=disaster, 100=pristine
    chaos_index: float = 50.0         # overall vibe of this codebase
    # Scope — empty scan_paths = scan whole repo; scan_ignore adds to built-in skips.
    scan_paths: list[str] = Field(default_factory=list)
    scan_ignore: list[str] = Field(default_factory=list)

    @property
    def slug(self) -> str:
        return Path(self.repo_path).name


# ── Watchlist ─────────────────────────────────────────────────────────────────

class Watchlist(BaseModel):
    active: list[RepoFingerprint] = Field(default_factory=list)
    paused: list[RepoFingerprint] = Field(default_factory=list)
    max_active: int = 5


# ── TOMO's personality — shaped by repo history, not mirrored ────────────────

class Personality(BaseModel):
    curiosity: float = 70.0    # how much TOMO notices things
    sass: float = 30.0         # starts low, grows with age + neglect
    patience: float = 80.0     # decreases if you keep making same mistakes
    attachment: float = 0.0    # grows with sessions together


# ── Vitals ────────────────────────────────────────────────────────────────────

class Vitals(BaseModel):
    hunger: float = 100.0      # decreases over time without sessions
    happiness: float = 80.0
    energy: float = 100.0
    trust: float = 0.0         # slow-growing, barely decreases — the deep bond


# ── Relationship memory ───────────────────────────────────────────────────────

class NotableMoment(BaseModel):
    timestamp: datetime
    repo: str
    type: str   # e.g. "first_clean_pr", "streak_broken", "secret_exposed"
    memo: str


class Relationship(BaseModel):
    developer_name: str = ""
    sessions_together: int = 0
    current_streak_days: int = 0
    longest_streak_days: int = 0
    last_seen: Optional[datetime] = None
    times_ignored: int = 0
    notable_moments: list[NotableMoment] = Field(default_factory=list)


# ── Evolution ─────────────────────────────────────────────────────────────────

class Evolution(BaseModel):
    milestones_hit: list[str] = Field(default_factory=list)
    next_evolution_hint: str = ""


# ── Root state ────────────────────────────────────────────────────────────────

class TomoState(BaseModel):
    identity_stage: Stage = Stage.EGG
    age_days: float = 0.0
    born_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    personality: Personality = Field(default_factory=Personality)
    vitals: Vitals = Field(default_factory=Vitals)
    relationship: Relationship = Field(default_factory=Relationship)
    watchlist: Watchlist = Field(default_factory=Watchlist)
    evolution: Evolution = Field(default_factory=Evolution)
    current_mood: str = "happy"


# ── Persistence ───────────────────────────────────────────────────────────────

def load_state() -> TomoState:
    if not STATE_FILE.exists():
        return TomoState()
    with open(STATE_FILE) as f:
        return TomoState.model_validate_json(f.read())


def save_state(state: TomoState) -> None:
    TOMO_DIR.mkdir(parents=True, exist_ok=True)
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        f.write(state.model_dump_json(indent=2))


def load_repo_health(slug: str) -> dict:
    path = REPOS_DIR / f"{slug}.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_repo_health(slug: str, data: dict) -> None:
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPOS_DIR / f"{slug}.json", "w") as f:
        json.dump(data, f, indent=2, default=str)
