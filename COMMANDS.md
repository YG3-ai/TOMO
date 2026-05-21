# TOMO command reference

All commands run a quiet "session start" first: vitals tick, evolution
checks, state saves. So just opening TOMO is part of the relationship.

---

## Core

### `tomo`

Bare invocation. Drops into the animated idle view for ~6 seconds, then exits.
The default greeting.

### `tomo hello` (alias `tomo hi`)

Introduce yourself. Prompts for your name on first run.

### `tomo status`

Full status panel: sprite, vitals (hunger / happiness / trust / energy),
mood, current stage, relationship summary, watched-repo list.

### `tomo live`

Persistent body-double window. Sprite animates continuously, vitals decay,
quips rotate, repo concerns surface, mid-session evolutions trigger
celebrations.

Keybinds:
- `f` or **click** — feed (+40 hunger, +5 happiness)
- `p` — play (+15 happiness, +3 trust)
- `q` or Ctrl-C — quit

Flags:
- `--decay-seconds N` (default 30) — how often vitals tick down
- `--quip-seconds N` (default 5) — how often the idle quip rotates
- `--scan-minutes N` (default 10) — auto-scan watched repos every N minutes; `0` disables

---

## The watchlist

TOMO watches up to 5 active repos. Pausing preserves history. Each watched
repo gets a fingerprint that decays without scans.

### `tomo watch [path]`

Add a repo to the watchlist. Defaults to current directory.

Flags:
- `--name`, `-n` — nickname for the repo
- `--only "src,tests"` — whitelist subdirectories to scan
- `--ignore "docs,vendor"` — blacklist subdirectories from scanning

### `tomo list`

Show all watched repos with their fingerprints.

### `tomo pause [path]`

Hibernate a repo. History preserved; TOMO stops worrying about it.

### `tomo ignore [path]`

Remove a repo entirely from the watchlist.

### `tomo scope [target]`

Show or update scan scope. Without args, lists scope for every watched repo.

Flags:
- `--only "src,tests"` — replace whitelist
- `--ignore "docs,vendor"` — replace blacklist
- `--clear` — reset to whole-repo

Target can be a path, nickname, or slug.

---

## Scanning

### `tomo scan [target]`

Compute real health metrics from git + filesystem and update watched-repo
fingerprints. Without args, scans every active repo.

Metrics (all 0–100):

| Metric | What it measures |
|---|---|
| `test_discipline` | share of source files that look like tests |
| `churn_tendency` | how often the same files keep getting rewritten |
| `commit_hygiene` | quality of recent commit messages |
| `chaos_index` | inverse composite of the other three |

Scope is honored: `test_discipline` and `churn_tendency` are computed only
over the in-scope paths. `commit_hygiene` stays repo-wide because commit
messages aren't path-specific.

---

## Talking

### `tomo talk`

Preview mode — shows what TOMO is "thinking" without an AI in the loop.

### `tomo talk --raw [message]`

Output TOMO's vocalization plus a translator prompt grounded in real state.
Optional message becomes the developer's framing for the AI.

```bash
tomo talk --raw "why are my tests failing" | claude
tomo talk --raw                          | codex
tomo talk --raw                          | ollama run llama3
```

The prompt is AI-agnostic. Different AIs may hear different things — that's
the seam, and it's intentional.

---

## Dual-agent review

### `tomo quill [aspect]`

Requires `pip install 'tomopet[quill]'` and both `claude` and `codex` CLIs
on PATH.

Summons [Quill](https://github.com/YG3-ai/quill) for a mosaic review: two
voices, parallel, cross-reviewed, seams preserved. TOMO builds the framing
automatically from current state (vitals, watched-repo fingerprints,
relationship pattern).

Flags:
- `--meta` — also show the mosaic plan, slices, and cross-review flags

The aspect argument is optional. Examples: `tomo quill testing`,
`tomo quill churn`, `tomo quill hygiene`. Omit for a holistic review.

Each consultation is saved as a notable moment.

---

## Living with TOMO

### `tomo feed`

Feed TOMO. Hunger +40, happiness +5.

### `tomo play`

Play with TOMO. Happiness +15, trust +3. Game varies by stage.

### `tomo history [-n N]`

Timeline of notable moments — evolutions, Quill consultations, milestones.
Default last 20.

### `tomo animate-cmd`

Watch TOMO idle for `--seconds N` (default 6). Useful for testing animation
changes.
