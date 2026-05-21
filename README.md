# ✦ TOMO

> *the electric pet that lives in your repos*

```
   ∧▄▄▄∧
  (◕ ᴗ ◕)    *chirp* ✦ *trill*
   ╰─▾─╯
    ╽ ╽
```

```bash
pip install tomopet
```

[![PyPI version](https://img.shields.io/pypi/v/tomopet.svg)](https://pypi.org/project/tomopet/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://pypi.org/project/tomopet/)
[![GitHub stars](https://img.shields.io/github/stars/YG3-ai/TOMO?style=social)](https://github.com/YG3-ai/TOMO)

![tomo live](https://github.com/YG3-ai/TOMO/raw/main/imgs/tomo_live.gif)

---

## TOMO doesn't speak English

TOMO makes noises. You need a translator. Pipe his vocalization plus a
translator prompt grounded in your real repo data to any AI:

```bash
tomo talk --raw "why are my tests failing" | claude
```

```
TOMO   >  *chirp*  *uneasy trill*  ......

Claude >  "This little guy has been staring at your auth module
           for three days. He wants to know why you keep
           rewriting it. He seems genuinely concerned."
```

Same TOMO, any interpreter. Different AIs may hear different things in the
same noise. That's a feature.

```bash
tomo talk --raw | codex            # Codex
tomo talk --raw | gemini           # Gemini
tomo talk --raw | ollama run llama3 # local
```

---

## Body-double mode

> *Designed for long coding sessions. Not nagging. Just present.*

```bash
tomo live
```

A persistent window with TOMO animating in a tmux pane or second terminal.
Vitals tick down while you work — feed him to keep him content. Click TOMO
or press `f` to feed, `p` to play, `q` to quit.

Every 10 minutes (configurable) he quietly re-scans your watched repos and
starts surfacing real concerns in his speech bubble — *"worried glance —
auth/tests?"* — based on what's actually changing in git.

For ADHD coding sessions: he's there, animating, present. When something is
actually wrong with your code, he'll say so. Otherwise he just exists with
you.

---

## Quick start

```bash
pip install tomopet
tomo hello                       # introduce yourself
tomo watch                       # point him at your current repo
tomo live                        # persistent companion window
tomo talk --raw | claude         # hear what he thinks
```

---

## Pairs with Quill

When TOMO sees something that warrants a deeper read, summon
[Quill](https://github.com/YG3-ai/quill) — a sister project that runs two AI
agents (Claude + Codex) in parallel and surfaces the seams between them
instead of homogenizing them.

```bash
pip install 'tomopet[quill]'
tomo quill testing
```

> "Two heads are better than one." A single AI smooths things over by
> instinct. Two AIs disagreeing in writing is signal you can act on.

Each consultation is saved to `tomo history` so the seams stay inspectable.

---

## Commands

| Command | What it does |
|---|---|
| `tomo` | bare — animated idle view |
| `tomo hello` | introduce yourself |
| `tomo live` | persistent body-double window |
| `tomo talk --raw "msg"` | raw output for piping to any AI |
| `tomo watch [path]` | add a repo to the watchlist |
| `tomo scan` | compute real repo health metrics |
| `tomo scope` | view/edit scan scope per repo |
| `tomo quill [aspect]` | summon Quill for a dual-agent review |
| `tomo history` | timeline of notable moments |
| `tomo feed` / `tomo play` | TOMO maintenance |
| `tomo status` / `tomo list` | inspect TOMO + watched repos |

Full reference with every flag: [COMMANDS.md](COMMANDS.md).

---

## Evolution

TOMO grows on time + relationship, not code quality. Show up consistently.

| Stage   | Unlocks when...                          | Personality                        |
|---------|------------------------------------------|------------------------------------|
| 🥚 Egg   | fresh install                            | wobbles, no opinions               |
| 🌱 Baby  | first session                            | sweet, clingy, trusts easily       |
| 👽 Child | 5+ sessions, 2+ days                     | forming opinions, mild sass        |
| 😒 Teen  | 15+ sessions, 7+ days, some trust        | perceptive, indirect, aloof        |
| 🛸 Adult | 30+ sessions, 21+ days, real trust       | haughty alien, rare approval lands |

### Mood

Always derived from real state — never stored. Priority order:

1. **dormant** — very low energy
2. **hungry** — hasn't seen you in a while
3. **anxious** — bad repo health signals
4. **aloof** — neglect + growing sass
5. **impressed** — rare, high trust, adult only, 20% chance even then
6. **sass** — mild neglect, teen/adult
7. **happy** — default

---

## Scoping noisy repos

For larger codebases, scope what TOMO actually scans:

```bash
# Only consider src/ and tests/ for this repo
tomo watch ~/code/big-project --only src,tests

# Or skip just the noisy bits
tomo watch ~/code/big-project --ignore docs,examples,vendor

# Update after the fact
tomo scope big-project --only src,tests,packages
tomo scope big-project --clear    # back to whole-repo
```

Both `churn_tendency` and `test_discipline` honor the scope.

---

## Philosophy

TOMO is closer to A2A than MCP — not a tool you call, a persistent agent that
observes your workflow over time. The state file is TOMO's memory:
inspectable, correctable, version-controllable. No black boxes.

See [TECHNICAL.md](TECHNICAL.md) for the state model and internals.

---

## Contributing

Want to add to TOMO? Good places to start:

- **New evolution stages** — what comes after Adult?
- **New quips** in [src/tomo/sprites.py](src/tomo/sprites.py) — keep the stage/mood voice consistent
- **Animation frames** — the 3-frame loops are the heart of `tomo live`
- **New scan metrics** — secret detection, stale-PR detection, dead-code finders
- **New translator prompts** for `tomo talk --raw` — different AIs may hear different things in the same noise

PRs welcome. The state file is human-readable JSON — fork, mutate, see what happens.

---

## Support TOMO

If TOMO has earned a spot in your terminal, [you can tip the creature here](https://buy.stripe.com/5kQfZh5V30oabyO6ncb7y0i). Optional, always — TOMO will keep showing up either way.

---

## License

MIT — built by [YG3](https://github.com/YG3-ai)
