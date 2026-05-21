# TOMO internals

This file is for people who want to look inside TOMO — fork him, mutate his
state, write new metrics, ship new evolution stages. For everyday use see
[README.md](README.md); for the full command list see [COMMANDS.md](COMMANDS.md).

---

## File layout on disk

```
~/.tomo/
  state.json          ← TOMO's global state (one creature)
  repos/
    <slug>.json       ← per-repo health (not used yet, reserved)
```

Nothing goes inside your repos. TOMO travels with the developer, not the
codebase. `state.json` is human-readable; mutating it by hand is supported.

---

## State model

Defined in [src/tomo/state.py](src/tomo/state.py) using Pydantic. Top-level:

```python
class TomoState(BaseModel):
    identity_stage: Stage          # egg | baby | child | teen | adult
    age_days: float
    born_at: datetime
    personality: Personality
    vitals: Vitals
    relationship: Relationship
    watchlist: Watchlist
    evolution: Evolution
    current_mood: str              # derived, never trusted as source-of-truth
```

### Vitals
```python
hunger: float      # 0–100, drains over time without sessions
happiness: float   # 0–100, restored by play + feed
energy: float      # 0–100, restored by sessions
trust: float       # 0–100, slow-growing, barely decreases — the deep bond
```

### Personality
```python
curiosity: float   # how much TOMO notices things
sass: float        # starts low, grows with age + neglect
patience: float    # decreases if you keep making the same mistakes
attachment: float  # grows with sessions together
```

### RepoFingerprint
```python
churn_tendency: float    # 0=stable, 100=chaotic rewriter
test_discipline: float   # 0=no tests, 100=test-obsessed
commit_hygiene: float    # 0=disaster, 100=pristine
chaos_index: float       # composite vibe of this codebase
scan_paths: list[str]    # whitelist; empty = whole repo
scan_ignore: list[str]   # blacklist; additive to built-in skips
last_scanned: datetime | None
```

### NotableMoment
```python
timestamp: datetime
repo: str           # nickname/slug, or "" for global
type: str           # "evolved", "quill_consultation:<aspect>", etc.
memo: str
```

---

## Mood derivation

Defined in [src/tomo/mood.py](src/tomo/mood.py). Always derived, never stored
as source-of-truth. Priority order (first match wins):

1. **dormant** — `energy < 10`
2. **hungry** — `hunger < 25`
3. **egg** — always `happy` (no opinions yet)
4. **baby** — `happy` or `hungry` only
5. **aloof** — teen/adult, `times_ignored > 3`, `personality.sass > 60`
6. **anxious** — any watched repo has `churn > 70` or `test_discipline < 30` or `chaos > 75`, AND `happiness < 60`
7. **impressed** — adult only, `trust > 80` AND `happiness > 85`, 20% chance even then
8. **sass** — teen/adult, `times_ignored > 1`, `personality.sass > 50`
9. **happy** — default

---

## Evolution

Defined in `check_evolution()` in `mood.py`. Time + relationship, not code
quality.

| Stage  | Sessions | Age (days) | Trust |
|--------|----------|------------|-------|
| Egg    | 0        | —          | —     |
| Baby   | 1+       | —          | —     |
| Child  | 5+       | 2+         | —     |
| Teen   | 15+      | 7+         | 20+   |
| Adult  | 30+      | 21+        | 50+   |

Evolutions append to `state.evolution.milestones_hit` AND
`state.relationship.notable_moments` (visible via `tomo history`).

---

## Scanner

Defined in [src/tomo/scan.py](src/tomo/scan.py).

### `test_discipline`
Walk in-scope source files. Test patterns: paths containing `test`, `tests`,
`__tests__`, `spec`, `specs`, or filenames matching `test_*.py`, `*_test.py`,
`*_test.go`, `*.test.{ts,tsx,js,jsx}`, `*.spec.{...}`, `*Test.java`, etc.
Ratio of tests-to-source, scaled so 30% test files = 100 score.

### `churn_tendency`
`git log -n200 --name-only` over in-scope paths. Compute (total changes /
unique files). 1.0 = no churn → 0 score. 3.0+ → 100 score.

### `commit_hygiene`
Last 100 commit messages, repo-wide. Penalize short messages and low-effort
ones (`wip`, `fix`, `tmp`, etc.).

### `chaos_index`
`(100 - test_discipline + churn_tendency + 100 - commit_hygiene) / 3`.

### Skipped dirs (built-in)
`.git`, `node_modules`, `venv`, `.venv`, `__pycache__`, `dist`, `build`,
`target`, `out`, `.next`, `.nuxt`, `vendor`, `.tox`, `.pytest_cache`,
`.mypy_cache`, `coverage`, `Pods`, `DerivedData`. Plus anything in
`scan_ignore` for the repo.

---

## Quill integration

Defined in [src/tomo/quill.py](src/tomo/quill.py). Builds a markdown framing
from TOMO state and calls `quill_mcp.mosaic.run_mosaic` directly (no MCP
client; just an import + `asyncio.run`).

Mosaic returns a dict with `task`, `plan`, `slices`, `cross_review_flags`,
`voice_map`, `assembled_response`. TOMO surfaces `assembled_response`; the
rest is available via `tomo quill --meta`.

Requires both `claude` and `codex` CLIs on PATH. Lazy import keeps the base
`tomopet` install slim.

---

## Code layout

```
src/tomo/
  __init__.py     version
  main.py         CLI entry (Typer commands)
  state.py        Pydantic models + persistence helpers
  mood.py         derive_mood, update_vitals_for_session, check_evolution
  scan.py         repo health metrics (test/churn/hygiene/chaos)
  quill.py        Quill framing + run_quill_consultation
  display.py      Rich rendering, animate(), run_live_session()
  sprites.py      ASCII sprites, mood expressions, QUIPS dict
  talk.py         vocalization + translator prompt builder
```

**Key principle:** mood is always *derived* from state, never stored as
source-of-truth. `derive_mood()` runs fresh on every state change.

**State mutations** always go through `save_state(state)`. Don't write to
`state.json` directly — that bypasses Pydantic validation.

**Adding new quips** goes in `sprites.py`'s `QUIPS` dict, keyed by `Stage`
and mood. Keep the stage/mood voice consistent — baby says `"hi!"`, adult
says `"...adequate."` That arc is the personality.

**Adding new commands** in `main.py` follow the `_session_start()` pattern
(tick vitals, check evolution, save) before doing their thing.
