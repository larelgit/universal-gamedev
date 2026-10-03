"""Tests for the ugd CLI and the repo's own content. Run: uv run --with pytest pytest -q tests"""
import json
import re
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ugd import cli, kb, release, scan, shot  # noqa: E402


def write(p: Path, text: str = "") -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def fake(prefix: str, n: int = 40) -> str:
    """A key-shaped string built at runtime, so this file never contains one."""
    return prefix + "a" * n


# --------------------------------------------------------------------------- scan

def test_scan_godot(tmp_path):
    write(tmp_path / "project.godot", 'config_version=5\n\n[application]\nconfig/name="Beacon"\n'
                                      'config/features=PackedStringArray("4.7", "Forward Plus")\n')
    write(tmp_path / "src/player.gd", "extends CharacterBody2D\n")
    write(tmp_path / "addons/gut/plugin.cfg")
    write(tmp_path / "test/test_player.gd", "extends GutTest\n")
    write(tmp_path / "export_presets.cfg",
          '[preset.0]\n\nname="Windows Desktop"\nplatform="Windows Desktop"\nexport_path="build/windows/Beacon.exe"\n\n'
          '[preset.0.options]\n\napplication/product_name="Beacon"\n\n'
          '[preset.1]\n\nname="Web"\nplatform="Web"\nexport_path="build/web/index.html"\n')
    r = scan.scan(str(tmp_path))
    e = r["engine"]
    assert (e["key"], e["version"], e["language"]) == ("godot", "4.7", "GDScript")
    assert r["name"] == "Beacon"
    assert any("gut_cmdln.gd -gdir=res://test -gexit" in c for c in e["commands"]["test"])
    assert any('--export-release "Web" build/web/index.html' in c for c in e["commands"]["export"])
    assert e["platforms"] == ["Windows Desktop", "Web"]
    assert e["playbook"] == "skills/make-any-game/references/engines/godot.md"
    assert (ROOT / e["playbook"]).exists()


def test_scan_godot_csharp_is_not_also_dotnet(tmp_path):
    write(tmp_path / "project.godot", 'config_version=5\nconfig/features=PackedStringArray("4.7")\n')
    write(tmp_path / "Beacon.csproj", '<Project Sdk="Godot.NET.Sdk/4.7.2"></Project>')
    write(tmp_path / "Player.cs", "")
    r = scan.scan(str(tmp_path))
    assert r["engine"]["key"] == "godot" and r["engine"]["language"] == "C#"
    assert r["also"] == []
    assert any("can't export to Web" in n for n in r["engine"]["notes"])


def test_scan_unity(tmp_path):
    write(tmp_path / "ProjectSettings/ProjectVersion.txt", "m_EditorVersion: 6000.3.2f1\n")
    write(tmp_path / "Packages/manifest.json", json.dumps({"dependencies": {
        "com.unity.render-pipelines.universal": "17.3.0", "com.unity.test-framework": "1.5.1"}}))
    write(tmp_path / "Assembly-CSharp.csproj", '<Project><ItemGroup><Reference Include="UnityEngine" /></ItemGroup></Project>')
    r = scan.scan(str(tmp_path))
    e = r["engine"]
    assert (e["key"], e["version"]) == ("unity", "6000.3.2f1")
    assert "render pipeline: URP" in e["notes"]
    assert any("-runTests -testPlatform EditMode" in c for c in e["commands"]["test"])
    assert r["also"] == []


def test_scan_unreal(tmp_path):
    write(tmp_path / "Beacon.uproject", json.dumps({"FileVersion": 3, "EngineAssociation": "5.8",
                                                     "Modules": [{"Name": "Beacon", "Type": "Runtime"}]}))
    e = scan.scan(str(tmp_path))["engine"]
    assert (e["key"], e["version"]) == ("unreal", "5.8") and e["language"].startswith("C++")
    assert 'Automation RunTests Beacon.;Quit' in e["commands"]["test"][0]
    assert "BuildCookRun" in e["commands"]["export"][0]


def test_scan_web_phaser(tmp_path):
    write(tmp_path / "package.json", json.dumps({
        "name": "beacon", "scripts": {"dev": "vite", "build": "vite build", "test": "vitest run"},
        "dependencies": {"phaser": "^4.2.1"},
        "devDependencies": {"vite": "^7.0.0", "typescript": "^5.9.0", "@playwright/test": "^1.63.0", "vitest": "^3.2.0"}}))
    write(tmp_path / "tsconfig.json", "{}")
    write(tmp_path / "pnpm-lock.yaml")
    e = scan.scan(str(tmp_path))["engine"]
    assert (e["key"], e["version"], e["language"]) == ("phaser", "4.2.1", "TypeScript")
    assert e["commands"]["run"] == "pnpm run dev" and e["commands"]["export"] == ["pnpm run build"]
    assert "pnpm test" in e["commands"]["test"] and "npx playwright test" in e["commands"]["test"]
    assert any("base: './'" in n for n in e["notes"])


def test_scan_bevy(tmp_path):
    write(tmp_path / "Cargo.toml", '[package]\nname = "beacon"\n\n[dependencies]\n'
                                   'bevy = { version = "0.19.1", features = ["dynamic_linking"] }\n')
    e = scan.scan(str(tmp_path))["engine"]
    assert (e["key"], e["version"]) == ("bevy", "0.19.1")
    assert e["commands"]["test"] == ["cargo test"]
    assert any("dynamic_linking" in n for n in e["notes"])


def test_scan_love(tmp_path):
    write(tmp_path / "main.lua", "function love.load() end\nfunction love.draw() end\n")
    write(tmp_path / "conf.lua", 'function love.conf(t) t.version = "11.5" end\n')
    write(tmp_path / "spec/sim_spec.lua")
    e = scan.scan(str(tmp_path))["engine"]
    assert (e["key"], e["version"]) == ("love2d", "11.5")
    assert e["commands"]["test"] == ["busted spec/"]


def test_scan_pygame(tmp_path):
    write(tmp_path / "main.py", "import pygame\n")
    write(tmp_path / "beacon/render.py", "import pygame\n")
    write(tmp_path / "tests/test_sim.py", "def test_x():\n    pass\n")
    write(tmp_path / "pyproject.toml", '[project]\nname = "beacon"\ndependencies = ["pygame-ce>=2.5.8"]\n\n[tool.uv]\npackage = false\n')
    e = scan.scan(str(tmp_path))["engine"]
    assert (e["key"], e["version"]) == ("pygame", "2.5.8")
    assert e["commands"]["run"] == "uv run python main.py"
    assert e["commands"]["test"][0].startswith("SDL_VIDEODRIVER=dummy")


def test_scan_monogame(tmp_path):
    write(tmp_path / "Beacon/Beacon.csproj", '<Project Sdk="Microsoft.NET.Sdk"><ItemGroup>'
          '<PackageReference Include="MonoGame.Framework.DesktopGL" Version="3.8.5.1" /></ItemGroup></Project>')
    write(tmp_path / "Beacon.Tests/Beacon.Tests.csproj", '<Project><ItemGroup><PackageReference Include="Microsoft.NET.Test.Sdk" '
          'Version="17.14.0" /><PackageReference Include="xunit" Version="2.9.3" /></ItemGroup></Project>')
    e = scan.scan(str(tmp_path))["engine"]
    assert (e["key"], e["version"]) == ("monogame", "3.8.5.1")
    assert e["commands"]["test"] == ["dotnet test"] and e["tests"]


def test_scan_raylib(tmp_path):
    write(tmp_path / "CMakeLists.txt", "FetchContent_Declare(raylib GIT_REPOSITORY https://github.com/raysan5/raylib.git "
                                       "GIT_TAG 6.0)\nenable_testing()\nadd_test(NAME sim COMMAND sim_tests)\n")
    write(tmp_path / "src/main.c", '#include "raylib.h"\n')
    e = scan.scan(str(tmp_path))["engine"]
    assert (e["key"], e["version"]) == ("raylib", "6.0")
    assert e["commands"]["test"] == ["ctest --test-dir build --output-on-failure"]


def test_scan_marker_engines(tmp_path):
    vn = tmp_path / "vn"
    write(vn / "game/script.rpy", "label start:\n    'Hello.'\n")
    assert scan.scan(str(vn))["engine"]["key"] == "renpy"
    gm = tmp_path / "gm"
    write(gm / "Beacon.yyp", '{"resourceType":"GMProject","MetaData":{"IDEVersion":"2024.8.1.171",},}')
    e = scan.scan(str(gm))["engine"]
    assert (e["key"], e["version"]) == ("gamemaker", "2024.8.1.171")
    rb = tmp_path / "rb"
    write(rb / "default.project.json", '{"name": "beacon", "tree": {}}')
    assert scan.scan(str(rb))["engine"]["key"] == "roblox"


def test_scan_empty_folder(tmp_path):
    r = scan.scan(str(tmp_path))
    assert r["engine"] is None
    assert "none detected" in scan.format_report(r)


def test_every_engine_has_a_playbook():
    for key, (_, playbook) in scan.ENGINES.items():
        assert (ROOT / scan.PLAYBOOK_DIR / playbook).exists(), key


def test_tools_report_runs():
    names = {row["name"] for row in scan.tools_report()}
    assert {"godot", "git", "python (running ugd)", "um (universal-modder)"} <= names


def test_cli_output_survives_a_non_utf8_pipe(tmp_path):
    """Regression: on Windows a piped stdout is cp1252 and used to crash on "→" (Godot's export-preset note)."""
    import os
    import subprocess
    write(tmp_path / "project.godot", 'config_version=5\nconfig/features=PackedStringArray("4.7")\n')
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
    env["PYTHONIOENCODING"] = "cp1252"   # what a Windows pipe gets by default
    r = subprocess.run([sys.executable, "-m", "ugd", "scan", str(tmp_path)], cwd=ROOT, env=env,
                       capture_output=True, timeout=120)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    assert "Project → Export" in r.stdout.decode("utf-8")


def test_cli_scan_json(tmp_path, capsys):
    write(tmp_path / "main.lua", "function love.draw() end\n")
    cli.main(["scan", str(tmp_path), "--json"])
    assert json.loads(capsys.readouterr().out)["engine"]["key"] == "love2d"


# --------------------------------------------------------------------------- release

def test_release_clean_project_passes(tmp_path, capsys):
    for n in ("README.md", "LICENSE", "CREDITS.md"):
        write(tmp_path / n, "Beacon. Made with Godot Engine (MIT).")
    write(tmp_path / "project.godot")
    assert release.check(str(tmp_path)) == 0
    assert "PASS: project" in capsys.readouterr().out


def test_release_catches_secrets_and_signing_material(tmp_path, capsys):
    write(tmp_path / "README.md", "x")
    write(tmp_path / "src/config.ts", f'export const key = "{fake("sk-ant-")}";\n')
    write(tmp_path / "tools/upload.sh", f"export GH={fake('ghp_')}\n")
    write(tmp_path / ".env", "FAL_KEY=short\n")
    write(tmp_path / ".env.example", "FAL_KEY=\n")
    (tmp_path / "android").mkdir()
    (tmp_path / "android/release.keystore").write_bytes(b"\x00\x01")
    assert release.check(str(tmp_path)) == 1
    out = capsys.readouterr().out
    assert "Anthropic key in src/config.ts" in out and "GitHub token in tools/upload.sh" in out
    assert "env file (secrets?): .env" in out and "Android keystore: android/release.keystore" in out
    assert ".env.example" not in out


def test_release_build_mode(tmp_path, capsys):
    write(tmp_path / "index.html", '<script src="/assets/main.js"></script>\n')
    write(tmp_path / "steam_appid.txt", "480\n")
    assert release.check(str(tmp_path)) == 1
    out = capsys.readouterr().out
    assert "build," in out and "FAIL  steam_appid.txt" in out and "root-absolute path in index.html" in out
    assert "no README" not in out  # docs checks are for projects


def test_release_credit_warnings(tmp_path, capsys):
    write(tmp_path / "README.md", "Beacon")
    write(tmp_path / "LICENSE", "MIT")
    write(tmp_path / "CREDITS.md", "Art by me")
    write(tmp_path / "project.godot")
    write(tmp_path / "assets/gen/fal_manifest.jsonl", "{}\n")
    write(tmp_path / "src/paths.gd", 'var p = "C:\\Users\\bob\\Desktop\\x.png"\n')
    assert release.check(str(tmp_path)) == 0
    out = capsys.readouterr().out
    assert "Godot project without" in out and "no fal credit" in out and "disclose AI content" in out
    assert "absolute user path in src/paths.gd" in out


def test_release_case_collision(tmp_path, capsys):
    write(tmp_path / "assets/Player.png", "a")
    if (tmp_path / "assets/player.png").exists():
        pytest.skip("case-insensitive file system")
    write(tmp_path / "assets/player.png", "b")
    release.check(str(tmp_path))
    assert "differ only by case" in capsys.readouterr().out


# --------------------------------------------------------------------------- shot

def test_shot_diff(tmp_path):
    from PIL import Image
    a = Image.new("RGB", (20, 10), (10, 20, 30))
    a.save(tmp_path / "golden.png")
    a.save(tmp_path / "same.png")
    res = shot.diff(tmp_path / "golden.png", tmp_path / "same.png")
    assert res["passed"] and res["changed"] == 0
    b = a.copy()
    b.putpixel((3, 3), (200, 20, 30))
    b.save(tmp_path / "one.png")
    res = shot.diff(tmp_path / "golden.png", tmp_path / "one.png", max_ratio=0.0, out=tmp_path / "diff.png")
    assert not res["passed"] and res["changed"] == 1 and (tmp_path / "diff.png").exists()
    assert Image.open(tmp_path / "diff.png").getpixel((3, 3))[0] > 200          # the changed pixel is red
    assert shot.diff(tmp_path / "golden.png", tmp_path / "one.png", max_ratio=0.01)["passed"]         # 1/200 = 0.5%
    assert shot.diff(tmp_path / "golden.png", tmp_path / "one.png", threshold=250, max_ratio=0)["passed"]
    Image.new("RGB", (21, 10)).save(tmp_path / "wider.png")
    assert not shot.diff(tmp_path / "golden.png", tmp_path / "wider.png")["passed"]


def test_shot_cli_update_then_compare(tmp_path, capsys):
    from PIL import Image
    Image.new("RGB", (8, 8), (1, 2, 3)).save(tmp_path / "actual.png")
    golden = tmp_path / "golden/arena.png"
    cli.main(["shot", "diff", str(golden), str(tmp_path / "actual.png"), "--update"])
    assert golden.exists()
    with pytest.raises(SystemExit) as e:
        cli.main(["shot", "diff", str(golden), str(tmp_path / "actual.png")])
    assert e.value.code == 0 and "PASS" in capsys.readouterr().out


# --------------------------------------------------------------------------- kb

def kb_root(tmp_path: Path) -> Path:
    root = tmp_path / "knowledge"
    write(root / "TEMPLATE.md", (ROOT / "knowledge/TEMPLATE.md").read_text(encoding="utf-8"))
    return root


def test_kb_project_note_lifecycle(tmp_path):
    root = kb_root(tmp_path)
    p = kb.new_note(root, "Pooling 1000 enemies in Godot", game="Beacon", genre="survivors-like", engine="godot",
                    agent="Claude Code (Opus 5.5)")
    assert p == root / "projects/godot/pooling-1000-enemies-in-godot.md"
    fails, _ = kb.check_note(p)
    assert any("unfilled template text" in f for f in fails)   # a scaffold isn't done until it's filled in
    text = p.read_text(encoding="utf-8")
    text = text.replace("FILL IN: exact version", "Godot 4.7.2 stable")
    text = text.replace("> Two to four sentences: what you built", "> We built")
    text = text.replace("The most valuable section. Numbered; each one symptom → cause → fix.\n", "")
    text = text.replace("1. **Symptom.** What you saw. **Cause:** what it really was. **Fix:** what worked.",
                        "1. **Enemies stuttered.** **Cause:** per-frame allocations. **Fix:** a pool.")
    p.write_text(text, encoding="utf-8")
    fails, _ = kb.check_note(p)
    assert fails == []
    assert kb.write_index(root) == 1
    assert "Pooling 1000 enemies in Godot" in (root / "INDEX.md").read_text(encoding="utf-8")
    res = kb.search(root, ["pooling"])
    assert res and res[0]["path"] == "projects/godot/pooling-1000-enemies-in-godot.md"
    assert kb.search(root, ["pooling"], engine="unity") == []


def test_kb_check_rejects_bad_notes(tmp_path):
    root = kb_root(tmp_path)
    bad = write(root / "projects/godot/bad.md", "---\nkind: project\ntitle: x\nstatus: shipped\n---\n# x\n"
                f"Key: {fake('sk-ant-')}\n")
    fails, _ = kb.check_note(bad)
    joined = " | ".join(fails)
    assert "missing front-matter key: engine" in joined and "status 'shipped'" in joined
    assert "missing section: ## Gotchas" in joined and "Anthropic key" in joined


def test_kb_repo_default_and_override(monkeypatch):
    monkeypatch.delenv("UGD_KB_REPO", raising=False)
    assert kb.repo_slug() == "larelgit/universal-gamedev"
    monkeypatch.setenv("UGD_KB_REPO", "someone/their-fork")
    assert kb.repo_slug() == "someone/their-fork"


def test_kb_technique_and_stale_index(tmp_path):
    root = kb_root(tmp_path)
    p = kb.new_note(root, "Golden images in CI", kind="technique", agent="Codex (gpt-6)")
    assert p.parent.name == "techniques"
    meta, _ = kb.parse(p)
    assert meta["kind"] == "technique" and "engine" not in meta
    assert any("tags" in f for f in kb.check_note(p)[0])
    p.write_text(p.read_text(encoding="utf-8").replace("tags: []", "tags: [testing, screenshots]"), encoding="utf-8")
    assert kb.check_note(p)[0] == []
    with pytest.raises(SystemExit) as e:
        cli.main(["kb", "check", "--index", "--root", str(root)])
    assert e.value.code == 1                 # INDEX.md missing
    kb.write_index(root)
    with pytest.raises(SystemExit) as e:
        cli.main(["kb", "check", "--index", "--root", str(root)])
    assert e.value.code == 0


# --------------------------------------------------------------------------- the repo itself

def test_repo_knowledge_base_is_valid_and_indexed():
    root = ROOT / "knowledge"
    for p, _, _ in kb.notes(root):
        assert kb.check_note(p)[0] == [], p
    idx, _ = kb.build_index(root)
    assert (root / "INDEX.md").read_text(encoding="utf-8").replace("\r\n", "\n") == idx


SKILLS = sorted((ROOT / "skills").glob("*/SKILL.md"))


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.parent.name)
def test_skill_frontmatter(skill):
    text = skill.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "no front matter"
    meta = yaml.safe_load(m.group(1))
    assert meta["name"] == skill.parent.name
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", meta["name"]) and len(meta["name"]) <= 64
    assert 100 < len(meta["description"]) <= 1024, len(meta["description"])
    assert len(text.splitlines()) < 500


MD_FILES = sorted([*ROOT.glob("*.md"), *(ROOT / "skills").rglob("*.md"), *(ROOT / "knowledge").glob("*.md")])


@pytest.mark.parametrize("md", MD_FILES, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_references_resolve(md):
    """Every references/*.md or engines/*.md path a doc mentions exists."""
    text = md.read_text(encoding="utf-8")
    skill_dir = next((p for p in md.parents if p.parent.name == "skills"), None)
    for ref in set(re.findall(r"(?<![\w/.-])((?:[\w-]+/)*references/[\w/.-]+\.md)", text)):
        bases = [ROOT, ROOT / "skills"] + ([skill_dir] if skill_dir else [])
        assert any((b / ref).exists() for b in bases), f"{ref} in {md.relative_to(ROOT)}"
    for m in re.finditer(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)", text):   # relative Markdown links
        target = m.group(1)
        if not target.startswith("http"):
            assert (md.parent / target).exists(), f"{target} in {md.relative_to(ROOT)}"


UGD_COMMANDS = {"scan": None, "kb": {"search", "show", "new", "check", "index", "sync", "pr"}, "release": {"check"},
                "shot": {"diff"}}
# universal-modder's `um` at the pinned commit (bin/um): groups and their commands, checked against its --help
UM_COMMANDS = {
    "scan": None, "render3d": None, "publish": {"check"},
    "fal": {"sprite", "image", "edit", "rmbg", "pixelate", "upscale", "texture", "pbr", "model3d", "rig", "sfx", "music",
            "voice", "video", "run", "search", "schema", "price", "result", "upload"},
    "sprite": {"info", "cutout", "fit", "pixelate", "palette", "sheet", "slice", "frames", "team-mask", "seamless",
               "tile-preview", "preview", "outline", "hard-alpha", "flip", "rotate"},
    "video": {"probe", "contact", "first-frame", "beats", "mux", "compile"},
    "win": {"setup", "ps", "kill", "launch", "shot", "drive", "record", "reg"},
    "backup": {"create", "list", "diff", "restore"},
    "kb": {"search", "show", "new", "check", "index", "sync", "pr"},
}


@pytest.mark.parametrize("md", MD_FILES, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_cited_cli_commands_exist(md):
    text = md.read_text(encoding="utf-8")
    for tool, table in (("ugd", UGD_COMMANDS), ("um", UM_COMMANDS)):
        for m in re.finditer(rf"(?<![\w/.\\-]){tool} ([a-z0-9-]+)(?: ([a-z0-9-]+))?", text):
            group, cmd = m.group(1), m.group(2)
            if group in ("is", "and", "or", "the", "from", "in", "for", "on", "to", "with", "reuses", "lives", "comes",
                         "runs", "kb's", "win's", "a", "it", "at", "also", "cli", "does"):
                continue  # prose ("`um` comes from universal-modder", ...)
            assert group in table, f"{tool} {group} in {md.relative_to(ROOT)}"
            cmds = table[group]
            if cmds and cmd and not cmd.startswith("-") and cmd not in cmds:
                # the word after a group may be an argument; flag only near-misses of real commands (typos)
                near = [c for c in cmds if c[:3] == cmd[:3]]
                assert not near, f"{tool} {group} {cmd} in {md.relative_to(ROOT)}: did you mean {near}?"


@pytest.mark.parametrize("group", ["scan", "kb", "release", "shot"])
def test_group_help(group):
    with pytest.raises(SystemExit) as e:
        cli.main([group, "--help"])
    assert e.value.code == 0
