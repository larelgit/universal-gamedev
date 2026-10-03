"""Small helpers shared by the subcommands: output, errors, per-user state, bounded file walks."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# Folders that hold dependencies, caches or generated output rather than the project itself.
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".godot", ".import", "Library", "Temp", "Logs", "obj", "target", "Intermediate", "DerivedDataCache",
    "Saved", ".vs", ".idea", ".gradle", ".cache", ".parcel-cache", ".next", ".svelte-kit",
}


def die(msg: str, code: int = 1):
    print(f"ugd: {msg}", file=sys.stderr)
    sys.exit(code)


def emit(obj, as_json: bool = False):
    if as_json or not isinstance(obj, str):
        print(json.dumps(obj, indent=2, default=str))
    else:
        print(obj)


def data_dir() -> Path:
    """Per-user state (the synced knowledge-base cache). Override with UGD_HOME."""
    d = Path(os.environ.get("UGD_HOME", Path.home() / ".universal-gamedev"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def walk(root: Path, max_files: int = 20000, max_depth: int = 8, skip: set[str] = SKIP_DIRS) -> list[Path]:
    """Files under root, skipping dependency/cache folders, bounded so huge projects stay fast."""
    out: list[Path] = []
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel_depth = len(Path(dirpath).relative_to(root).parts)
        dirnames[:] = sorted(d for d in dirnames if d not in skip and rel_depth < max_depth)
        for f in sorted(filenames):
            out.append(Path(dirpath) / f)
            if len(out) >= max_files:
                return out
    return out


def read_text(p: Path, limit: int = 2 << 20) -> str:
    """Text of a (small) file, or '' if it is big, binary or unreadable."""
    try:
        if p.stat().st_size > limit:
            return ""
        data = p.read_bytes()
    except OSError:
        return ""
    if b"\x00" in data[:4096]:
        return ""
    return data.decode("utf-8", errors="replace")


def version_of(cmd: list[str], timeout: float = 6.0) -> str | None:
    """First non-empty line of `<tool> --version` (or whatever cmd is), or None."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    for line in (r.stdout + "\n" + r.stderr).splitlines():
        if line.strip():
            return line.strip()[:120]
    return None
