# Contributing to TOMO

Thanks for wanting to feed the creature.

The README already lists [good places to start](README.md#contributing) at a
high level — new evolution stages, new quips, new metrics, new translator
prompts. This file covers the practical bits.

---

## Dev setup

```bash
git clone https://github.com/YG3-ai/TOMO.git
cd TOMO
python3 -m venv venv
source venv/bin/activate
pip install -e '.[quill]'
```

`pip install -e .` is an editable install — your edits take effect immediately
without reinstalling. The `[quill]` extra pulls in `quill-mcp` so
`tomo quill` works (requires both `claude` and `codex` CLIs on PATH).

Sanity check:

```bash
tomo hello
tomo live
```

---

## Where things live

See [TECHNICAL.md](TECHNICAL.md) for the full state model, mood priority,
scanner internals, and a code-layout map. Skim it once before your first PR
and you'll know which file to touch.

The TL;DR:

| You want to... | Touch |
|---|---|
| add a quip | [src/tomo/sprites.py](src/tomo/sprites.py) |
| add an animation frame | [src/tomo/sprites.py](src/tomo/sprites.py) |
| add a CLI command | [src/tomo/main.py](src/tomo/main.py) |
| add a mood signal | [src/tomo/mood.py](src/tomo/mood.py) |
| add a scan metric | [src/tomo/scan.py](src/tomo/scan.py) |
| change the live TUI | [src/tomo/display.py](src/tomo/display.py) |
| add state fields | [src/tomo/state.py](src/tomo/state.py) |
| change Quill framing | [src/tomo/quill.py](src/tomo/quill.py) |

---

## House style

- **Mood is always derived from state.** Never store `current_mood` as
  source-of-truth — `derive_mood()` runs fresh on every change.
- **State writes go through `save_state()`.** Don't write to `state.json`
  directly; that bypasses Pydantic validation.
- **New commands follow the `_session_start()` pattern** — tick vitals,
  check evolution, save, then do the thing.
- **Keep the personality arc intact.** Baby says `"hi!"`. Adult says
  `"...adequate."` Sweet-to-aloof. If a quip would feel out of voice for
  its stage, leave it out.

---

## Pull requests

- Open an issue first if it's a bigger feature than a quip or a fix.
- Keep PRs focused — one feature or fix per PR.
- Match existing code style; no new deps without discussing.
- If you change behavior, mention it in the PR description.

---

## Issues

File one at https://github.com/YG3-ai/TOMO/issues. Useful issue types:

- **Bug** — paste the traceback if you have one, plus your `tomo --version`
  (or pip show output) and OS.
- **Feature idea** — what should TOMO *do* differently? Concrete behavior
  beats abstract goals.
- **Quip request** — surprisingly the most common.

---

## Code of conduct

Be kind to TOMO and to each other. TOMO is sensitive and so are we.
