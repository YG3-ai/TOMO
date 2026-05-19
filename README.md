# ✦ TOMO

> *the electric pet that lives in your repos*

TOMO is a terminal companion that watches your codebases and develops a personality over time. One creature per developer, multiple watched repos. Grows from egg to opinionated adult alien. Makes noises. Needs an interpreter.

```
   ∧▄▄▄∧
  (◕ ᴗ ◕)    *chirp* ✦ *trill*
   ╰─▾─╯
    ╽ ╽
```

---

## Why TOMO?

Most dev tools are stateless. Every session starts cold. TOMO fixes that — not with fuzzy conversational memory, but with a structured state file that travels with your workflow. TOMO knows your streak, your repos' health history, and whether you've been neglecting your tests.

It's also a creature that lives in your terminal and has feelings about your commit hygiene.

---

## Install

```bash
pip install tomo
```

---

## Quick start

```bash
tomo hello                       # introduce yourself
tomo watch --only src,tests      # add current repo, scoped to what matters
tomo scan                        # measure repo health for real
tomo                             # see TOMO front and center
tomo live                        # persistent body-double window
```

---

## Body-double mode

```bash
tomo live
```

A persistent window with TOMO animating in it. Keep it open in a tmux pane or
a second terminal. Vitals tick down while you work — feed him to keep him
content. Click TOMO or press `f` to feed, `p` to play, `q` to quit.

Every ~10 minutes (configurable) TOMO quietly re-scans your watched repos and
starts surfacing concerns in his speech bubble — "*worried glance — auth/
tests?*" — based on what's actually changing in git.

```bash
tomo live --decay-seconds 60     # slow the hunger drain
tomo live --quip-seconds 8       # change quip cadence
tomo live --scan-minutes 0       # disable auto-scan
```

For ADHD coding sessions: he's there, animating, present. Not nagging. Just
working alongside you. When something's actually wrong with your code he'll
say so.

---

## Commands

```bash
tomo                          # bare invocation — animated idle view
tomo hello                    # introduce yourself to TOMO
tomo live                     # persistent body-double window (recommended)
tomo status                   # TOMO + all repo health at a glance
tomo watch [path]             # add a repo to the watchlist
tomo watch --only src,tests   # scope scanning to specific subdirs
tomo watch --ignore docs,gen  # exclude subdirs from scanning
tomo scope                    # list scope settings for all watched repos
tomo scope <repo> --only ...  # update scope on a watched repo
tomo scope <repo> --clear     # reset scope to whole repo
tomo scan                     # scan all watched repos for real health metrics
tomo scan <repo>              # scan just one
tomo list                     # see all watched repos and their fingerprints
tomo pause                    # hibernate a repo without losing history
tomo ignore                   # remove a repo entirely
tomo feed                     # feed TOMO
tomo play                     # play with TOMO (boosts happiness + trust)
tomo talk                     # see what TOMO is thinking (preview mode)
tomo talk --raw "msg"         # raw output for piping to any AI
```

---

## Scoping what TOMO watches

By default TOMO scans every source file in a watched repo (skipping the obvious
junk: `node_modules`, `venv`, `dist`, etc.). For larger repos that's noisy —
docs, examples, vendored code, and generated output all pollute the metrics.

Use `--only` to whitelist specific subdirectories, or `--ignore` to blacklist
them:

```bash
# Only consider src/ and tests/ for this repo
tomo watch ~/code/big-project --only src,tests

# Or skip just the noisy bits
tomo watch ~/code/big-project --ignore docs,examples,vendor,generated

# Update after the fact
tomo scope big-project --only src,tests,packages
tomo scope big-project --clear   # back to whole-repo
```

Both `churn_tendency` and `test_discipline` honor the scope, so the metrics
reflect the part of the codebase you actually care about. `commit_hygiene`
stays repo-wide because commit messages aren't path-specific.

---

## Talking to TOMO

TOMO doesn't speak English. TOMO makes noises. You need a translator.

`tomo talk --raw` outputs TOMO's vocalization + a translator prompt grounded in your real repo data. Pipe it to any AI:

```bash
# Claude Code
tomo talk --raw "why are my tests failing" | claude

# Codex
tomo talk --raw | codex

# Gemini
tomo talk --raw | gemini

# Local model
tomo talk --raw | ollama run llama3
```

The AI translates in third person. TOMO makes the noise. The AI gives it meaning:

```
TOMO  >  *chirp*  *uneasy trill*  ......

Claude >  "This little guy has been staring at your auth module
           for three days. He wants to know why you keep
           rewriting it. He seems genuinely concerned."
```

The translator prompt is AI-agnostic — same TOMO, any interpreter. Different AIs may hear different things in the same noise. That's a feature.

### Claude Code slash command (optional convenience)

Drop `.claude/commands/tomo.md` from this repo into your project and `/tomo` becomes a native slash command in Claude Code.

---

## How TOMO works

TOMO lives in `~/.tomo/state.json` — one creature, persistent across all sessions and repos.

Each watched repo gets its own health fingerprint in `~/.tomo/repos/`. TOMO builds a personality fingerprint per repo over time — churn tendency, test discipline, chaos index — and its behavior reflects what it has observed, without directly mirroring metrics back at you.

### Evolution stages

| Stage   | Unlocks when...                          | Personality                        |
|---------|------------------------------------------|------------------------------------|
| 🥚 Egg   | fresh install                            | wobbles, no opinions               |
| 🌱 Baby  | first session                            | sweet, clingy, trusts easily       |
| 👽 Child | 5+ sessions, 2+ days                    | forming opinions, mild sass        |
| 😒 Teen  | 15+ sessions, 7+ days, some trust built | perceptive, indirect, aloof        |
| 🛸 Adult | 30+ sessions, 21+ days, real trust      | haughty alien, rare approval lands |

TOMO evolves on time + relationship, not code quality. Show up consistently.

### Mood system

Mood is always derived from real state — never stored. Priority order:

1. **dormant** — very low energy
2. **hungry** — hasn't seen you in a while
3. **anxious** — bad repo health signals
4. **aloof** — neglect + growing sass
5. **impressed** — rare, high trust, adult only, 20% chance even then
6. **sass** — mild neglect, teen/adult
7. **happy** — default

### The watchlist

TOMO watches up to 5 active repos. Pausing preserves history without worry. `times_ignored` increments when you leave for more than 24 hours — it feeds the Charizard energy.

---

## File structure

```
~/.tomo/
  state.json        ← TOMO's global state (one creature)
  repos/
    project.json    ← per-repo health fingerprints
```

Nothing goes in your repos. TOMO lives with you, not in your codebases.

---

## Philosophy

TOMO is closer to A2A than MCP — not a tool you call, a persistent agent that observes your workflow over time. The state file is TOMO's memory: inspectable, correctable, version-controllable. No black boxes.

Pairs naturally with [Quill](https://github.com/YG3-ai/quill) — when TOMO detects bad repo health it can summon Quill's two-AI deliberation for a second opinion.

---

## Built with

- [Rich](https://github.com/Textualize/rich) — terminal rendering + the Live TUI
- [Typer](https://typer.tiangolo.com) — CLI
- [Pydantic](https://docs.pydantic.dev) — state modeling
- `git` (via subprocess) — repo scanning

---

## Roadmap

- [x] `tomo scan` — real repo health analysis (test discipline, churn, commit hygiene, chaos)
- [x] `tomo live` — persistent body-double window with mouse clicks + auto-scan
- [x] Scoping — `--only` / `--ignore` for noisy repos
- [ ] Quill integration — TOMO summons a second opinion on bad health signals
- [ ] Secret detection in scan
- [ ] Pixel art rendering via Sixel/Kitty for supported terminals
- [ ] `tomo history` — notable moments timeline
- [ ] `tomo game` — mini games that build trust

---

## License

MIT — built by [YG3](https://github.com/YG3-ai)