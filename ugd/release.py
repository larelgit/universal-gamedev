"""Check a game project, or an exported build, before you ship it.

    ugd release check .                 # the project: secrets, sensitive files, credits, licenses, paths
    ugd release check build/windows     # an exported build (detected by its .exe/.pck/index.html/...)
    ugd release check build/web --build # force build mode

FAIL  leaked keys (fal, OpenAI, Anthropic, GitHub, AWS, Google, Stripe, Slack, npm, private keys); .env files;
      keystores and certificates (.jks .keystore .p12 .pfx .p8 .mobileprovision); Steam credential files
      (config.vdf, ssfn*); Godot's export_credentials.cfg; steam_appid.txt inside a build
WARN  no README / LICENSE / CREDITS (projects); generated assets (fal_manifest.jsonl) without a fal credit;
      a Godot project without the engine's license notice; absolute user paths; files over 100 MB; file names
      that differ only by case; steam_appid.txt in a project; root-absolute paths (src="/...") in a web build
NOTE  reminders that need a human decision (AI disclosure when generated assets are present)

It's a lint, not a guarantee and not legal advice: also walk the release checklist in the ship-game skill.
Adapted from universal-modder's `um publish check`.
"""
from __future__ import annotations

import re
from pathlib import Path

from ugd.common import SKIP_DIRS, die, read_text, walk

SECRET_PATTERNS = [
    ("fal key", re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:[0-9a-f]{32}\b")),
    ("FAL_KEY assignment", re.compile(r"FAL_KEY\s*[=:]\s*['\"]?[A-Za-z0-9:_\-]{20,}")),
    ("Anthropic key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_\-]{32,}")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})")),
    ("AWS key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Stripe live key", re.compile(r"\b(?:sk|rk)_live_[0-9A-Za-z]{20,}")),
    ("Slack token", re.compile(r"\bxox[abposr]-[0-9A-Za-z\-]{10,}")),
    ("npm token", re.compile(r"_authToken\s*=\s*[^\s$]{10,}")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")),
]
TEXT_EXT = {
    ".gd", ".cs", ".c", ".cpp", ".h", ".hpp", ".py", ".lua", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".rs", ".go",
    ".java", ".kt", ".gml", ".rpy", ".hx", ".json", ".toml", ".ini", ".cfg", ".txt", ".md", ".xml", ".yaml", ".yml",
    ".tscn", ".tres", ".godot", ".uproject", ".sh", ".ps1", ".bat", ".cmd", ".html", ".htm", ".css", ".env", ".properties",
    ".gradle", ".plist", ".vdf", ".npmrc", ".csv", ".shader", ".gdshader", ".hlsl", ".glsl", ".wgsl",
}
KEY_FILES = {".jks": "Android keystore", ".keystore": "Android keystore", ".p12": "certificate bundle",
             ".pfx": "code-signing certificate", ".p8": "Apple private key", ".mobileprovision": "Apple provisioning profile"}
BUILD_MARKERS = (".exe", ".pck", ".app", ".x86_64", ".apk", ".aab", ".ipa", ".love", ".wasm")
DOC_NAMES = ("readme", "license", "licence", "copying", "credits", "notice", "third_party", "thirdparty", "copyright")
ENV_OK = {".env.example", ".env.sample", ".env.template"}
BIG = 100 << 20


def is_build(root: Path, files: list[Path]) -> bool:
    top = [p for p in files if p.parent == root]
    return any(p.suffix.lower() in BUILD_MARKERS for p in top) or (root / "index.html").exists() and not (root / "package.json").exists()


def check(folder: str, force_build: bool = False) -> int:
    root = Path(folder).expanduser().resolve()
    if not root.is_dir():
        die(f"not a folder: {root}")
    # builds keep everything (Binaries, Saved...); projects skip dependency and cache folders
    files = walk(root, max_files=100000, max_depth=20,
                 skip={".git", "node_modules", ".venv", "venv", "__pycache__"} if force_build else SKIP_DIRS)
    build = force_build or is_build(root, files)
    fails, warns, notes = [], [], []
    seen_lower: dict[str, str] = {}
    for f in files:
        rel = f.relative_to(root).as_posix()
        name, suf = f.name.lower(), f.suffix.lower()
        low = rel.lower()
        if low in seen_lower and seen_lower[low] != rel:
            warns.append(f"names differ only by case: {seen_lower[low]} vs {rel} (breaks on Windows/macOS and web hosts)")
        seen_lower.setdefault(low, rel)
        if (name == ".env" or name.startswith(".env.") or name.endswith(".env")) and name not in ENV_OK:
            fails.append(f"env file (secrets?): {rel}")
        if suf in KEY_FILES:
            fails.append(f"{KEY_FILES[suf]}: {rel} (keep signing material out of repos and builds)")
        if name == "config.vdf" or name.startswith("ssfn"):
            fails.append(f"Steam credential file: {rel}")
        if name == "export_credentials.cfg":
            fails.append(f"Godot export credentials (keystore passwords): {rel}")
        if name == "steam_appid.txt":
            (fails if build else warns).append(f"steam_appid.txt: {rel} (for local testing only; never ship it in a depot)")
        try:
            size = f.stat().st_size
        except OSError:
            continue
        if size > BIG:
            warns.append(f"large file ({size >> 20} MB): {rel} (store limits, Git LFS, download size)")
        if suf in TEXT_EXT or name in (".env", ".npmrc"):
            txt = read_text(f)
            if not txt:
                continue
            for label, rx in SECRET_PATTERNS:
                if rx.search(txt):
                    fails.append(f"{label} in {rel}")
            if re.search(r"[A-Z]:\\Users\\(?!<)[^\\\s\"'<]+\\|/home/(?!<)[a-z_][a-z0-9_-]*/|/Users/(?!<|Shared/)[A-Za-z][^/\s]*/", txt):
                warns.append(f"absolute user path in {rel}")
            if build and suf in (".html", ".htm", ".css") and re.search(r"""(?:src|href)\s*=\s*["']/(?!/)|url\(\s*["']?/(?!/)""", txt):
                warns.append(f"root-absolute path in {rel}: use relative paths so the build runs from a subfolder (itch.io)")
    top_names = [p.name.lower() for p in root.iterdir()] if root.exists() else []
    docs = [root / n for n in [p.name for p in root.iterdir()] if n.lower().startswith(DOC_NAMES)] if root.exists() else []
    doc_text = "\n".join(read_text(p).lower() for p in docs if p.is_file())
    if not build:
        for want in ("readme", "license", "credits"):
            if not any(n.startswith(want) or (want == "license" and n.startswith(("licence", "copying"))) for n in top_names):
                warns.append(f"no {want.upper()} at the top level"
                             + {"readme": " (what it is, how to run and build it)",
                                "license": " (the license for your code)",
                                "credits": " (engine, libraries, fonts, assets with sources and licenses, tools)"}[want])
        if (root / "project.godot").exists() and "godot" not in doc_text:
            warns.append("Godot project without the engine's license notice in LICENSE/CREDITS (Godot is MIT: credit it)")
    manifests = [f for f in files if f.name == "fal_manifest.jsonl"]
    if manifests:
        if "fal" not in doc_text:
            warns.append("generated assets (fal_manifest.jsonl) but no fal credit in README/CREDITS (name the models)")
        notes.append("generated assets present: disclose AI content where stores ask (Steam Content Survey, itch.io's AI field)")
    for x in fails:
        print("FAIL ", x)
    for x in warns:
        print("WARN ", x)
    for x in notes:
        print("NOTE ", x)
    kind = "build" if build else "project"
    print(f"{'FAIL' if fails else 'WARN' if warns else 'PASS'}: {kind}, {len(files)} files, "
          f"{len(fails)} failures, {len(warns)} warnings")
    return 1 if fails else 0


def main(a):
    raise SystemExit(check(a.folder, a.build))


def register(sub):
    import argparse
    p = sub.add_parser("release", help="lint a project or exported build before shipping (secrets, keys, credits)",
                       description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cs = p.add_subparsers(dest="cmd", metavar="<cmd>")
    q = cs.add_parser("check", help="check a project or build folder")
    q.add_argument("folder", nargs="?", default=".")
    q.add_argument("--build", action="store_true", help="treat the folder as an exported build")
    q.set_defaults(func=main)
