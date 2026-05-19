"""
TOMO sprites — each evolution stage has 3 animation frames.
Designed with Unicode box-drawing + block characters for terminal pixel art.
Rich color tags are embedded for rendering.
"""

from enum import Enum


class Stage(str, Enum):
    EGG = "egg"
    BABY = "baby"
    CHILD = "child"
    TEEN = "teen"
    ADULT = "adult"


# Each sprite is a list of 3 frames (idle animation)
# Each frame is a list of lines
# Rich markup tags used for color

SPRITES = {
    Stage.EGG: [
        # Frame 1
        [
            "  [white]╭───╮[/]  ",
            " [white]╭╯[yellow]✦ ✦[/][white]╰╮[/] ",
            " [white]│[cyan] ··· [/][white]│[/] ",
            " [white]╰─────╯[/] ",
            " [dim]wobble..[/]  ",
        ],
        # Frame 2
        [
            "  [white]╭───╮[/]  ",
            " [white]╭╯[yellow]✦ ✦[/][white]╰╮[/] ",
            " [white]│[cyan] ─·─ [/][white]│[/] ",
            " [white]╰─────╯[/] ",
            " [dim]..wobble[/]  ",
        ],
        # Frame 3
        [
            "  [white]╭───╮[/]  ",
            " [white]╭╯[yellow]★ ★[/][white]╰╮[/] ",
            " [white]│[cyan] ··· [/][white]│[/] ",
            " [white]╰─────╯[/] ",
            " [dim]wobble..[/]  ",
        ],
    ],

    Stage.BABY: [
        # Frame 1 — big curious eyes, tiny body
        [
            " [cyan]∧[green]▄▄▄[/][cyan]∧[/]  ",
            "[cyan](◕ ᴗ ◕)[/] ",
            " [cyan]╰[green]─▾─[/][cyan]╯[/]  ",
            "  [green]╽ ╽[/]   ",
            "[yellow]hi........[/]",
        ],
        # Frame 2
        [
            " [cyan]∧[green]▄▄▄[/][cyan]∧[/]  ",
            "[cyan](◕ ‿ ◕)[/] ",
            " [cyan]╰[green]─▾─[/][cyan]╯[/]  ",
            "  [green]╽ ╽[/]   ",
            "[yellow]hi........[/]",
        ],
        # Frame 3
        [
            " [cyan]∧[green]▄▄▄[/][cyan]∧[/]  ",
            "[cyan](◕ ᴗ ◕)[/] ",
            " [cyan]╰[green]─▿─[/][cyan]╯[/]  ",
            "  [green]╽╽[/]    ",
            "[yellow]hi!.......[/]",
        ],
    ],

    Stage.CHILD: [
        # Frame 1 — a bit bigger, starting to look alien
        [
            " [cyan]╭[green]═══[/][cyan]╮[/]  ",
            "[cyan]╭╯[/][yellow]◉[/] [cyan]▾[/] [yellow]◉[/][cyan]╰╮[/]",
            "[cyan]│[green] ╭─╮ [/][cyan]│[/] ",
            "[cyan]╰[green]─┴─┴─[/][cyan]╯[/]",
            " [green]╿[/]   [green]╿[/]  ",
        ],
        # Frame 2
        [
            " [cyan]╭[green]═══[/][cyan]╮[/]  ",
            "[cyan]╭╯[/][yellow]◉[/] [cyan]─[/] [yellow]◉[/][cyan]╰╮[/]",
            "[cyan]│[green] ╭─╮ [/][cyan]│[/] ",
            "[cyan]╰[green]─┴─┴─[/][cyan]╯[/]",
            " [green]╿[/]   [green]╿[/]  ",
        ],
        # Frame 3
        [
            " [cyan]╭[green]═══[/][cyan]╮[/]  ",
            "[cyan]╭╯[/][yellow]◉[/] [cyan]▾[/] [yellow]◉[/][cyan]╰╮[/]",
            "[cyan]│[green] ╰─╯ [/][cyan]│[/] ",
            "[cyan]╰[green]─┴─┴─[/][cyan]╯[/]",
            " [green]╿ [/]  [green]╿[/]  ",
        ],
    ],

    Stage.TEEN: [
        # Frame 1 — taller, more defined, slight attitude
        [
            "  [cyan]╭[green]═╤═[/][cyan]╮[/] ",
            " [cyan]╭╯[/][yellow]⊙[/] [cyan]△[/] [yellow]⊙[/][cyan]╰╮[/]",
            " [cyan]│[green] ╭──╮ [/][cyan]│[/]",
            " [cyan]╰╮[green]╰──╯[/][cyan]╭╯[/]",
            "  [green]╿╿[/]  [green]╿╿[/] ",
        ],
        # Frame 2
        [
            "  [cyan]╭[green]═╤═[/][cyan]╮[/] ",
            " [cyan]╭╯[/][yellow]⊙[/] [cyan]─[/] [yellow]⊙[/][cyan]╰╮[/]",
            " [cyan]│[green] ╭──╮ [/][cyan]│[/]",
            " [cyan]╰╮[green]╰──╯[/][cyan]╭╯[/]",
            "  [green]╿╿[/]  [green]╿╿[/] ",
        ],
        # Frame 3
        [
            "  [cyan]╭[green]═╤═[/][cyan]╮[/] ",
            " [cyan]╭╯[/][yellow]⊙[/] [cyan]△[/] [yellow]⊙[/][cyan]╰╮[/]",
            " [cyan]│[green] ╰──╯ [/][cyan]│[/]",
            " [cyan]╰╮[green]╭──╮[/][cyan]╭╯[/]",
            "  [green]╿╿[/]  [green]╿╿[/] ",
        ],
    ],

    Stage.ADULT: [
        # Frame 1 — full haughty alien, tall antennae, regal
        [
            " [cyan]⌇[/] [cyan]╭[green]═╤═[/][cyan]╮[/] [cyan]⌇[/]",
            " [cyan]╭╯[/][yellow]★[/] [cyan]▽[/] [yellow]★[/][cyan]╰╮[/]",
            "[cyan]╭╯[green]╭──────╮[/][cyan]╰╮[/]",
            "[cyan]│[/] [cyan]╰╮[green]════[/][cyan]╭╯[/] [cyan]│[/]",
            "[cyan]╰╮[green]╿╿[/]  [green]╿╿[/][cyan]╭╯[/]",
        ],
        # Frame 2
        [
            " [cyan]⌇[/] [cyan]╭[green]═╤═[/][cyan]╮[/] [cyan]⌇[/]",
            " [cyan]╭╯[/][yellow]★[/] [cyan]─[/] [yellow]★[/][cyan]╰╮[/]",
            "[cyan]╭╯[green]╭──────╮[/][cyan]╰╮[/]",
            "[cyan]│[/] [cyan]╰╮[green]════[/][cyan]╭╯[/] [cyan]│[/]",
            "[cyan]╰╮[green]╿╿[/]  [green]╿╿[/][cyan]╭╯[/]",
        ],
        # Frame 3
        [
            " [cyan]⌇[/] [cyan]╭[green]═╤═[/][cyan]╮[/] [cyan]⌇[/]",
            " [cyan]╭╯[/][yellow]★[/] [cyan]▽[/] [yellow]★[/][cyan]╰╮[/]",
            "[cyan]╭╯[green]╭──────╮[/][cyan]╰╮[/]",
            "[cyan]│[/] [cyan]╰╮[green]────[/][cyan]╭╯[/] [cyan]│[/]",
            "[cyan]╰╮[green]╿╿[/]  [green]╿╿[/][cyan]╭╯[/]",
        ],
    ],
}


# Mood overlays — small expressions TOMO shows
MOOD_EXPRESSIONS = {
    "happy":     "[yellow]( ˶ᵔ ᵕ ᵔ˶ )[/]",
    "hungry":    "[red]( ._.) ₍ᐢ..ᐢ₎?[/]",
    "anxious":   "[orange1](  ╥ ω ╥  )[/]",
    "aloof":     "[blue]( ¬  ¬ )[/]",
    "impressed": "[green]( ！∀！)[/]",
    "dormant":   "[dim](  -  -  ) zzz[/]",
    "sass":      "[magenta]( ¬ᴗ¬ ) ...[/]",
}


# Speech bubbles TOMO says based on mood + stage
# These get picked randomly weighted by personality
QUIPS = {
    Stage.EGG: [
        "...",
        "*wobble*",
        "soon.",
    ],
    Stage.BABY: {
        "happy":   ["hiiii!", "✦ ✦", "stay?", "more?"],
        "hungry":  ["...feed?", "*sad noise*", "empty :("],
        "default": ["...", "hi!", "wat dat"],
    },
    Stage.CHILD: {
        "happy":   ["ur ok i guess", "tests passing 👍", "acceptable."],
        "hungry":  ["hello?? food??", "NEGLECT", "been 6 hours"],
        "anxious": ["churn detected 😰", "why rewrite again", "plz stop"],
        "default": ["watching...", "noted.", "hmm."],
    },
    Stage.TEEN: {
        "happy":   ["...fine. good job.", "coverage up. whatever.", "not bad."],
        "hungry":  ["it's been DAYS", "i noticed u left", "classic."],
        "anxious": ["3 TODOs added", "that PR is stale", "secrets?? really??"],
        "aloof":   ["...", "busy.", "not now."],
        "default": ["observing.", "still here.", "..."],
    },
    Stage.ADULT: {
        "happy":   [
            "...acceptable.",
            "i suppose that refactor was not terrible.",
            "your coverage is adequate. for a human.",
        ],
        "hungry":  [
            "you dare abandon me.",
            "i have been watching this empty repo for 3 days.",
            "characteristic.",
        ],
        "anxious": [
            "i detected a secret in your last commit. embarrassing.",
            "churn rate: appalling.",
            "have you considered... testing?",
        ],
        "aloof":   [
            "i am aware of your presence.",
            "...",
            "you may proceed.",
        ],
        "impressed": [
            "...i will allow it.",
            "that was almost elegant.",
            "don't let it go to your head.",
        ],
        "default": [
            "observing.",
            "your code is... fine.",
            "i've seen worse. not many worse, but some.",
        ],
    },
}
