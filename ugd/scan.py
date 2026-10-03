"""Fingerprint a game project: engine + version, language, tests, CI, and how to run, test and export it.

    ugd scan                       # the project in the current folder
    ugd scan path/to/game --json   # machine-readable, for agents
    ugd scan --tools               # engines, SDKs and tools installed on this machine (and their versions)

The report ends with the commands that run, test and export the project and the engine playbook to read next
(skills/make-any-game/references/engines/*.md). Everything here is read-only: it reads files and asks
installed tools for their version, nothing else. Commands are suggestions built from what's on disk: check
them against the playbook and the project's own README before relying on them.
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from ugd.common import die, read_text, version_of, walk

# key -> (display name, playbook file in skills/make-any-game/references/engines/)
ENGINES = {
    "godot": ("Godot", "godot.md"),
    "unity": ("Unity", "unity.md"),
    "unreal": ("Unreal Engine", "unreal.md"),
    "phaser": ("Phaser", "web.md"),
    "threejs": ("three.js", "web.md"),
    "pixijs": ("PixiJS", "web.md"),
    "babylonjs": ("Babylon.js", "web.md"),
    "kaplay": ("Kaplay / Kaboom", "web.md"),
    "excalibur": ("Excalibur", "web.md"),
    "playcanvas": ("PlayCanvas", "web.md"),
    "web": ("Web (canvas / other)", "web.md"),
    "bevy": ("Bevy", "bevy-rust.md"),
    "macroquad": ("macroquad", "bevy-rust.md"),
    "fyrox": ("Fyrox", "bevy-rust.md"),
    "ggez": ("ggez", "bevy-rust.md"),
    "love2d": ("LÖVE", "love2d.md"),
    "pygame": ("pygame-ce / pygame", "python.md"),
    "arcade": ("Python Arcade", "python.md"),
    "pyxel": ("Pyxel", "python.md"),
    "ursina": ("Ursina", "python.md"),
    "panda3d": ("Panda3D", "python.md"),
    "monogame": ("MonoGame", "dotnet.md"),
    "fna": ("FNA", "dotnet.md"),
    "kni": ("KNI", "dotnet.md"),
    "stride": ("Stride", "other-engines.md"),
    "raylib": ("raylib", "native.md"),
    "sdl": ("SDL", "native.md"),
    "sfml": ("SFML", "native.md"),
    "native": ("C/C++ (custom engine)", "native.md"),
    "gamemaker": ("GameMaker", "gamemaker.md"),
    "renpy": ("Ren'Py", "narrative.md"),
    "rpgmaker": ("RPG Maker MV/MZ", "narrative.md"),
    "twine": ("Twine (Twee)", "narrative.md"),
    "defold": ("Defold", "other-engines.md"),
    "gdevelop": ("GDevelop", "other-engines.md"),
    "construct": ("Construct 3", "other-engines.md"),
    "ebitengine": ("Ebitengine", "other-engines.md"),
    "haxeflixel": ("HaxeFlixel", "other-engines.md"),
    "heaps": ("Heaps", "other-engines.md"),
    "solar2d": ("Solar2D", "other-engines.md"),
    "cocos": ("Cocos Creator", "other-engines.md"),
    "flax": ("Flax", "other-engines.md"),
    "o3de": ("O3DE", "other-engines.md"),
    "pico8": ("PICO-8", "other-engines.md"),
    "tic80": ("TIC-80", "other-engines.md"),
    "roblox": ("Roblox (Rojo)", "other-engines.md"),
}
PLAYBOOK_DIR = "skills/make-any-game/references/engines"


@dataclass
class Hit:
    key: str
    score: int
    version: str | None = None
    language: str | None = None
    evidence: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    commands: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    name: str | None = None  # the project's own name, when the engine stores one
    platforms: list[str] = field(default_factory=list)


class Index:
    """A bounded listing of the project, with cheap lookups by name and extension."""

    def __init__(self, root: Path):
        self.root = root
        self.files = walk(root)
        self.rel = [p.relative_to(root).as_posix() for p in self.files]
        self.by_name: dict[str, list[str]] = defaultdict(list)
        for r in self.rel:
            self.by_name[r.rsplit("/", 1)[-1].lower()].append(r)
        self.exts = Counter(Path(r).suffix.lower() for r in self.rel)

    def has(self, rel: str) -> bool:
        return (self.root / rel).is_file()

    def isdir(self, rel: str) -> bool:
        return (self.root / rel).is_dir()

    def text(self, rel: str) -> str:
        return read_text(self.root / rel)

    def named(self, name: str, max_depth: int = 99) -> list[str]:
        return [r for r in self.by_name.get(name.lower(), []) if r.count("/") <= max_depth]

    def with_ext(self, *exts: str, max_depth: int = 99) -> list[str]:
        exts = tuple(e.lower() for e in exts)
        return [r for r in self.rel if r.lower().endswith(exts) and r.count("/") <= max_depth]


def _q(path: str) -> str:
    return f'"{path}"' if " " in path else path


def _dir_of(rel: str) -> str:
    d = rel.rsplit("/", 1)[0] if "/" in rel else "."
    return d


# --------------------------------------------------------------------------- detectors

def det_godot(ix: Index, hits: list[Hit]):
    cands = ix.named("project.godot", max_depth=1)
    if not cands:
        return
    pg = sorted(cands, key=lambda r: r.count("/"))[0]
    pdir = _dir_of(pg)
    t = ix.text(pg)
    ver = None
    m = re.search(r"config/features\s*=\s*PackedStringArray\(([^)]*)\)", t)
    if m:
        vm = re.search(r'"(\d+\.\d+)"', m.group(1))
        ver = vm.group(1) if vm else None
    cv = re.search(r"^config_version\s*=\s*(\d+)", t, re.M)
    if not ver and cv:
        ver = {"5": "4.x", "4": "3.x", "3": "3.x"}.get(cv.group(1))
    name = re.search(r'config/name\s*=\s*"([^"]*)"', t)
    csproj = [r for r in ix.with_ext(".csproj") if "Godot.NET.Sdk" in ix.text(r)]
    has_gd = ix.exts[".gd"] > 0
    lang = "GDScript + C#" if (csproj and has_gd) else "C#" if csproj else "GDScript"
    h = Hit("godot", 10, ver, lang, [pg], name=name.group(1) if name else None)
    prefix = "" if pdir == "." else pdir + "/"
    testdir = next((d for d in ("test", "tests") if ix.isdir(prefix + d)), "test")
    if ix.isdir(prefix + "addons/gut"):
        h.tests.append("GUT (addons/gut)")
        h.commands.setdefault("test", []).append(
            f"godot --headless --path {_q(pdir)} -s addons/gut/gut_cmdln.gd -gdir=res://{testdir} -gexit")
    if ix.isdir(prefix + "addons/gdUnit4"):
        h.tests.append("gdUnit4 (addons/gdUnit4)")
        runner = "runtest.cmd" if os.name == "nt" else "runtest.sh"
        h.commands.setdefault("test", []).append(
            f"cd {_q(pdir)} && addons/gdUnit4/{runner} -a res://{testdir}   (needs GODOT_BIN)")
    h.commands["run"] = f"godot --path {_q(pdir)}"
    h.commands["import"] = f"godot --headless --path {_q(pdir)} --import"
    h.commands["headless"] = f"godot --headless --path {_q(pdir)} --quit-after 600 -- --autotest smoke"
    presets = ix.text(prefix + "export_presets.cfg")
    exports = []
    for sec in re.split(r"^\[preset\.\d+\]\s*$", presets, flags=re.M)[1:]:
        pname = re.search(r'^name\s*=\s*"([^"]*)"', sec, re.M)
        ppath = re.search(r'^export_path\s*=\s*"([^"]*)"', sec, re.M)
        plat = re.search(r'^platform\s*=\s*"([^"]*)"', sec, re.M)
        if pname:
            out = ppath.group(1) if ppath and ppath.group(1) else f"build/{re.sub(r'[^a-z0-9]+', '-', pname.group(1).lower())}/"
            exports.append(f'godot --headless --path {_q(pdir)} --export-release "{pname.group(1)}" {_q(out)}')
            if plat:
                h.platforms.append(plat.group(1))
    if exports:
        h.commands["export"] = exports
    else:
        h.notes.append("no export_presets.cfg yet: add presets in Project → Export (needs export templates)")
    if csproj:
        h.notes.append("C# project: needs the .NET build of Godot and the .NET SDK; C# can't export to Web")
    hits.append(h)


def det_unity(ix: Index, hits: list[Hit]):
    pv = next((r for r in ix.named("ProjectVersion.txt", max_depth=2) if r.endswith("ProjectSettings/ProjectVersion.txt")), None)
    if not pv:
        return
    pdir = pv[: -len("ProjectSettings/ProjectVersion.txt")].rstrip("/") or "."
    t = ix.text(pv)
    m = re.search(r"m_EditorVersion:\s*(\S+)", t)
    h = Hit("unity", 10, m.group(1) if m else None, "C#", [pv])
    prefix = "" if pdir == "." else pdir + "/"
    manifest = ix.text(prefix + "Packages/manifest.json")
    deps = {}
    try:
        deps = json.loads(manifest).get("dependencies", {}) if manifest else {}
    except ValueError:
        pass
    if "com.unity.render-pipelines.universal" in deps:
        h.notes.append("render pipeline: URP")
    elif "com.unity.render-pipelines.high-definition" in deps:
        h.notes.append("render pipeline: HDRP")
    if "com.unity.inputsystem" in deps:
        h.notes.append("Input System package")
    test_asm = [r for r in ix.with_ext(".asmdef") if re.search(r"UNITY_INCLUDE_TESTS|nunit\.framework", ix.text(r))]
    if "com.unity.test-framework" in deps or test_asm:
        h.tests.append(f"Unity Test Framework ({len(test_asm)} test assemblies)")
    unity = "<Unity>"
    eds = unity_editors()
    if h.version and h.version in eds:
        unity = _q(eds[h.version])
    elif eds:
        h.notes.append(f"editor {h.version} not found among installed: {', '.join(sorted(eds))}")
    h.commands["test"] = [
        f"{unity} -batchmode -nographics -projectPath {_q(pdir)} -runTests -testPlatform EditMode -testResults results/editmode.xml -logFile -",
        f"{unity} -batchmode -projectPath {_q(pdir)} -runTests -testPlatform PlayMode -testResults results/playmode.xml -logFile -",
    ]
    builders = [r for r in ix.with_ext(".cs") if "/Editor/" in r and "BuildPipeline.BuildPlayer" in ix.text(r)]
    h.commands["export"] = [f"{unity} -batchmode -quit -projectPath {_q(pdir)} -executeMethod <Class.Method> -logFile -"
                            + (f"   (build script: {builders[0]})" if builders else "   (add an editor build script first)")]
    h.notes.append("close the Unity editor before batch runs (one instance per project)")
    hits.append(h)


def det_unreal(ix: Index, hits: list[Hit]):
    ups = ix.with_ext(".uproject", max_depth=1)
    if not ups:
        return
    up = sorted(ups, key=lambda r: r.count("/"))[0]
    meta = {}
    try:
        meta = json.loads(ix.text(up) or "{}")
    except ValueError:
        pass
    assoc = str(meta.get("EngineAssociation", "") or "")
    cpp = bool(meta.get("Modules")) or ix.isdir("Source" if _dir_of(up) == "." else _dir_of(up) + "/Source")
    name = Path(up).stem
    ver = assoc if re.match(r"^\d+\.\d+", assoc) else ("source build " + assoc if assoc else None)
    h = Hit("unreal", 10, ver, "C++ + Blueprints" if cpp else "Blueprints", [up], name=name)
    ue = "<UE>"
    installs = unreal_installs()
    if assoc in installs:
        ue = installs[assoc]
    upq = _q(up)
    if cpp:
        h.commands["build"] = f'"{ue}/Engine/Build/BatchFiles/Build.bat" {name}Editor Win64 Development -Project={upq} -WaitMutex'
    h.commands["run"] = f'"{ue}/Engine/Binaries/Win64/UnrealEditor.exe" {upq} -game -windowed -ResX=1280 -ResY=720'
    h.commands["test"] = [f'"{ue}/Engine/Binaries/Win64/UnrealEditor-Cmd.exe" {upq} -ExecCmds="Automation RunTests {name}.;Quit" '
                          "-unattended -nopause -nullrhi -nosplash -log -ReportExportPath=Saved/TestReport"]
    h.commands["export"] = [f'"{ue}/Engine/Build/BatchFiles/RunUAT.bat" BuildCookRun -project={upq} -noP4 -platform=Win64 '
                            "-clientconfig=Shipping -build -cook -stage -pak -archive -archivedirectory=Build"]
    hits.append(h)


WEB_LIBS = [("phaser", "phaser"), ("three", "threejs"), ("@react-three/fiber", "threejs"), ("pixi.js", "pixijs"),
            ("@babylonjs/core", "babylonjs"), ("babylonjs", "babylonjs"), ("kaplay", "kaplay"), ("kaboom", "kaplay"),
            ("excalibur", "excalibur"), ("playcanvas", "playcanvas")]
WEB_GAMEY = ("matter-js", "planck", "@dimforge/rapier2d", "@dimforge/rapier3d", "@dimforge/rapier2d-compat",
             "@dimforge/rapier3d-compat", "howler", "cannon-es", "melonjs", "littlejsengine")


def det_web(ix: Index, hits: list[Hit]):
    if not ix.has("package.json"):
        return
    try:
        pkg = json.loads(ix.text("package.json") or "{}")
    except ValueError:
        return
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    if isinstance(pkg.get("creator"), dict):  # Cocos Creator keeps its version here
        hits.append(Hit("cocos", 10, str(pkg["creator"].get("version") or "") or None, "TypeScript", ["package.json (creator)"]))
        return
    found = [(dep, key) for dep, key in WEB_LIBS if dep in deps]
    lang = "TypeScript" if (ix.has("tsconfig.json") or "typescript" in deps) else "JavaScript"
    pm = ("pnpm" if ix.has("pnpm-lock.yaml") else "yarn" if ix.has("yarn.lock")
          else "bun" if (ix.has("bun.lock") or ix.has("bun.lockb")) else "npm")
    scripts = pkg.get("scripts", {}) or {}
    tests = [t for t in ("vitest", "jest", "@playwright/test", "cypress", "mocha") if t in deps]
    if any(ix.has(f"playwright.config.{e}") for e in ("ts", "js", "mjs")) and "@playwright/test" not in tests:
        tests.append("@playwright/test")

    def runs(s: str) -> str:
        return f"{pm} test" if s == "test" else f"{pm} run {s}"

    commands = {}
    for k, names in (("run", ("dev", "start", "serve")), ("export", ("build",)), ("preview", ("preview",))):
        s = next((n for n in names if n in scripts), None)
        if s:
            commands[k] = runs(s) if k != "export" else [runs(s)]
    tcmds = [runs(s) for s in scripts if s == "test" or s.startswith("test:") or s in ("e2e", "unit")]
    if "@playwright/test" in tests and not any("playwright" in str(scripts.get(s, "")) for s in scripts):
        tcmds.append("npx playwright test")
    if "vitest" in tests and not any("vitest" in str(scripts.get(s, "")) for s in scripts):
        tcmds.append("npx vitest run")
    if tcmds:
        commands["test"] = tcmds
    bundler = next((b for b in ("vite", "webpack", "parcel", "esbuild", "rollup") if b in deps), None)
    notes = [f"package manager: {pm}" + (f", bundler: {bundler}" if bundler else "")]
    if bundler == "vite":
        vcfg = next((ix.text(f"vite.config.{e}") for e in ("ts", "js", "mjs") if ix.has(f"vite.config.{e}")), "")
        if not re.search(r"base\s*:", vcfg):
            notes.append("vite.config has no `base`: set base: './' so builds work in subfolders (itch.io)")
    if found:
        for i, (dep, key) in enumerate(found):
            ver = str(deps.get(dep, "")).lstrip("^~>=<") or None
            hits.append(Hit(key, 8 if i == 0 else 6, ver, lang, [f"package.json: {dep}"], tests=list(tests),
                            commands=dict(commands) if i == 0 else {}, notes=list(notes) if i == 0 else [],
                            name=pkg.get("name")))
    elif any(d in deps for d in WEB_GAMEY) or (ix.has("index.html") and "<canvas" in ix.text("index.html")):
        hits.append(Hit("web", 4, None, lang, ["package.json + canvas/game libraries"], tests=tests, commands=commands,
                        notes=notes, name=pkg.get("name")))


RUST_ENGINES = ("bevy", "macroquad", "fyrox", "ggez")


def det_rust(ix: Index, hits: list[Hit]):
    if not ix.has("Cargo.toml"):
        return
    t = ix.text("Cargo.toml")
    for i, eng in enumerate(e for e in RUST_ENGINES if re.search(rf"^\s*{e}\s*=", t, re.M)):
        m = re.search(rf'^\s*{eng}\s*=\s*(?:"([^"]+)"|\{{[^}}]*?version\s*=\s*"([^"]+)")', t, re.M)
        ver = (m.group(1) or m.group(2)) if m else None
        h = Hit(eng, 8 if i == 0 else 5, ver, "Rust", [f"Cargo.toml: {eng}"])
        h.commands = {"run": "cargo run", "test": ["cargo test"], "export": ["cargo build --release"]}
        if ix.has("Trunk.toml") or ix.has("index.html"):
            h.commands["web"] = "trunk serve   |   trunk build --release"
        if eng == "bevy" and "dynamic_linking" in t:
            h.notes.append("dynamic_linking is enabled: keep it out of release builds")
        hits.append(h)


def det_love(ix: Index, hits: list[Hit]):
    if not ix.has("main.lua"):
        return
    main, conf = ix.text("main.lua"), ix.text("conf.lua")
    if ix.has("build.settings"):  # Solar2D, not LÖVE
        hits.append(Hit("solar2d", 9, None, "Lua", ["main.lua + build.settings"]))
        return
    if "love." not in main + conf:
        return
    m = re.search(r't\.version\s*=\s*"([^"]+)"', conf)
    h = Hit("love2d", 9, m.group(1) if m else None, "Lua", ["main.lua" + (" + conf.lua" if conf else "")])
    h.commands = {"run": "love .   (lovec . on Windows for console output)", "export": ["makelove   (or zip the folder as game.love)"]}
    if ix.isdir("spec") or ix.has(".busted"):
        h.tests.append("busted (spec/)")
        h.commands["test"] = ["busted spec/"]
    hits.append(h)


PY_LIBS = [("pygame", r"^\s*(?:import|from)\s+pygame\b", "pygame"), ("arcade", r"^\s*(?:import|from)\s+arcade\b", "arcade"),
           ("pyxel", r"^\s*(?:import|from)\s+pyxel\b", "pyxel"), ("ursina", r"^\s*(?:import|from)\s+ursina\b", "ursina"),
           ("panda3d", r"^\s*(?:import|from)\s+(?:panda3d|direct\.showbase)\b", "panda3d")]


def det_python(ix: Index, hits: list[Hit]):
    pys = [r for r in ix.with_ext(".py") if "/site-packages/" not in r][:400]
    if not pys:
        return
    counts = Counter()
    for r in pys:
        t = ix.text(r)
        for key, rx, _ in PY_LIBS:
            if re.search(rx, t, re.M):
                counts[key] += 1
    if not counts:
        return
    reqs = " ".join(ix.text(r) for r in ("requirements.txt", "requirements-dev.txt", "pyproject.toml", "setup.cfg") if ix.has(r))
    uv = ix.has("uv.lock") or "[tool.uv" in reqs
    py = "uv run python" if uv else "python"
    entry = next((e for e in ("main.py", "game.py", "run.py", "app.py") if ix.has(e)), None)
    for i, (key, n) in enumerate(counts.most_common()):
        dist = "pygame-ce" if key == "pygame" and "pygame-ce" in reqs else {"panda3d": "panda3d"}.get(key, key)
        m = re.search(rf"{re.escape(dist)}\s*(?:[=<>~!]=?|\s)\s*([0-9][0-9a-zA-Z.*]*)", reqs)
        h = Hit(key, (8 if n >= 2 else 6) if i == 0 else 4, m.group(1) if m else None, "Python",
                [f"{n} file(s) import {key}"] + ([f"declares {dist}"] if dist in reqs else []))
        if i == 0:
            if entry:
                h.commands["run"] = f"{py} {entry}"
            has_tests = ix.isdir("tests") or any(Path(r).name.startswith("test_") for r in pys)
            if has_tests:
                h.tests.append("pytest")
                pre = "SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy " if key == "pygame" else ""
                h.commands["test"] = [f"{pre}{'uv run ' if uv else ''}pytest"]
            if key == "pygame":
                if "pygame-ce" not in reqs and "pygame" in reqs:
                    h.notes.append("declares `pygame`, not `pygame-ce` (the maintained fork); never install both")
                h.commands["export"] = [f"{'uv run ' if uv else ''}pyinstaller --windowed {entry or 'main.py'}",
                                        f"{'uv run ' if uv else ''}pygbag --build .   (web; needs an async main loop)"]
        hits.append(h)


DOTNET_PKGS = [(r"MonoGame\.Framework\.", "monogame"), (r"nkast\.Xna\.Framework|\bKNI\b", "kni"),
               (r"\bFNA(?:\.Core)?\.csproj|Include=\"FNA\"", "fna"), (r"\bStride\.Engine\b", "stride"),
               (r"\bRaylib-cs\b", "raylib")]


def det_dotnet(ix: Index, hits: list[Hit]):
    projs = [r for r in ix.with_ext(".csproj", max_depth=3)]
    if not projs:
        return
    game_proj, tests = None, []
    seen: dict[str, Hit] = {}
    for r in projs:
        t = ix.text(r)
        if "Godot.NET.Sdk" in t or "UnityEngine" in t:
            continue
        if "Microsoft.NET.Test.Sdk" in t:
            fw = next((f for f in ("xunit", "NUnit", "MSTest") if f.lower() in t.lower()), "test")
            tests.append(f"{fw} ({r})")
            continue
        for rx, key in DOTNET_PKGS:
            if re.search(rx, t) and key not in seen:
                m = re.search(r"(?:" + rx + r')[^"]*"\s+Version="([^"]+)"', t)
                seen[key] = Hit(key, 8, m.group(1) if m else None, "C#", [f"{r}"])
                game_proj = game_proj or r
    for i, (key, h) in enumerate(seen.items()):
        if i == 0:
            h.tests = tests
            h.commands = {"run": f"dotnet run --project {_q(game_proj)}",
                          "export": [f"dotnet publish {_q(game_proj)} -c Release -r win-x64 --self-contained"]}
            if tests:
                h.commands["test"] = ["dotnet test"]
            if key == "monogame" and not ix.named("Content.mgcb"):
                h.notes.append("no Content.mgcb found: content loads from raw files or a Content Builder project")
        else:
            h.score = 5
        hits.append(h)


NATIVE_LIBS = [("raylib", r"\braylib\b"), ("sdl", r"\bSDL[23]?\b"), ("sfml", r"\bSFML\b")]


def det_native(ix: Index, hits: list[Hit]):
    cm = ix.text("CMakeLists.txt") if ix.has("CMakeLists.txt") else ""
    srcs = ix.with_ext(".c", ".cpp", ".cc", ".h", ".hpp")
    if not cm and not srcs:
        return
    sample = cm + "\n".join(ix.text(r)[:4000] for r in srcs[:60])
    found = [key for key, rx in NATIVE_LIBS if re.search(rx, sample)]
    if not found and not (cm and srcs):
        return
    for i, key in enumerate(found or ["native"]):
        m = re.search(r"GIT_TAG\s+v?([0-9][\w.\-]*)", cm) if key == "raylib" else None
        h = Hit(key, (7 if found else 3) if i == 0 else 4, m.group(1) if m else None, "C/C++",
                ["CMakeLists.txt" if cm else f"{len(srcs)} C/C++ files"])
        if i == 0 and cm:
            h.commands = {"build": "cmake -B build -DCMAKE_BUILD_TYPE=Debug && cmake --build build --config Debug",
                          "export": ["cmake -B build-rel -DCMAKE_BUILD_TYPE=Release && cmake --build build-rel --config Release"]}
            if re.search(r"enable_testing|add_test|doctest|Catch2|GTest", cm):
                h.tests.append("CTest")
                h.commands["test"] = ["ctest --test-dir build --output-on-failure"]
            if key == "raylib":
                h.commands["web"] = "emcmake cmake -B build-web -DPLATFORM=Web && cmake --build build-web"
        hits.append(h)


def det_markers(ix: Index, hits: list[Hit]):
    """Engines identified by a single project file."""
    for r in ix.with_ext(".yyp", max_depth=1):
        m = re.search(r'"IDEVersion"\s*:\s*"([^"]+)"', ix.text(r))
        hits.append(Hit("gamemaker", 10, m.group(1) if m else None, "GML", [r],
                        commands={"run": "run from the GameMaker IDE", "export": ["Igor (see gamemaker.md; copy the IDE's own Igor command line)"]}))
    rpy = [r for r in ix.with_ext(".rpy") if r.startswith("game/") or "/game/" in r]
    if rpy:
        base = rpy[0].split("game/")[0].rstrip("/") or "."
        hits.append(Hit("renpy", 10, None, "Ren'Py script + Python", [f"{len(rpy)} .rpy files in game/"],
                        commands={"test": [f"renpy.sh {base} lint", f"renpy.sh {base} test   (Ren'Py 8.5+)"],
                                  "export": [f"renpy.sh launcher distribute {base}"]}))
    if ix.named("game.rmmzproject", 1) or ix.named("Game.rpgproject", 1):
        mz = bool(ix.named("game.rmmzproject", 1))
        hits.append(Hit("rpgmaker", 10, "MZ" if mz else "MV", "JavaScript", ["RPG Maker project file"]))
    if ix.has("game.project") and "[project]" in ix.text("game.project"):
        hits.append(Hit("defold", 10, None, "Lua", ["game.project"],
                        commands={"export": ["java -jar bob.jar --platform x86_64-win32 --archive --bundle-output build/ resolve build bundle"]}))
    if ix.has("game.json") and '"gdVersion"' in ix.text("game.json"):
        m = re.search(r'"gdVersion"\s*:\s*\{[^}]*"major"\s*:\s*(\d+)[^}]*"minor"\s*:\s*(\d+)', ix.text("game.json"))
        hits.append(Hit("gdevelop", 10, f"{m.group(1)}.{m.group(2)}" if m else None, "events + JavaScript", ["game.json"]))
    if ix.named("project.c3proj", 2) or ix.with_ext(".c3p", max_depth=1):
        hits.append(Hit("construct", 10, None, "events + JavaScript", ["Construct project"]))
    if ix.has("go.mod"):
        m = re.search(r"github\.com/hajimehoshi/ebiten/v2\s+v([\w.\-]+)", ix.text("go.mod"))
        if m:
            hits.append(Hit("ebitengine", 8, m.group(1), "Go", ["go.mod"],
                            commands={"run": "go run .", "test": ["go test ./..."], "export": ["go build -o build/ ."]}))
    if ix.has("Project.xml") and re.search(r'haxelib\s+name="flixel"', ix.text("Project.xml")):
        hits.append(Hit("haxeflixel", 9, None, "Haxe", ["Project.xml"],
                        commands={"run": "lime test windows   |   lime test html5", "export": ["lime build html5"]}))
    if any("-lib heaps" in ix.text(r) for r in ix.with_ext(".hxml", max_depth=1)):
        hits.append(Hit("heaps", 9, None, "Haxe", [".hxml with heaps"]))
    if ix.with_ext(".flaxproj", max_depth=1):
        hits.append(Hit("flax", 10, None, "C# / C++", ["*.flaxproj"]))
    if ix.has("project.json"):
        t = ix.text("project.json")
        if '"project_name"' in t and ('"engine"' in t or "o3de" in t.lower()):
            hits.append(Hit("o3de", 9, None, "C++ / Lua", ["project.json"]))
    if ix.with_ext(".p8", max_depth=2):
        hits.append(Hit("pico8", 9, None, "Lua (PICO-8)", ["*.p8 cart"], commands={"run": "pico8 -run <cart>.p8"}))
    if ix.with_ext(".tic", max_depth=2):
        hits.append(Hit("tic80", 9, None, "TIC-80", ["*.tic cart"]))
    if ix.has("default.project.json"):
        hits.append(Hit("roblox", 10, None, "Luau", ["default.project.json (Rojo)"],
                        commands={"run": "rojo serve   (then connect from Roblox Studio)", "export": ["rojo build -o game.rbxlx"]}))
    if ix.with_ext(".twee", ".tw"):
        hits.append(Hit("twine", 8, None, "Twee", ["*.twee"], commands={"export": ["tweego -o build/index.html src/"]}))


DETECTORS = [det_godot, det_unity, det_unreal, det_web, det_rust, det_love, det_python, det_dotnet, det_native, det_markers]


# --------------------------------------------------------------------------- installed engines and tools

def unity_editors() -> dict[str, str]:
    """version -> editor executable, from Unity Hub's default install folders."""
    pats = [r"C:\Program Files\Unity\Hub\Editor\*\Editor\Unity.exe",
            "/Applications/Unity/Hub/Editor/*/Unity.app/Contents/MacOS/Unity",
            str(Path.home() / "Unity/Hub/Editor/*/Editor/Unity")]
    out = {}
    for pat in pats:
        for p in glob.glob(pat):
            parts = Path(p).parts
            idx = [i for i, x in enumerate(parts) if x == "Editor"]
            ver = parts[idx[0] + 1] if idx and idx[0] + 1 < len(parts) else Path(p).parent.name
            out[ver] = p
    return out


def unreal_installs() -> dict[str, str]:
    """'5.8' -> engine root, from the Epic Games Launcher's default folders."""
    out = {}
    for pat in [r"C:\Program Files\Epic Games\UE_*", "/Users/Shared/Epic Games/UE_*"]:
        for p in glob.glob(pat):
            m = re.search(r"UE_(\d+\.\d+)", p)
            if m:
                out[m.group(1)] = p
    return out


def find_godot() -> str | None:
    for env in ("GODOT", "GODOT_BIN"):
        if os.environ.get(env) and Path(os.environ[env]).exists():
            return os.environ[env]
    for name in ("godot", "godot4", "Godot", "godot-mono"):
        p = shutil.which(name)
        if p:
            return p
    pats = [r"C:\Program Files (x86)\Steam\steamapps\common\Godot Engine\godot*.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\GodotEngine*\Godot*.exe"),
            str(Path.home() / "scoop/apps/godot*/current/*.exe"),
            "/Applications/Godot*.app/Contents/MacOS/Godot"]
    for pat in pats:
        hits = sorted(glob.glob(pat))
        hits = [h for h in hits if "console" not in Path(h).name.lower()] or hits
        if hits:
            return hits[-1]
    return None


# name, finder (list of candidate executables), version args (None = don't run it)
TOOLS: list[tuple[str, list[str], list[str] | None]] = [
    ("git", ["git"], ["--version"]),
    ("git-lfs", ["git-lfs"], ["version"]),
    ("gh", ["gh"], ["--version"]),
    ("uv", ["uv"], ["--version"]),
    ("node", ["node"], ["--version"]),
    ("npm", ["npm"], ["--version"]),
    ("pnpm", ["pnpm"], ["--version"]),
    ("bun", ["bun"], ["--version"]),
    ("dotnet", ["dotnet"], ["--version"]),
    ("cargo", ["cargo"], ["--version"]),
    ("trunk", ["trunk"], ["--version"]),
    ("go", ["go"], ["version"]),
    ("java", ["java"], ["-version"]),
    ("cmake", ["cmake"], ["--version"]),
    ("emcc (Emscripten)", ["emcc"], None),
    ("love", ["love", "lovec"], ["--version"]),
    ("haxe", ["haxe"], ["--version"]),
    ("blender", ["blender"], None),
    ("ffmpeg", ["ffmpeg"], ["-version"]),
    ("butler (itch.io)", ["butler"], ["-V"]),
    ("steamcmd", ["steamcmd"], None),
    ("um (universal-modder)", ["um"], None),
    ("xvfb-run", ["xvfb-run"], None),
]


def tools_report() -> list[dict]:
    rows = []
    g = find_godot()
    rows.append(dict(name="godot", found=bool(g), path=g, version=version_of([g, "--version"]) if g else None))
    eds = unity_editors()
    rows.append(dict(name="unity editors (Hub)", found=bool(eds), path=", ".join(eds.values()) or None,
                     version=", ".join(sorted(eds)) or None))
    ues = unreal_installs()
    rows.append(dict(name="unreal engine", found=bool(ues), path=", ".join(ues.values()) or None, version=", ".join(sorted(ues)) or None))
    rows.append(dict(name="python (running ugd)", found=True, path=sys.executable, version=sys.version.split()[0]))
    for name, exes, vargs in TOOLS:
        path = next((shutil.which(e) for e in exes if shutil.which(e)), None)
        ver = version_of([path, *vargs]) if (path and vargs) else None
        if ver and "was not found" in ver:  # Windows Store aliases print this instead of running
            path, ver = None, None
        if name == "dotnet" and ver and not re.match(r"^\d", ver):
            ver = "runtime only? `dotnet --version` found no SDK"
        if name.startswith("um ") and not path and shutil.which("uvx"):
            ver = "not installed; bin/um runs a pinned copy through uvx"
        rows.append(dict(name=name, found=bool(path), path=path, version=ver))
    return rows


# --------------------------------------------------------------------------- scan

def scan(path: str = ".") -> dict:
    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        die(f"not a folder: {root}")
    ix = Index(root)
    hits: list[Hit] = []
    for d in DETECTORS:
        d(ix, hits)
    hits.sort(key=lambda h: -h.score)
    top = hits[0] if hits else None
    size = 0
    big = []
    for p in ix.files:
        try:
            s = p.stat().st_size
        except OSError:
            continue
        size += s
        if s > 50 << 20:
            big.append(f"{p.relative_to(root).as_posix()} ({s >> 20} MB)")
    ci = [r for r in ix.rel if r.startswith(".github/workflows/") and r.endswith((".yml", ".yaml"))]
    ci += [r for r in (".gitlab-ci.yml", "azure-pipelines.yml", "Jenkinsfile") if ix.has(r)]
    docs = {d: any(n.upper().startswith(d) for n in os.listdir(root)) for d in ("README", "LICENSE", "CREDITS")}
    docs.update({d: ix.has(d) for d in ("GAME_PLAN.md", "DEVLOG.md")})
    gitattr = ix.text(".gitattributes") if ix.has(".gitattributes") else ""
    rep = dict(
        path=str(root),
        name=(top.name if top and top.name else root.name),
        engine=None,
        also=[dict(key=h.key, name=ENGINES[h.key][0], version=h.version, score=h.score) for h in hits[1:6]],
        git=(root / ".git").exists(),
        lfs="filter=lfs" in gitattr,
        ci=ci,
        docs=docs,
        fal_manifests=len(ix.named("fal_manifest.jsonl")),
        files=len(ix.files),
        files_capped=len(ix.files) >= 20000,
        size_mb=round(size / 2**20, 1),
        big_files=big[:10],
    )
    if top:
        rep["engine"] = dict(key=top.key, name=ENGINES[top.key][0], version=top.version, language=top.language,
                             score=top.score, evidence=top.evidence, tests=top.tests, commands=top.commands,
                             notes=top.notes, platforms=top.platforms,
                             playbook=f"{PLAYBOOK_DIR}/{ENGINES[top.key][1]}")
    return rep


def format_report(r: dict) -> str:
    out = [f"Project: {r['name']}  ({r['path']})"]
    e = r["engine"]
    if not e:
        out.append("Engine:  none detected. A new project? The game-plan skill helps choose an engine.")
    else:
        out.append(f"Engine:  {e['name']}{' ' + e['version'] if e['version'] else ''}  [{e['key']}]  via {', '.join(e['evidence'])}")
        if r["also"]:
            out.append("   also: " + ", ".join(f"{a['name']}{' ' + a['version'] if a['version'] else ''}" for a in r["also"]))
        out.append(f"Language: {e['language'] or '?'}   Tests: {', '.join(e['tests']) or 'none found'}")
        if e["platforms"]:
            out.append(f"Export presets: {', '.join(e['platforms'])}")
    flags = [f"git{' + LFS' if r['lfs'] else ''}" if r["git"] else "no git",
             f"CI: {', '.join(r['ci'])}" if r["ci"] else "no CI"]
    out.append("Repo:    " + " | ".join(flags))
    out.append("Docs:    " + "  ".join(f"{k} {'yes' if v else 'no'}" for k, v in r["docs"].items()))
    out.append(f"Files:   {r['files']}{'+' if r['files_capped'] else ''} files, {r['size_mb']} MB"
               + (f", {r['fal_manifests']} fal_manifest.jsonl" if r["fal_manifests"] else ""))
    for b in r["big_files"]:
        out.append(f"   big: {b}")
    if e and e["commands"]:
        out.append("Commands (suggestions; check the playbook):")
        for k, v in e["commands"].items():
            for cmd in v if isinstance(v, list) else [v]:
                out.append(f"  {k + ':':9} {cmd}")
    if e:
        for n in e["notes"]:
            out.append(f"Note:    {n}")
        out.append(f"Playbook: {e['playbook']}")
    return "\n".join(out)


def main(a):
    if a.tools:
        rows = tools_report()
        if a.json:
            print(json.dumps(rows, indent=2))
            return
        for t in rows:
            mark = "yes" if t["found"] else " - "
            detail = (t["version"] or "") + (f"   {t['path']}" if t["path"] and t["found"] else "")
            detail = detail if (t["found"] or t["version"]) else ""
            print(f"{mark}  {t['name']:24} {detail}".rstrip())
        return
    rep = scan(a.path)
    print(json.dumps(rep, indent=2) if a.json else format_report(rep))


def register(sub):
    import argparse
    p = sub.add_parser("scan", help="fingerprint a game project, or list installed engines and tools",
                       description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--tools", action="store_true", help="list installed engines, SDKs and tools instead")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=main)
