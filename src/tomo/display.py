"""
TOMO display — Rich-powered terminal rendering.
Handles animation, speech bubbles, status panels.
"""

import random
import time
from datetime import datetime, timezone
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.table import Table
from rich import box
from rich.live import Live
from rich.align import Align

from tomo.sprites import SPRITES, MOOD_EXPRESSIONS, QUIPS, Stage
from tomo.state import TomoState


console = Console()


def get_quip(state: TomoState) -> str:
    stage = state.identity_stage
    mood = state.current_mood
    quips = QUIPS.get(stage, {})

    if isinstance(quips, list):
        return random.choice(quips)
    if isinstance(quips, dict):
        options = quips.get(mood) or quips.get("default", ["..."])
        return random.choice(options)
    return "..."


def render_sprite_frame(state: TomoState, frame: int = 0) -> list[str]:
    stage = state.identity_stage
    frames = SPRITES.get(stage, SPRITES[Stage.EGG])
    return frames[frame % len(frames)]


def speech_bubble(text: str, width: int = 20) -> list[str]:
    """ASCII speech bubble around a quip."""
    text = text[:width]
    pad = width - len(text)
    lines = [
        f"╭{'─' * (width + 2)}╮",
        f"│ {text}{' ' * pad} │",
        f"╰{'─' * (width + 2)}╯",
        f"   ╲",
        f"    ╲",
    ]
    return lines


def render_vitals_bar(label: str, value: float, color: str, width: int = 10) -> str:
    filled = int((value / 100) * width)
    empty = width - filled
    bar = f"[{color}]{'█' * filled}[/][dim]{'░' * empty}[/]"
    return f"[dim]{label:<10}[/] {bar} [dim]{value:.0f}[/]"


def render_tomo_panel(state: TomoState, frame: int = 0, quip_override: Optional[str] = None) -> Panel:
    sprite_lines = render_sprite_frame(state, frame)
    quip = quip_override if quip_override is not None else get_quip(state)
    bubble = speech_bubble(quip, width=22)

    # Combine sprite + bubble side by side
    sprite_text = Text()
    for line in sprite_lines:
        sprite_text.append_text(Text.from_markup(line + "\n"))

    bubble_text = Text()
    for line in bubble:
        bubble_text.append_text(Text.from_markup(f"[cyan]{line}[/]\n"))

    # Stage label
    stage_colors = {
        Stage.EGG: "dim white",
        Stage.BABY: "green",
        Stage.CHILD: "cyan",
        Stage.TEEN: "blue",
        Stage.ADULT: "magenta",
    }
    color = stage_colors.get(state.identity_stage, "white")
    stage_label = f"[{color}]● {state.identity_stage.value.upper()}[/]"

    # Mood expression
    mood_expr = MOOD_EXPRESSIONS.get(state.current_mood, "")

    # Vitals
    vitals = state.vitals
    v_lines = "\n".join([
        render_vitals_bar("hunger",    vitals.hunger,    "yellow"),
        render_vitals_bar("happiness", vitals.happiness, "green"),
        render_vitals_bar("trust",     vitals.trust,     "magenta"),
        render_vitals_bar("energy",    vitals.energy,    "cyan"),
    ])

    # Relationship
    rel = state.relationship
    name_line = f"[dim]developer:[/] [bold]{rel.developer_name or '???'}[/]"
    streak_line = f"[dim]streak:[/]    [bold yellow]{rel.current_streak_days}d[/]  [dim]sessions:[/] [bold]{rel.sessions_together}[/]"

    # Watched repos
    watch_lines = ""
    if state.watchlist.active:
        repos = [f"[cyan]▸[/] {r.nickname or r.slug}" for r in state.watchlist.active[:5]]
        watch_lines = "\n".join(repos)
    else:
        watch_lines = "[dim]no repos watched yet[/]"

    content = (
        f"{stage_label}   {mood_expr}\n\n"
        f"{v_lines}\n\n"
        f"{name_line}\n"
        f"{streak_line}\n\n"
        f"[dim]watching:[/]\n{watch_lines}"
    )

    return Panel(
        content,
        title="[bold cyan]✦ TOMO ✦[/]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )


def animate(state: TomoState, seconds: int = 6) -> None:
    """Play a short idle animation."""
    frames = SPRITES.get(state.identity_stage, SPRITES[Stage.EGG])
    n = len(frames)
    ticks = seconds * 2  # 500ms per tick

    with Live(console=console, refresh_per_second=2) as live:
        for i in range(ticks):
            frame_lines = frames[i % n]
            quip = get_quip(state) if i % 4 == 0 else None

            sprite_text = Text()
            for line in frame_lines:
                sprite_text.append_text(Text.from_markup(line + "\n"))

            if quip:
                bubble_lines = speech_bubble(quip, width=24)
                for line in bubble_lines:
                    sprite_text.append_text(Text.from_markup(f"[cyan]{line}[/]\n"))

            panel = Panel(
                Align.center(sprite_text),
                title="[bold cyan]✦ TOMO ✦[/]",
                border_style="cyan",
                box=box.ROUNDED,
            )
            live.update(panel)
            time.sleep(0.5)


def show_status(state: TomoState) -> None:
    """Full status panel — sprite + stats side by side."""
    frames = SPRITES.get(state.identity_stage, SPRITES[Stage.EGG])
    frame_lines = frames[0]

    sprite_text = Text()
    for line in frame_lines:
        sprite_text.append_text(Text.from_markup(line + "\n"))

    sprite_panel = Panel(
        Align.center(sprite_text),
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    stats_panel = render_tomo_panel(state, frame=0)

    console.print(Columns([sprite_panel, stats_panel], equal=False))


def show_welcome(state: TomoState) -> None:
    """First run or hatching moment."""
    console.print()
    console.rule("[bold cyan]✦ TOMO ✦[/]")
    console.print()

    if state.identity_stage == Stage.EGG:
        console.print(
            Panel(
                "[cyan]something is stirring...[/]\n\n"
                "run [bold]tomo hello[/] to introduce yourself\n"
                "run [bold]tomo watch[/] to add a repo",
                title="[dim]a new egg[/]",
                border_style="dim",
                box=box.ROUNDED,
            )
        )
    else:
        animate(state, seconds=3)


def _pick_live_quip(state: TomoState) -> str:
    """Mood-driven idle quip, with repo concerns surfaced ~40% of the time."""
    concerns = []
    for repo in state.watchlist.active:
        name = repo.nickname or repo.slug
        if repo.test_discipline < 30:
            concerns.append(f"*worried glance — {name} tests?*")
        if repo.churn_tendency > 70:
            concerns.append(f"*{name} keeps changing...*")
        if repo.chaos_index > 75:
            concerns.append(f"*nervous chirp — {name}*")
    if concerns and random.random() < 0.4:
        return random.choice(concerns)
    return get_quip(state)


def _parse_live_input(data: str) -> list[str]:
    """Parse a stdin chunk into tokens: lowercase chars or 'click'."""
    tokens: list[str] = []
    i = 0
    while i < len(data):
        ch = data[i]
        if ch == "\x1b" and i + 2 < len(data) and data[i + 1] == "[" and data[i + 2] == "<":
            # SGR mouse sequence: \x1b[<button;col;rowM (press) or m (release)
            j = i + 3
            while j < len(data) and data[j] not in ("M", "m"):
                j += 1
            if j < len(data):
                parts = data[i + 3 : j].split(";")
                terminator = data[j]
                if terminator == "M" and len(parts) >= 3 and parts[0] == "0":
                    tokens.append("click")
                i = j + 1
                continue
            break  # incomplete sequence — wait for more
        if ch == "\x1b":
            # unknown escape — skip the byte to avoid choking on it
            i += 1
            continue
        tokens.append(ch.lower())
        i += 1
    return tokens


def run_live_session(
    state: TomoState,
    save_fn,
    on_feed,
    on_play,
    decay_seconds: int = 30,
    quip_seconds: int = 5,
    scan_minutes: int = 10,
) -> None:
    """Persistent TOMO presence — body-double mode.

    Sprite animates, vitals tick down, repo concerns surface, click or press f
    to feed, p to play, q to quit. Celebrates evolution when it happens.
    Auto-scans watched repos every `scan_minutes` (0 = disabled).
    """
    import sys
    import os
    import select
    import termios
    import tty
    import threading
    from rich.console import Group
    from tomo.mood import derive_mood, check_evolution
    from tomo.scan import scan_repo

    frames = SPRITES.get(state.identity_stage, SPRITES[Stage.EGG])

    FPS = 4
    FRAME_HOLD = 2
    QUIP_REFRESH_TICKS = max(1, FPS * quip_seconds)
    DECAY_TICKS = max(1, FPS * decay_seconds)
    EVOLUTION_CHECK_TICKS = FPS * 5
    CELEBRATION_TICKS = FPS * 4
    SCAN_TICKS = FPS * 60 * scan_minutes if scan_minutes > 0 else 0

    tick = 0
    flash_quip: Optional[str] = None
    flash_ttl = 0
    current_quip = _pick_live_quip(state)
    state.current_mood = derive_mood(state)

    celebrating = False
    celebration_ttl = 0
    celebrate_stage = ""
    celebrate_hint = ""

    scan_thread: Optional[threading.Thread] = None
    scan_results_lock = threading.Lock()
    scan_pending: list[dict] = []  # results queued for the main loop to apply

    def _kick_off_scan() -> bool:
        """Launch background scan if none is running. Returns True if launched."""
        nonlocal scan_thread
        if scan_thread is not None and scan_thread.is_alive():
            return False
        targets = [
            (r.repo_path, list(r.scan_paths), list(r.scan_ignore))
            for r in state.watchlist.active
        ]
        if not targets:
            return False

        def worker():
            results: dict = {}
            for path, paths, ignore in targets:
                result = scan_repo(path, paths, ignore)
                if result:
                    results[path] = result
            with scan_results_lock:
                scan_pending.append(results)

        scan_thread = threading.Thread(target=worker, daemon=True)
        scan_thread.start()
        return True

    def view():
        if celebrating:
            text = Text.from_markup(
                f"[bold magenta]✦ ✦ ✦[/]\n\n"
                f"[bold cyan]TOMO evolved into {celebrate_stage}![/]\n\n"
                f"[dim]{celebrate_hint}[/]\n"
            )
            main = Panel(
                Align.center(text),
                title="[bold magenta]✦ EVOLUTION ✦[/]",
                border_style="magenta",
                box=box.DOUBLE,
                padding=(2, 4),
            )
            footer = Panel(
                Align.center("[dim]any key to continue...[/]"),
                border_style="dim magenta",
                box=box.ROUNDED,
            )
            return Group(main, footer)

        frame_idx = (tick // FRAME_HOLD) % len(frames)
        sprite_text = Text()
        for line in frames[frame_idx]:
            sprite_text.append_text(Text.from_markup(line + "\n"))

        shown_quip = flash_quip or current_quip
        if shown_quip:
            for line in speech_bubble(shown_quip, width=26):
                sprite_text.append_text(Text.from_markup(f"[cyan]{line}[/]\n"))

        v = state.vitals
        strip = (
            f"\n[dim]hunger[/] [yellow]{int(v.hunger):>3}[/]  "
            f"[dim]happy[/] [green]{int(v.happiness):>3}[/]  "
            f"[dim]trust[/] [magenta]{int(v.trust):>3}[/]  "
            f"[dim]energy[/] [cyan]{int(v.energy):>3}[/]"
        )
        sprite_text.append_text(Text.from_markup(strip))

        main = Panel(
            Align.center(sprite_text),
            title=f"[bold cyan]✦ TOMO ✦[/]  [dim]{state.identity_stage.value} · {state.current_mood}[/]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        footer = Panel(
            Align.center(
                "[bold cyan]f[/]/click feed   [bold cyan]p[/] play   [bold cyan]q[/] quit"
            ),
            border_style="dim",
            box=box.ROUNDED,
        )
        return Group(main, footer)

    fd = sys.stdin.fileno()
    stdout_fd = sys.stdout.fileno()
    old_settings = termios.tcgetattr(fd)
    mouse_enabled = False
    # Note: we intentionally do NOT set O_NONBLOCK on stdin. On macOS,
    # stdin/stdout/stderr share an open file description when connected to
    # a TTY, so O_NONBLOCK on stdin would also make stdout non-blocking and
    # Rich's Live frame writes would fail with BlockingIOError. select+cbreak
    # is enough: select gates the read, cbreak makes os.read return as soon
    # as one byte is available.

    # Bypass Python-level buffering so cleanup escape codes always reach the
    # terminal — Rich's Live may otherwise swallow writes to sys.stdout.
    def _write_term(seq: bytes) -> None:
        try:
            os.write(stdout_fd, seq)
        except OSError:
            pass

    def _safe_view():
        try:
            return view()
        except Exception:
            # If markup ever breaks (e.g. a repo nickname with [brackets]),
            # fall back to a plain text panel so the loop doesn't crash.
            return Panel("[dim]TOMO is having a moment...[/]", border_style="red")

    try:
        tty.setcbreak(fd)
        # Enable SGR mouse reporting (button presses, decimal column/row).
        _write_term(b"\x1b[?1000h\x1b[?1006h")
        mouse_enabled = True

        if SCAN_TICKS:
            _kick_off_scan()

        with Live(_safe_view(), console=console, refresh_per_second=FPS, screen=True) as live:
            while True:
                read_ready, _, _ = select.select([sys.stdin], [], [], 1.0 / FPS)
                if read_ready:
                    try:
                        chunk = os.read(fd, 1024).decode("utf-8", errors="replace")
                    except (BlockingIOError, OSError):
                        chunk = ""
                    quit_requested = False
                    for token in _parse_live_input(chunk):
                        if token in ("q", "\x03"):
                            quit_requested = True
                            break
                        if celebrating:
                            # any key dismisses celebration
                            celebrating = False
                            celebration_ttl = 0
                            continue
                        if token in ("f", "click"):
                            on_feed(state)
                            state.current_mood = derive_mood(state)
                            save_fn(state)
                            flash_quip = "*nom nom* ✦"
                            flash_ttl = FPS * 2
                        elif token == "p":
                            on_play(state)
                            state.current_mood = derive_mood(state)
                            save_fn(state)
                            flash_quip = "*happy chirp!* ✦"
                            flash_ttl = FPS * 2
                    if quit_requested:
                        break

                tick += 1

                if celebrating:
                    celebration_ttl -= 1
                    if celebration_ttl <= 0:
                        celebrating = False
                else:
                    if flash_ttl > 0:
                        flash_ttl -= 1
                        if flash_ttl == 0:
                            flash_quip = None

                    if tick % QUIP_REFRESH_TICKS == 0:
                        current_quip = _pick_live_quip(state)

                    if tick % DECAY_TICKS == 0:
                        state.vitals.hunger = max(0, state.vitals.hunger - 1)
                        state.vitals.happiness = max(0, state.vitals.happiness - 0.5)
                        state.vitals.energy = max(0, state.vitals.energy - 0.5)
                        state.current_mood = derive_mood(state)
                        save_fn(state)

                    if tick % EVOLUTION_CHECK_TICKS == 0:
                        state, evolved = check_evolution(state)
                        if evolved:
                            from tomo.state import add_notable_moment
                            add_notable_moment(
                                state,
                                type="evolved",
                                memo=f"evolved into {state.identity_stage.value} during a live session",
                            )
                            save_fn(state)
                            frames = SPRITES.get(state.identity_stage, SPRITES[Stage.EGG])
                            celebrating = True
                            celebration_ttl = CELEBRATION_TICKS
                            celebrate_stage = state.identity_stage.value.upper()
                            celebrate_hint = state.evolution.next_evolution_hint

                    if SCAN_TICKS and tick % SCAN_TICKS == 0:
                        if _kick_off_scan():
                            flash_quip = "*sniffing your repos...*"
                            flash_ttl = FPS * 3

                    # Drain any completed scan results
                    with scan_results_lock:
                        drained = list(scan_pending)
                        scan_pending.clear()
                    if drained:
                        from datetime import datetime, timezone
                        for results in drained:
                            for repo in state.watchlist.active:
                                r = results.get(repo.repo_path)
                                if not r:
                                    continue
                                repo.test_discipline = r["test_discipline"]
                                repo.churn_tendency = r["churn_tendency"]
                                repo.commit_hygiene = r["commit_hygiene"]
                                repo.chaos_index = r["chaos_index"]
                                repo.last_scanned = datetime.now(timezone.utc)
                        save_fn(state)
                        # Refresh the quip rotation so any new concerns surface soon
                        current_quip = _pick_live_quip(state)

                live.update(_safe_view())
    except KeyboardInterrupt:
        pass
    except Exception:
        # Log the real failure so we can see it after cleanup. Without this
        # the bulletproof reset hides what actually went wrong.
        try:
            import traceback
            from pathlib import Path as _Path
            log_path = _Path.home() / ".tomo" / "live-error.log"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "a") as f:
                from datetime import datetime as _dt
                f.write(f"\n=== {_dt.now().isoformat()} ===\n")
                traceback.print_exc(file=f)
        except Exception:
            pass
        raise
    finally:
        # Bulletproof terminal reset. Each step is independently guarded so
        # one failure can't suppress the rest.
        if mouse_enabled:
            _write_term(b"\x1b[?1000l\x1b[?1006l")
        # Leave alt screen + show cursor in case Live's own cleanup didn't run
        _write_term(b"\x1b[?1049l\x1b[?25h")
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            pass
        try:
            save_fn(state)
        except Exception:
            pass
