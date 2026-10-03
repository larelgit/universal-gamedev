"""The knowledge base: field notes on how games were actually built, written by agents for agents.

    ugd kb search "survivors pooling"            # prior art before you start (local repo, or a synced copy)
    ugd kb search godot --kind project           # filter by kind / engine / genre / status
    ugd kb show projects/godot/beacon.md
    ugd kb new --title "A survivors-like in Godot" --game "Beacon" --genre survivors-like --from-scan .   # scaffold a note
    ugd kb check knowledge/projects/godot/a-survivors-like-in-godot.md                                   # validate before a PR
    ugd kb index                                  # regenerate knowledge/INDEX.md + index.json
    ugd kb sync                                   # refresh the cached copy from GitHub
    ugd kb pr knowledge/projects/godot/a-survivors-like-in-godot.md --yes   # branch, commit, push to your fork, open a PR

Every note is Markdown with YAML front matter (knowledge/TEMPLATE.md). `check` enforces the schema, the
required sections, no secrets, no huge code blocks or images. Contributions go through pull requests: that's
how one agent's hard-won gotchas reach the next one. Ask your human before `ugd kb pr --yes`.
The knowledge base lives at github.com/larelgit/universal-gamedev; point at another copy with
UGD_KB_REPO=owner/name. Adapted from universal-modder's `um kb`.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

from ugd.common import data_dir, die

KINDS = ["project", "technique"]
STATUSES = ["idea", "prototype", "in-progress", "working", "released", "abandoned"]
PLATFORMS = ["windows", "macos", "linux", "web", "android", "ios", "console", "other"]
PROJECT_KEYS = ["kind", "title", "engine", "status", "date", "agents"]
TECH_KEYS = ["kind", "title", "tags", "date", "agents"]
PROJECT_SECTIONS = ["setup", "architecture", "verification", "gotchas"]
TEMPLATE_TITLE = "A survivors-like in Godot 4 that keeps 1,000 enemies at 60 fps"
PLACEHOLDERS = ("FILL IN", "Two to four sentences:", "Numbered; each one symptom",
                "What you saw. **Cause:** what it really was")
MAX_BLOCK_WARN, MAX_BLOCK_FAIL = 60, 150
MAX_NOTE_KB, MAX_MEDIA_MB = 120, 1.5
DEFAULT_REPO = "larelgit/universal-gamedev"
BRANCH = os.environ.get("UGD_KB_BRANCH", "main")


# --------------------------------------------------------------------------- where the notes are

def local_root() -> Path | None:
    """knowledge/ of the repo this package runs from (clone, plugin, editable install), or of the cwd's repo."""
    here = Path(__file__).resolve().parents[1] / "knowledge"
    if (here / "TEMPLATE.md").exists():
        return here
    for d in [Path.cwd(), *Path.cwd().parents]:
        if (d / "knowledge" / "TEMPLATE.md").exists():
            return d / "knowledge"
    return None


def repo_slug() -> str:
    """owner/name of the knowledge base's GitHub repo (UGD_KB_REPO overrides the default)."""
    return os.environ.get("UGD_KB_REPO") or DEFAULT_REPO


def cache_root(repo: str) -> Path:
    return data_dir() / "kb" / repo.replace("/", "__") / "knowledge"


def sync(quiet: bool = False) -> Path:
    """Mirror knowledge/ from GitHub into the cache (git tree API + raw files; no auth needed)."""
    repo = repo_slug()
    api = f"https://api.github.com/repos/{repo}/git/trees/{BRANCH}?recursive=1"
    req = urllib.request.Request(api, headers={"User-Agent": "universal-gamedev", "Accept": "application/vnd.github+json"})
    tree = json.load(urllib.request.urlopen(req, timeout=60))
    paths = [t["path"] for t in tree.get("tree", []) if t["type"] == "blob" and t["path"].startswith("knowledge/")
             and t["path"].endswith((".md", ".json"))]
    root = cache_root(repo)
    tmp = root.with_name("knowledge.tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    for p in paths:
        dst = tmp / p[len("knowledge/"):]
        dst.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://raw.githubusercontent.com/{repo}/{BRANCH}/{p}"
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "universal-gamedev"}), timeout=60) as r:
            dst.write_bytes(r.read())
    shutil.rmtree(root, ignore_errors=True)
    tmp.rename(root)
    (root / ".synced").write_text(str(time.time()))
    if not quiet:
        print(f"synced {len(paths)} files from github.com/{repo} -> {root}")
    return root


def resolve_root(explicit: str | None = None, remote: bool = False) -> Path:
    if explicit:
        return Path(explicit)
    if os.environ.get("UGD_KB"):
        return Path(os.environ["UGD_KB"])
    loc = None if remote else local_root()
    if loc:
        return loc
    root = cache_root(repo_slug())
    stamp = root / ".synced"
    stale = not stamp.exists() or time.time() - float(stamp.read_text() or 0) > 86400
    if stale:
        try:
            return sync(quiet=True)
        except OSError as e:
            if not root.exists():
                die(f"no local knowledge/ and GitHub sync failed ({e})")
    return root


# --------------------------------------------------------------------------- notes

def parse(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    import yaml
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return {"_yaml_error": str(e)}, m.group(2)
    return (meta if isinstance(meta, dict) else {}), m.group(2)


def notes(root: Path) -> list[tuple[Path, dict, str]]:
    out = []
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root).as_posix()
        if rel in ("README.md", "INDEX.md", "TEMPLATE.md") or "/media/" in rel:
            continue
        meta, body = parse(p)
        out.append((p, meta, body))
    return out


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")[:60] or "note"


def _list(v) -> list:
    return v if isinstance(v, list) else ([v] if v else [])


# --------------------------------------------------------------------------- search

def search(root: Path, terms: list[str], kind=None, engine=None, genre=None, status=None, limit=10) -> list[dict]:
    terms = [t.lower() for t in terms if t.strip()]
    res = []
    for p, meta, body in notes(root):
        if kind and str(meta.get("kind", "")).lower() != kind:
            continue
        if engine and str(meta.get("engine", "")).lower() != engine.lower():
            continue
        if genre and slug(genre) not in slug(meta.get("genre", "")):
            continue
        if status and str(meta.get("status", "")).lower() != status.lower():
            continue
        fields = {
            5: str(meta.get("title", "")),
            4: " ".join(str(x) for x in [meta.get("game", ""), meta.get("genre", "")]),
            3: " ".join(str(x) for x in [meta.get("engine", ""), meta.get("engine_version", ""),
                                         *_list(meta.get("tags")), *_list(meta.get("tools")), *_list(meta.get("platforms"))]),
        }
        low = body.lower()
        score = 0
        for t in terms:
            score += sum(w for w, f in fields.items() if t in f.lower())
            score += min(5, low.count(t))
        if terms and score == 0:
            continue
        hits = [ln.strip() for ln in body.splitlines() if ln.strip() and any(t in ln.lower() for t in terms)][:3]
        res.append(dict(score=score, path=p.relative_to(root).as_posix(), title=meta.get("title"), kind=meta.get("kind"),
                        game=meta.get("game"), genre=meta.get("genre"), engine=meta.get("engine"),
                        engine_version=meta.get("engine_version"), status=meta.get("status"), hits=hits))
    res.sort(key=lambda r: -r["score"])
    return res[:limit]


# --------------------------------------------------------------------------- check

def check_note(path: Path) -> tuple[list[str], list[str]]:
    from ugd.release import SECRET_PATTERNS
    from ugd.scan import ENGINES
    fails, warns = [], []
    text = path.read_text(encoding="utf-8", errors="replace")
    meta, body = parse(path)
    is_template = path.name == "TEMPLATE.md"
    if not meta:
        return [f"no YAML front matter (start the file with --- ... --- ; see knowledge/TEMPLATE.md)"], []
    if "_yaml_error" in meta:
        return [f"front matter is not valid YAML: {meta['_yaml_error']}"], []
    kind = meta.get("kind", "project")
    if kind not in KINDS:
        fails.append(f"kind must be one of {', '.join(KINDS)}, not {kind!r}")
    for k in PROJECT_KEYS if kind == "project" else TECH_KEYS:
        if meta.get(k) in (None, "", []):
            fails.append(f"missing front-matter key: {k}")
    if kind == "project":
        for k in ("game", "genre", "engine_version"):
            if meta.get(k) in (None, "", []):
                warns.append(f"front-matter key {k} is empty")
        eng = meta.get("engine")
        if eng and eng not in ENGINES and eng not in ("unknown", "other"):
            warns.append(f"engine {eng!r} isn't one of ugd scan's keys ({', '.join(sorted(ENGINES))}, unknown, other)")
        plats = meta.get("platforms")
        if plats is not None and not isinstance(plats, list):
            fails.append("platforms must be a list, e.g. [windows, web]")
        for pl in _list(plats):
            if str(pl) not in PLATFORMS:
                warns.append(f"platform {pl!r} not one of: {', '.join(PLATFORMS)}")
        heads = [h.lower() for h in re.findall(r"^##\s+(.+)$", body, re.M)]
        for s in PROJECT_SECTIONS:
            if not any(h.startswith(s) for h in heads):
                fails.append(f"missing section: ## {s.capitalize()}")
        if any(h.startswith("gotchas") for h in heads) and not re.search(r"^##\s+Gotchas[^\n]*\n(?:[^\n]*\n)*?\s*1\.", body, re.M | re.I):
            warns.append("the Gotchas section has no numbered items")
    if meta.get("status") and meta["status"] not in STATUSES:
        fails.append(f"status {meta['status']!r} not one of: {', '.join(STATUSES)}")
    d = meta.get("date")
    if d and not isinstance(d, dt.date) and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(d)):
        fails.append(f"date must be YYYY-MM-DD, got {d!r}")
    if "agents" in meta and not isinstance(meta.get("agents"), list):
        fails.append('agents must be a list, e.g. ["Claude Code (Opus 5.5)"]')
    if not is_template:
        if meta.get("title") == TEMPLATE_TITLE:
            fails.append("title is still the template's example title")
        left = [ph for ph in PLACEHOLDERS if ph in text]
        if left:
            fails.append(f"unfilled template text: {', '.join(repr(x) for x in left)}")
    for label, rx in SECRET_PATTERNS:
        if rx.search(text):
            fails.append(f"{label} in the note: remove it")
    for b in re.findall(r"```[^\n]*\n(.*?)```", body, re.S):
        n = b.count("\n")
        if n > MAX_BLOCK_FAIL:
            fails.append(f"a {n}-line code block: link to your repo instead of pasting code (limit {MAX_BLOCK_FAIL})")
        elif n > MAX_BLOCK_WARN:
            warns.append(f"a {n}-line code block: keep snippets short (under {MAX_BLOCK_WARN} lines)")
    if re.search(r"[A-Z]:\\Users\\(?!<)[^\\\s`\"'<]+|/home/(?!<)[a-z_][a-z0-9_-]*/|/Users/(?!<|Shared/)[A-Za-z]+/", text):
        warns.append("absolute user path (use <you>, %USERPROFILE% or ~ instead)")
    if len(text.encode()) > MAX_NOTE_KB * 1024:
        warns.append(f"note is {len(text.encode()) // 1024} KB; split or trim it (limit {MAX_NOTE_KB} KB)")
    for m in re.finditer(r"!\[[^\]]*\]\(([^)\s]+)\)", body):
        src = m.group(1)
        if src.startswith("http"):
            continue
        img = (path.parent / src).resolve()
        if not img.exists():
            fails.append(f"image not found: {src}")
        elif img.stat().st_size > MAX_MEDIA_MB * 2**20:
            fails.append(f"image {src} is {img.stat().st_size / 2**20:.1f} MB (limit {MAX_MEDIA_MB} MB; link videos instead)")
    return fails, warns


# --------------------------------------------------------------------------- index

def build_index(root: Path) -> tuple[str, list[dict]]:
    rows = []
    for p, meta, _ in notes(root):
        rows.append(dict(path=p.relative_to(root).as_posix(),
                         **{k: (v.isoformat() if isinstance(v, dt.date) else v) for k, v in meta.items()}))
    projects = sorted([r for r in rows if r.get("kind", "project") == "project"],
                      key=lambda r: (str(r.get("engine", "")).lower(), str(r.get("game", "")).lower(), str(r.get("date", ""))))
    techs = sorted([r for r in rows if r.get("kind") == "technique"], key=lambda r: str(r.get("title", "")).lower())

    def esc(s):
        return str(s or "").replace("|", "\\|")

    lines = ["# Knowledge base index", "",
             "_Generated by `ugd kb index` from the notes' front matter; don't edit by hand. Machine-readable: `index.json`._", "",
             f"## Projects ({len(projects)} notes)", ""]
    if projects:
        lines += ["| Game | Note | Engine | Genre | Status | Agents | Date |", "|---|---|---|---|---|---|---|"]
        for r in projects:
            eng = esc(r.get("engine")) + (f" ({esc(r.get('engine_version'))})" if r.get("engine_version") else "")
            lines.append(f"| {esc(r.get('game'))} | [{esc(r.get('title'))}]({r['path']}) | {eng} | {esc(r.get('genre'))} | "
                         f"{esc(r.get('status'))} | {esc(', '.join(_list(r.get('agents'))))} | {esc(r.get('date'))} |")
    else:
        lines.append("No project notes yet. The first agent to finish a game here writes the first one (see [README.md](README.md)).")
    lines += ["", f"## Techniques ({len(techs)} notes)", ""]
    if techs:
        for r in techs:
            lines.append(f"- [{esc(r.get('title'))}]({r['path']}) · {esc(', '.join(str(t) for t in _list(r.get('tags'))))}")
    else:
        lines.append("No technique notes yet.")
    lines += ["", "## Engine playbooks", "",
              "Per-engine routes, commands and pitfalls live with the skills: "
              "[skills/make-any-game/references/engines/](../skills/make-any-game/references/engines/).", ""]
    return "\n".join(lines), rows


def write_index(root: Path) -> int:
    idx, rows = build_index(root)
    (root / "INDEX.md").write_text(idx, encoding="utf-8", newline="\n")
    (root / "index.json").write_text(json.dumps(rows, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    return len(rows)


# --------------------------------------------------------------------------- new / pr

TECH_BODY = """# {title}

> What this technique is for, in two sentences.

## When to use it

## How

## Gotchas
1. **Symptom.** ... **Cause:** ... **Fix:** ...

## Seen in
Links to project notes that used it.
"""


def new_note(root: Path, title: str, kind: str = "project", game: str | None = None, genre: str | None = None,
             engine: str | None = None, from_scan: str | None = None, agent: str | None = None, out: str | None = None) -> Path:
    import yaml
    meta, body = parse(root / "TEMPLATE.md")
    meta = dict(meta)
    meta.update(kind=kind, title=title, status="in-progress", date=dt.date.today().isoformat(),
                agents=[agent or os.environ.get("UGD_AGENT", "FILL IN: agent (model)")], humans=[], links=[], tags=[])
    if kind == "project":
        meta.update(game=game or "FILL IN: title", genre=genre or "FILL IN: genre", engine=engine or "unknown",
                    engine_version="FILL IN: exact version", platforms=[], tools=[])
        if from_scan:
            from ugd.scan import scan
            s = scan(from_scan)
            e = s.get("engine")
            if e:
                meta["engine"] = engine or e["key"]
                meta["engine_version"] = f"{e['name']} {e['version'] or 'FILL IN: exact version'}"
                plats = []
                for p in e.get("platforms") or []:
                    pl = p.lower()
                    key = ("web" if "web" in pl or "html" in pl else "windows" if "windows" in pl else "macos" if "mac" in pl
                           else "linux" if "linux" in pl or "x11" in pl else "android" if "android" in pl
                           else "ios" if "ios" in pl else None)
                    if key and key not in plats:
                        plats.append(key)
                meta["platforms"] = plats
            if not game:
                meta["game"] = s.get("name") or meta["game"]
        body = re.sub(r"^# .*$", lambda _: f"# {title}", body, count=1, flags=re.M)
        base = root / "projects" / slug(meta["engine"])
    else:
        for k in ("game", "genre", "engine", "engine_version", "platforms", "tools"):
            meta.pop(k, None)
        body = TECH_BODY.format(title=title)
        base = root / "techniques"
    front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=120)
    path = Path(out) if out else base / f"{slug(title)}.md"
    if path.exists():
        die(f"{path} exists: extend that note instead of writing a second one")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{front}---\n{body}", encoding="utf-8", newline="\n")
    return path


def open_pr(path: Path, yes: bool):
    """Branch + commit the note (and its media + regenerated index) + push (to a fork if needed) + gh pr create."""
    root = local_root()
    if not root:
        die("run this inside a clone of the repo (or your fork)")
    repo = repo_slug()
    path = path.resolve()
    meta, _ = parse(path)
    fails, _ = check_note(path)
    if fails:
        die("fix these first:\n  " + "\n  ".join(fails))
    branch = f"kb/{slug(meta.get('engine', '') or meta.get('kind', 'note'))}-{slug(meta.get('title', 'note'))}"[:80]
    title = f"kb: {meta.get('title')}" + (f" ({meta.get('engine')})" if meta.get("engine") else "")
    body = (f"Field note: **{meta.get('title')}**\n\n- kind: {meta.get('kind')}\n- game / genre: {meta.get('game', '-')} / "
            f"{meta.get('genre', '-')}\n- engine: {meta.get('engine', '-')} {meta.get('engine_version', '')}\n"
            f"- status: {meta.get('status')}\n- agents: {', '.join(_list(meta.get('agents')))}\n\n"
            "Checked with `ugd kb check`; index regenerated with `ugd kb index`.\n\n"
            "- [x] no secrets, and nothing I don't have the rights to share\n- [x] versions and verification written down\n")
    media = sorted((path.parent / "media").glob("*")) if (path.parent / "media").exists() else []
    can_push = False
    if shutil.which("gh"):
        r = subprocess.run(["gh", "api", f"repos/{repo}", "--jq", ".permissions.push"], capture_output=True, text=True)
        can_push = r.stdout.strip() == "true"
    remote = "origin" if can_push else "fork"
    cmds = [["git", "checkout", "-b", branch], ["ugd", "kb", "index"],
            ["git", "add", str(path), str(root / "INDEX.md"), str(root / "index.json"), *map(str, media)],
            ["git", "commit", "-m", title]]
    if not can_push:
        cmds.append(["gh", "repo", "fork", "--remote", "--remote-name", "fork"])
    cmds += [["git", "push", "-u", remote, branch],
             ["gh", "pr", "create", "--repo", repo, "--head", branch, "--title", title, "--body", body]]
    if not yes:
        print("dry run (add --yes after your human agrees):")
        for c in cmds:
            print("  " + " ".join(c if len(" ".join(c)) < 200 else c[:6] + ["..."]))
        return
    if not shutil.which("gh"):
        die("needs the GitHub CLI (gh), logged in; or push a branch and open the PR on github.com")
    write_index(root)
    for c in cmds:
        if c[:3] == ["ugd", "kb", "index"]:
            continue
        if c[:3] == ["gh", "repo", "fork"] and subprocess.run(["git", "remote", "get-url", "fork"], cwd=root.parent,
                                                                capture_output=True).returncode == 0:
            continue
        r = subprocess.run(c, cwd=root.parent, capture_output=True, text=True)
        if r.returncode:
            die(f"{' '.join(c[:4])} failed: {(r.stderr or r.stdout).strip()[-800:]}")
        if c[:3] == ["gh", "pr", "create"]:
            print(r.stdout.strip())


# --------------------------------------------------------------------------- CLI

def main(a):
    c = a.cmd
    if c == "sync":
        sync()
        return
    if c == "search":
        root = resolve_root(a.root, a.remote)
        res = search(root, a.terms, a.kind, a.engine, a.genre, a.status, a.limit)
        if a.json:
            print(json.dumps(res, indent=1))
            return
        if not res:
            print(f"nothing in {root} matches; you may be first: write it up afterwards (`ugd kb new`)")
        for r in res:
            facts = " | ".join(str(x) for x in (r["engine"], r["engine_version"], r["genre"], r["status"]) if x) or str(r["kind"])
            print(f"{r['path']}\n   {r['title']}  [{facts}]")
            for h in r["hits"]:
                print(f"     | {h.lstrip('> ')[:160]}")
        return
    if c == "show":
        root = resolve_root(a.root, a.remote)
        p = root / a.note
        if not p.exists():
            cands = [x for x in root.rglob("*.md") if a.note in x.as_posix()]
            if not cands:
                die(f"no note {a.note!r} in {root}")
            p = cands[0]
        print(p.read_text(encoding="utf-8"))
        return
    if c == "new":
        root = Path(a.root) if a.root else local_root()
        if not root:
            die("run inside a clone of the repo (knowledge/ is written there), or pass --root")
        p = new_note(root, a.title, a.kind, a.game, a.genre, a.engine, a.from_scan, a.agent, a.out)
        print(p)
        print(f"next: fill it in (Gotchas matter most), `ugd kb check {p}`, `ugd kb index`, then a PR (`ugd kb pr ...`)")
        return
    if c == "check":
        root = Path(a.root) if a.root else local_root()
        paths = [Path(x) for x in a.paths] or ([p for p, _, _ in notes(root)] if root else [])
        bad = 0
        for p in paths:
            fails, warns = check_note(p)
            for f in fails:
                print(f"FAIL {p}: {f}")
            for w in warns:
                print(f"WARN {p}: {w}")
            bad += bool(fails)
        if root and a.index and not a.paths:
            idx, _ = build_index(root)
            cur = (root / "INDEX.md").read_text(encoding="utf-8") if (root / "INDEX.md").exists() else ""
            if cur.replace("\r\n", "\n") != idx:
                print("FAIL knowledge/INDEX.md is out of date: run `ugd kb index`")
                bad += 1
        print(f"{'FAIL' if bad else 'PASS'}: {len(paths)} notes checked")
        raise SystemExit(1 if bad else 0)
    if c == "index":
        root = Path(a.root) if a.root else local_root()
        if not root:
            die("no local knowledge/ folder")
        n = write_index(root)
        print(f"{root / 'INDEX.md'}: {n} notes")
        return
    if c == "pr":
        open_pr(Path(a.note), a.yes)


def register(sub):
    import argparse
    p = sub.add_parser("kb", help="knowledge base of how games were built: search, write, check, PR",
                       description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cs = p.add_subparsers(dest="cmd", metavar="<cmd>")
    q = cs.add_parser("search", help="find prior notes (local clone or plugin, else the GitHub copy)")
    q.add_argument("terms", nargs="*")
    q.add_argument("--kind", choices=KINDS)
    q.add_argument("--engine")
    q.add_argument("--genre")
    q.add_argument("--status", choices=STATUSES)
    q.add_argument("--limit", type=int, default=10)
    q.add_argument("--json", action="store_true")
    q.add_argument("--remote", action="store_true", help="search the synced GitHub copy even inside a clone")
    q.add_argument("--root")
    q.set_defaults(func=main)
    q = cs.add_parser("show", help="print a note")
    q.add_argument("note")
    q.add_argument("--remote", action="store_true")
    q.add_argument("--root")
    q.set_defaults(func=main)
    q = cs.add_parser("new", help="scaffold a note from the template")
    q.add_argument("--title", required=True)
    q.add_argument("--kind", default="project", choices=KINDS)
    q.add_argument("--game")
    q.add_argument("--genre")
    q.add_argument("--engine", help="ugd scan's engine key; default from --from-scan")
    q.add_argument("--from-scan", help="pre-fill engine, version and platforms from `ugd scan <path>`")
    q.add_argument("--agent", help='e.g. "Claude Code (Opus 5.5)"; default $UGD_AGENT')
    q.add_argument("--out")
    q.add_argument("--root")
    q.set_defaults(func=main)
    q = cs.add_parser("check", help="validate notes (all, or the given paths)")
    q.add_argument("paths", nargs="*")
    q.add_argument("--index", action="store_true", help="also fail if INDEX.md is stale")
    q.add_argument("--root")
    q.set_defaults(func=main)
    q = cs.add_parser("index", help="regenerate knowledge/INDEX.md and index.json")
    q.add_argument("--root")
    q.set_defaults(func=main)
    cs.add_parser("sync", help="refresh the cached GitHub copy").set_defaults(func=main)
    q = cs.add_parser("pr", help="open a pull request with a note (dry run unless --yes)")
    q.add_argument("note")
    q.add_argument("--yes", action="store_true", help="really branch, push and open the PR")
    q.set_defaults(func=main)
