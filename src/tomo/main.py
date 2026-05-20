"""
TOMO CLI — tomo [command]
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box

from tomo.state import load_state, save_state, RepoFingerprint, add_notable_moment
from tomo.display import show_status, show_welcome, animate, console, run_live_session
from tomo.mood import update_vitals_for_session, check_evolution
from tomo.talk import run_talk_preview, format_slash_command_output
from typing import Optional

app = typer.Typer(
    name="tomo",
    help="✦ TOMO — the electric pet that lives in your repos ✦",
    add_completion=False,
    rich_markup_mode="rich",
    invoke_without_command=True,
)


@app.callback(invoke_without_command=True)
def _default(ctx: typer.Context):
    """✦ TOMO — the electric pet that lives in your repos ✦"""
    if ctx.invoked_subcommand is None:
        state = load_state()
        state = _session_start(state)
        animate(state, seconds=6)


def _session_start(state, quiet: bool = False):
    """Run on every tomo command — tick vitals, check evolution."""
    state = update_vitals_for_session(state)
    state, evolved = check_evolution(state)
    if evolved:
        add_notable_moment(
            state,
            type="evolved",
            memo=f"evolved into {state.identity_stage.value}",
        )
        if not quiet:
            console.print(
                Panel(
                    f"[bold cyan]✦ TOMO evolved into {state.identity_stage.value.upper()}! ✦[/]\n\n"
                    f"[dim]{state.evolution.next_evolution_hint}[/]",
                    border_style="cyan",
                    box=box.ROUNDED,
                )
            )
    save_state(state)
    return state


@app.command()
def hello():
    """Introduce yourself to TOMO."""
    state = load_state()
    state = _session_start(state)

    if not state.relationship.developer_name:
        name = Prompt.ask("[cyan]what's your name?[/]")
        state.relationship.developer_name = name.strip()
        save_state(state)
        console.print(f"\n[cyan]TOMO tilts its head.[/] [dim]...{name}. noted.[/]\n")

    show_welcome(state)


@app.command()
def status():
    """See TOMO and your repo health at a glance."""
    state = load_state()
    state = _session_start(state)
    show_status(state)


def _split_csv(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [p.strip() for p in value.split(",") if p.strip()]


@app.command()
def watch(
    path: str = typer.Argument(
        ".",
        help="Path to the repo to watch (defaults to current directory)"
    ),
    nickname: str = typer.Option(None, "--name", "-n", help="Nickname for this repo"),
    only: Optional[str] = typer.Option(
        None, "--only",
        help="Comma-separated dirs to scan exclusively (e.g. 'src,tests'). Empty = whole repo.",
    ),
    ignore: Optional[str] = typer.Option(
        None, "--ignore",
        help="Comma-separated dirs to skip during scan (e.g. 'docs,examples,vendor').",
    ),
):
    """Add a repo to TOMO's watchlist."""
    state = load_state()
    state = _session_start(state)

    repo_path = str(Path(path).resolve())

    existing = [r for r in state.watchlist.active if r.repo_path == repo_path]
    if existing:
        console.print(f"[dim]TOMO already watches this one.[/] [dim](use [bold]tomo scope[/][dim] to update its scope.)[/]")
        return

    if len(state.watchlist.active) >= state.watchlist.max_active:
        console.print(
            Panel(
                f"[yellow]TOMO is already watching {state.watchlist.max_active} repos.[/]\n"
                "[dim]pause one first with [bold]tomo pause <path>[/][dim] or TOMO will be spread too thin.[/]",
                border_style="yellow",
                box=box.ROUNDED,
            )
        )
        return

    nick = nickname or Path(repo_path).name
    repo = RepoFingerprint(
        repo_path=repo_path,
        nickname=nick,
        scan_paths=_split_csv(only),
        scan_ignore=_split_csv(ignore),
    )
    state.watchlist.active.append(repo)
    save_state(state)

    console.print(f"\n[cyan]TOMO glances at[/] [bold]{nick}[/][cyan].[/]")
    if repo.scan_paths:
        console.print(f"[dim]scope: only {', '.join(repo.scan_paths)}[/]")
    if repo.scan_ignore:
        console.print(f"[dim]ignoring: {', '.join(repo.scan_ignore)}[/]")
    console.print(f"[dim]...observing.[/]\n")


@app.command()
def ignore(
    path: str = typer.Argument(".", help="Repo to stop watching"),
):
    """Remove a repo from TOMO's watchlist entirely."""
    state = load_state()
    repo_path = str(Path(path).resolve())

    before = len(state.watchlist.active)
    state.watchlist.active = [r for r in state.watchlist.active if r.repo_path != repo_path]

    if len(state.watchlist.active) < before:
        save_state(state)
        console.print(f"[dim]TOMO lets go of that one.[/]")
    else:
        console.print(f"[dim]that repo wasn't being watched.[/]")


@app.command()
def pause(
    path: str = typer.Argument(".", help="Repo to pause"),
):
    """Pause a repo — TOMO remembers it but stops worrying about it."""
    state = load_state()
    repo_path = str(Path(path).resolve())

    active = [r for r in state.watchlist.active if r.repo_path == repo_path]
    if not active:
        console.print("[dim]that repo isn't in the active watchlist.[/]")
        return

    state.watchlist.active = [r for r in state.watchlist.active if r.repo_path != repo_path]
    state.watchlist.paused.extend(active)
    save_state(state)

    console.print(f"[dim]TOMO sets that repo aside. it'll be there when you're back.[/]")


@app.command(name="list")
def list_repos():
    """Show all watched repos and their health."""
    state = load_state()

    from rich.table import Table
    table = Table(
        title="[bold cyan]✦ TOMO's watchlist ✦[/]",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=True,
    )
    table.add_column("repo", style="bold")
    table.add_column("sessions", justify="right")
    table.add_column("test discipline", justify="right")
    table.add_column("churn", justify="right")
    table.add_column("chaos", justify="right")
    table.add_column("status")

    for r in state.watchlist.active:
        table.add_row(
            r.nickname or r.slug,
            str(r.session_count),
            f"{r.test_discipline:.0f}",
            f"{r.churn_tendency:.0f}",
            f"{r.chaos_index:.0f}",
            "[green]active[/]",
        )

    for r in state.watchlist.paused:
        table.add_row(
            r.nickname or r.slug,
            str(r.session_count),
            f"{r.test_discipline:.0f}",
            f"{r.churn_tendency:.0f}",
            f"{r.chaos_index:.0f}",
            "[dim]paused[/]",
        )

    if not state.watchlist.active and not state.watchlist.paused:
        console.print("[dim]TOMO isn't watching anything yet. try [bold]tomo watch[/][dim].[/]")
        return

    console.print(table)


@app.command()
def feed():
    """Feed TOMO."""
    state = load_state()
    state = _session_start(state)

    state.vitals.hunger = min(100, state.vitals.hunger + 40)
    state.vitals.happiness = min(100, state.vitals.happiness + 5)
    save_state(state)

    responses = {
        "egg":   "the egg wobbles appreciatively.",
        "baby":  "TOMO makes a small happy noise. 🌟",
        "child": "TOMO eats quickly and pretends not to be grateful.",
        "teen":  "TOMO eats without making eye contact. '...thanks.'",
        "adult": "TOMO accepts the offering. '...adequate.'",
    }
    console.print(f"\n[cyan]{responses[state.identity_stage.value]}[/]\n")
    animate(state, seconds=2)


@app.command()
def play():
    """Play with TOMO. Boosts happiness and trust."""
    state = load_state()
    state = _session_start(state)

    stage = state.identity_stage.value

    games = {
        "egg":   "the egg does not play. it is an egg.",
        "baby":  "you play peek-a-boo. TOMO is delighted. ✦",
        "child": "you play a refactoring puzzle. TOMO wins. obviously.",
        "teen":  "you challenge TOMO to spot the bug. TOMO finds 3. '...not hard.'",
        "adult": "TOMO reviews your architecture. 'i will allow 2 of these 7 decisions.'",
    }

    state.vitals.happiness = min(100, state.vitals.happiness + 15)
    state.vitals.trust = min(100, state.vitals.trust + 3)
    save_state(state)

    console.print(f"\n[cyan]{games[stage]}[/]\n")
    animate(state, seconds=3)


@app.command()
def talk(
    message: Optional[str] = typer.Argument(
        None,
        help="Optional message to pass to TOMO (used with --raw for piping to an AI).",
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        help="Output raw vocalization + translator prompt for piping to any AI.",
    ),
):
    """Talk to TOMO. A conversation grounded in your real history and repos."""
    state = load_state()
    state = _session_start(state, quiet=raw)
    if raw:
        typer.echo(format_slash_command_output(state, message))
    else:
        run_talk_preview(state)


@app.command()
def animate_cmd(
    seconds: int = typer.Option(6, "--seconds", "-s"),
):
    """Watch TOMO idle for a bit."""
    state = load_state()
    state = _session_start(state)
    animate(state, seconds=seconds)


def _color_score(value: float, invert: bool = False) -> str:
    """Color a 0-100 score. invert=True when high values are bad (churn, chaos)."""
    if invert:
        if value >= 70: return f"[red]{value:.0f}[/]"
        if value >= 40: return f"[yellow]{value:.0f}[/]"
        return f"[green]{value:.0f}[/]"
    if value >= 70: return f"[green]{value:.0f}[/]"
    if value >= 40: return f"[yellow]{value:.0f}[/]"
    return f"[red]{value:.0f}[/]"


@app.command()
def scan(
    target: Optional[str] = typer.Argument(
        None,
        help="Path or nickname of a watched repo. Omit to scan all.",
    ),
):
    """Scan watched repo(s) — compute health metrics from git + filesystem."""
    from rich.table import Table
    from tomo.scan import scan_repo

    state = load_state()
    state = _session_start(state)

    if not state.watchlist.active:
        console.print("[dim]TOMO isn't watching anything yet. Try [bold]tomo watch[/][dim].[/]")
        return

    if target:
        try:
            resolved = str(Path(target).expanduser().resolve())
        except OSError:
            resolved = target
        repos = [
            r for r in state.watchlist.active
            if r.repo_path == resolved or r.nickname == target or r.slug == target
        ]
        if not repos:
            console.print(f"[dim]nothing in the watchlist matches [bold]{target}[/][dim].[/]")
            return
    else:
        repos = state.watchlist.active

    table = Table(
        title="[bold cyan]✦ scan results ✦[/]",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("repo", style="bold")
    table.add_column("tests", justify="right")
    table.add_column("churn", justify="right")
    table.add_column("hygiene", justify="right")
    table.add_column("chaos", justify="right")
    table.add_column("notes", style="dim")

    for repo in repos:
        result = scan_repo(repo.repo_path, repo.scan_paths, repo.scan_ignore)
        name = repo.nickname or repo.slug
        if result is None:
            table.add_row(name, "—", "—", "—", "—", "path missing")
            continue

        repo.test_discipline = result["test_discipline"]
        repo.churn_tendency = result["churn_tendency"]
        repo.commit_hygiene = result["commit_hygiene"]
        repo.chaos_index = result["chaos_index"]

        notes = []
        if not result["_is_git_repo"]:
            notes.append("not a git repo")
        else:
            notes.append(f"{result['_n_commits_scanned']} commits")
        notes.append(f"{result['_n_test']}/{result['_n_source']} test files")

        table.add_row(
            name,
            _color_score(result["test_discipline"]),
            _color_score(result["churn_tendency"], invert=True),
            _color_score(result["commit_hygiene"]),
            _color_score(result["chaos_index"], invert=True),
            ", ".join(notes),
        )

    save_state(state)
    console.print(table)

    worst = max(state.watchlist.active, key=lambda r: r.chaos_index, default=None)
    if worst and worst.chaos_index > 70:
        console.print(
            f"\n[cyan]TOMO frowns at [bold]{worst.nickname or worst.slug}[/][cyan]. "
            f"[dim]something is off.[/][/]"
        )
    elif state.watchlist.active and all(r.test_discipline > 60 for r in state.watchlist.active):
        console.print("\n[cyan]TOMO seems pleased with your test discipline. ✦[/]")


def _find_repo(state, target: str):
    """Resolve a target string to a watched repo (by path, nickname, or slug)."""
    try:
        resolved = str(Path(target).expanduser().resolve())
    except OSError:
        resolved = target
    for r in state.watchlist.active:
        if r.repo_path == resolved or r.nickname == target or r.slug == target:
            return r
    return None


@app.command()
def scope(
    target: Optional[str] = typer.Argument(None, help="Path, nickname, or slug of a watched repo. Omit to list all."),
    only: Optional[str] = typer.Option(None, "--only", help="Replace scan_paths (comma-separated)."),
    ignore: Optional[str] = typer.Option(None, "--ignore", help="Replace scan_ignore (comma-separated)."),
    clear: bool = typer.Option(False, "--clear", help="Reset scope to whole repo."),
):
    """View or update the scan scope for watched repos."""
    state = load_state()

    if target is None:
        if not state.watchlist.active:
            console.print("[dim]TOMO isn't watching anything yet.[/]")
            return
        for r in state.watchlist.active:
            name = r.nickname or r.slug
            only_s = ", ".join(r.scan_paths) if r.scan_paths else "[dim]whole repo[/]"
            ignore_s = ", ".join(r.scan_ignore) if r.scan_ignore else "[dim]none[/]"
            console.print(f"[bold cyan]{name}[/]  [dim]{r.repo_path}[/]")
            console.print(f"  [dim]only:[/]   {only_s}")
            console.print(f"  [dim]ignore:[/] {ignore_s}\n")
        return

    repo = _find_repo(state, target)
    if repo is None:
        console.print(f"[dim]nothing in the watchlist matches [bold]{target}[/][dim].[/]")
        return

    # No flags = display only
    if only is None and ignore is None and not clear:
        name = repo.nickname or repo.slug
        only_s = ", ".join(repo.scan_paths) if repo.scan_paths else "[dim]whole repo[/]"
        ignore_s = ", ".join(repo.scan_ignore) if repo.scan_ignore else "[dim]none[/]"
        console.print(f"[bold cyan]{name}[/]  [dim]{repo.repo_path}[/]")
        console.print(f"  [dim]only:[/]   {only_s}")
        console.print(f"  [dim]ignore:[/] {ignore_s}")
        return

    if clear:
        repo.scan_paths = []
        repo.scan_ignore = []
    if only is not None:
        repo.scan_paths = _split_csv(only)
    if ignore is not None:
        repo.scan_ignore = _split_csv(ignore)

    save_state(state)
    name = repo.nickname or repo.slug
    console.print(f"[cyan]scope updated for [bold]{name}[/][cyan].[/]")
    if repo.scan_paths:
        console.print(f"  [dim]only:[/]   {', '.join(repo.scan_paths)}")
    if repo.scan_ignore:
        console.print(f"  [dim]ignore:[/] {', '.join(repo.scan_ignore)}")
    if not repo.scan_paths and not repo.scan_ignore:
        console.print("  [dim](whole repo, no ignores)[/]")


@app.command()
def quill(
    aspect: Optional[str] = typer.Argument(
        None,
        help="What to focus on (e.g. 'testing', 'churn'). Omit for a holistic review.",
    ),
    show_meta: bool = typer.Option(False, "--meta", help="Also show plan, slices, and cross-review metadata."),
):
    """Summon Quill — a dual-agent review grounded in TOMO's repo state."""
    from tomo.quill import build_framing, run_quill_consultation

    state = load_state()
    state = _session_start(state)

    framing = build_framing(state, aspect=aspect)

    console.print(
        Panel(
            "[cyan]TOMO is summoning Quill...[/]\n"
            "[dim]two voices are reviewing — this can take 1–3 minutes.[/]",
            border_style="magenta",
            box=box.ROUNDED,
        )
    )

    try:
        result = run_quill_consultation(framing)
    except RuntimeError as e:
        console.print(f"\n[red]{e}[/]\n")
        raise typer.Exit(code=1)

    if "error" in result:
        console.print(f"\n[red]Quill returned an error:[/] [dim]{result['error']}[/]\n")
        raise typer.Exit(code=1)

    response = result.get("assembled_response") or "[dim](no assembled response returned)[/]"
    console.print(
        Panel(
            response,
            title="[bold magenta]✦ Quill ✦[/]  [dim]two voices[/]",
            border_style="magenta",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    if show_meta:
        from rich.table import Table
        table = Table(title="[dim]mosaic slices[/]", box=box.ROUNDED, border_style="dim magenta")
        table.add_column("slice", style="bold")
        table.add_column("voice", style="cyan")
        table.add_column("content", overflow="fold")
        for s in result.get("slices", []):
            table.add_row(s.get("slice", "?"), s.get("voice", "?"), s.get("content", "")[:400])
        console.print(table)
        flags = result.get("cross_review_flags", [])
        if flags:
            console.print(f"\n[dim]cross-review flags:[/] {len(flags)}")

    aspect_label = aspect or "holistic"
    memo = (response[:160] + "...") if len(response) > 160 else response
    add_notable_moment(
        state,
        type=f"quill_consultation:{aspect_label}",
        memo=memo,
    )
    save_state(state)


@app.command()
def history(
    limit: int = typer.Option(20, "--limit", "-n", help="How many recent moments to show."),
):
    """Timeline of notable moments — evolutions, consultations, milestones."""
    state = load_state()
    moments = list(state.relationship.notable_moments)
    if not moments:
        console.print(
            "[dim]TOMO doesn't remember anything notable yet. "
            "Things will accrue here as you keep showing up.[/]"
        )
        return

    moments.sort(key=lambda m: m.timestamp, reverse=True)
    moments = moments[:limit]

    from rich.table import Table
    table = Table(
        title=f"[bold cyan]✦ TOMO's history ✦[/]  [dim]({len(state.relationship.notable_moments)} moments total)[/]",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("when", style="dim")
    table.add_column("type", style="magenta")
    table.add_column("repo", style="cyan")
    table.add_column("memo", overflow="fold")
    for m in moments:
        when = m.timestamp.strftime("%Y-%m-%d %H:%M")
        table.add_row(when, m.type, m.repo or "", m.memo)
    console.print(table)


def _live_feed(state):
    state.vitals.hunger = min(100, state.vitals.hunger + 40)
    state.vitals.happiness = min(100, state.vitals.happiness + 5)


def _live_play(state):
    state.vitals.happiness = min(100, state.vitals.happiness + 15)
    state.vitals.trust = min(100, state.vitals.trust + 3)


@app.command()
def live(
    decay_seconds: int = typer.Option(30, "--decay-seconds", help="How often vitals tick down."),
    quip_seconds: int = typer.Option(5, "--quip-seconds", help="How often the idle quip rotates."),
    scan_minutes: int = typer.Option(10, "--scan-minutes", help="Auto-scan watched repos every N minutes (0 disables)."),
):
    """Persistent TOMO window. Press f to feed, p to play, click to feed, q to quit."""
    state = load_state()
    state = _session_start(state)
    run_live_session(
        state,
        save_fn=save_state,
        on_feed=_live_feed,
        on_play=_live_play,
        decay_seconds=decay_seconds,
        quip_seconds=quip_seconds,
        scan_minutes=scan_minutes,
    )


# alias
app.command(name="hi")(hello)


if __name__ == "__main__":
    app()