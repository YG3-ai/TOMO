"""
Repo health scanner — computes the four RepoFingerprint metrics from real
git history and filesystem contents.

Metrics (all 0-100):
- test_discipline   — share of source files that look like tests
- churn_tendency    — how often the same files get rewritten
- commit_hygiene    — quality of recent commit messages
- chaos_index       — inverse composite of the other three
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Optional


SOURCE_EXTS = {
    ".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".rb", ".go", ".rs", ".java", ".kt", ".swift",
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cs", ".scala", ".clj",
    ".ex", ".exs", ".php",
}

SKIP_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", ".env",
    "__pycache__", "dist", "build", "target", "out",
    ".next", ".nuxt", "vendor", ".tox", ".pytest_cache",
    ".mypy_cache", "coverage", ".coverage", ".cache",
    ".gradle", "Pods", "DerivedData",
}

TEST_DIR_NAMES = {"test", "tests", "__tests__", "spec", "specs"}

TEST_FILE_PATTERNS = [
    re.compile(r"^test_.+\.py$", re.IGNORECASE),
    re.compile(r".+_test\.py$", re.IGNORECASE),
    re.compile(r".+_test\.go$", re.IGNORECASE),
    re.compile(r".+\.test\.(ts|tsx|js|jsx|mjs)$", re.IGNORECASE),
    re.compile(r".+\.spec\.(ts|tsx|js|jsx|mjs)$", re.IGNORECASE),
    re.compile(r".+Test\.(java|kt|scala)$"),
    re.compile(r".+Spec\.(rb|scala|clj)$"),
]

LOW_EFFORT_MSG = re.compile(
    r"^(wip|fix|asdf|tmp|temp|test|update|updated|fixed|stuff|changes|misc|.|\?)\.?$",
    re.IGNORECASE,
)


def _is_test_file(path: Path, repo_root: Path) -> bool:
    name = path.name
    rel_parts = {p.lower() for p in path.relative_to(repo_root).parts[:-1]}
    if rel_parts & TEST_DIR_NAMES:
        return True
    return any(pat.match(name) for pat in TEST_FILE_PATTERNS)


def _resolve_scope_roots(repo_root: Path, scan_paths: list[str]) -> list[Path]:
    """Resolve user-supplied scope paths to absolute directories under repo_root."""
    if not scan_paths:
        return [repo_root]
    roots: list[Path] = []
    for sp in scan_paths:
        candidate = (repo_root / sp).resolve()
        # Reject paths that escape the repo.
        try:
            candidate.relative_to(repo_root)
        except ValueError:
            continue
        if candidate.exists() and candidate.is_dir():
            roots.append(candidate)
    return roots or [repo_root]


def _is_under_ignored(path: Path, repo_root: Path, ignore_dirs: set[str]) -> bool:
    if not ignore_dirs:
        return False
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        return False
    parts = rel.parts
    for ignore in ignore_dirs:
        ignore_parts = tuple(p for p in Path(ignore).parts if p not in (".", ""))
        if not ignore_parts:
            continue
        # Match anywhere in the path (e.g. "docs" matches "src/docs/foo")
        # or as a prefix (e.g. "docs/legacy" matches only that nested path).
        if len(ignore_parts) == 1:
            if ignore_parts[0] in parts:
                return True
        else:
            for i in range(len(parts) - len(ignore_parts) + 1):
                if parts[i : i + len(ignore_parts)] == ignore_parts:
                    return True
    return False


def _count_files(
    repo_root: Path,
    scan_paths: Optional[list[str]] = None,
    scan_ignore: Optional[list[str]] = None,
) -> tuple[int, int]:
    """Walk the repo, return (n_source, n_test)."""
    n_source = 0
    n_test = 0
    ignore_set = set(scan_ignore or [])
    for root in _resolve_scope_roots(repo_root, scan_paths or []):
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if _is_under_ignored(path, repo_root, ignore_set):
                continue
            if path.suffix.lower() not in SOURCE_EXTS:
                continue
            n_source += 1
            if _is_test_file(path, repo_root):
                n_test += 1
    return n_source, n_test


def _git(repo_root: Path, args: list[str]) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def _git_file_changes(
    repo_root: Path,
    max_commits: int = 200,
    scan_paths: Optional[list[str]] = None,
    scan_ignore: Optional[list[str]] = None,
) -> list[str]:
    args = ["log", f"-n{max_commits}", "--pretty=format:", "--name-only"]
    if scan_paths:
        args.append("--")
        args.extend(scan_paths)
    out = _git(repo_root, args)
    if out is None:
        return []
    changes = [line.strip() for line in out.splitlines() if line.strip()]
    if scan_ignore:
        ignore_set = set(scan_ignore)
        changes = [
            c for c in changes
            if not _is_under_ignored(repo_root / c, repo_root, ignore_set)
        ]
    return changes


def _git_messages(repo_root: Path, max_commits: int = 100) -> list[str]:
    out = _git(repo_root, ["log", f"-n{max_commits}", "--pretty=format:%s"])
    if out is None:
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def _compute_test_discipline(n_source: int, n_test: int) -> float:
    if n_source == 0:
        return 50.0  # unknown — leave neutral
    ratio = n_test / n_source
    # 30% test files is "ideal" → 100. Linear scale.
    return min(100.0, ratio * 333.0)


def _compute_churn(file_changes: list[str]) -> float:
    if not file_changes:
        return 50.0
    unique = len(set(file_changes))
    avg_changes = len(file_changes) / max(unique, 1)
    # 1.0 = no churn → 0. 3.0+ = severe churn → 100.
    return max(0.0, min(100.0, (avg_changes - 1.0) * 50.0))


def _compute_hygiene(messages: list[str]) -> float:
    if not messages:
        return 50.0
    short = sum(1 for m in messages if len(m) < 10)
    low_effort = sum(1 for m in messages if LOW_EFFORT_MSG.match(m))
    pct_short = short / len(messages)
    pct_low = low_effort / len(messages)
    score = 100.0 - (pct_short * 100.0 + pct_low * 150.0)
    return max(0.0, min(100.0, score))


def _compute_chaos(td: float, ct: float, ch: float) -> float:
    return (100.0 - td + ct + 100.0 - ch) / 3.0


def scan_repo(
    repo_path: str,
    scan_paths: Optional[list[str]] = None,
    scan_ignore: Optional[list[str]] = None,
) -> Optional[dict]:
    """Scan a repo and return updated metrics, or None if the path is unusable."""
    root = Path(repo_path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        return None

    n_source, n_test = _count_files(root, scan_paths, scan_ignore)
    file_changes = _git_file_changes(root, scan_paths=scan_paths, scan_ignore=scan_ignore)
    messages = _git_messages(root)

    td = _compute_test_discipline(n_source, n_test)
    ct = _compute_churn(file_changes)
    ch = _compute_hygiene(messages)
    ci = _compute_chaos(td, ct, ch)

    return {
        "test_discipline": td,
        "churn_tendency": ct,
        "commit_hygiene": ch,
        "chaos_index": ci,
        "_n_source": n_source,
        "_n_test": n_test,
        "_n_commits_scanned": len(messages),
        "_is_git_repo": bool(messages or file_changes),
    }
