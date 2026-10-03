# Godot 4

**Pick it when** you want 2D, or stylised 3D, for desktop, web and mobile, and the agent writes most of the
code. Scenes and resources are text, the editor is a ~100 MB download, everything runs from the command line,
and it's MIT-licensed. **Think twice** for photoreal 3D (Unreal), for C# projects that must export to the
web (the .NET build can't), and for consoles (they go through porting partners).

Versions: 4.7.x was the latest stable in October 2026. Check https://godotengine.org/download for the
current release, and use the **exact same version** in every session and in CI.

## Identify
- `project.godot` at the root. `config/features=PackedStringArray("4.7", "Forward Plus")` holds the major
  and minor version, and `config_version=5` means Godot 4 (`4` means Godot 3).
- `.tscn` (scenes), `.tres` (resources), `.gd` (GDScript). A `.csproj` using `Godot.NET.Sdk` means C#.
- `export_presets.cfg` lists the export targets (preset names and output paths).

## Setup
- **Install:** the official download (standard or .NET build) is a single executable. Put it on PATH as
  `godot`, or set `GODOT` / `GODOT_BIN` to its path (`ugd scan --tools` finds common install places).
- **Export templates** (needed to export) match the engine version exactly: Editor → Manage Export Templates,
  or extract the `.tpz` into `%APPDATA%\Godot\export_templates\<version>\` (Windows),
  `~/.local/share/godot/export_templates/<version>/` (Linux) or
  `~/Library/Application Support/Godot/export_templates/<version>/` (macOS).
- **New project from text:** a minimal `project.godot` is enough:
  ```ini
  config_version=5

  [application]
  config/name="Beacon"
  run/main_scene="res://scenes/main.tscn"
  config/features=PackedStringArray("4.7", "Forward Plus")
  ```
- **Git:** ignore `.godot/` (the import cache). **Commit** the `*.import` sidecar files and the `*.uid`
  files (Godot 4.4+ writes one next to each script and shader). Use LFS for large binaries.

## Agent workflow
- **GDScript with static types** (`var speed: float = 200.0`, `func hit(amount: int) -> void:`) catches
  mistakes at parse time. Turn on the untyped-declaration warnings in Project Settings → Debug → GDScript.
- **Scenes as text:** `.tscn` is editable, but every `ext_resource` and sub-resource has an id, and nodes
  reference parents by path. For anything bigger than a property tweak, either build the node tree in code
  (`_ready()` adding children), or write a small `@tool` / `EditorScript` that creates the scene. Validate
  hand edits by loading the project headless.
- **Data:** custom `Resource` classes (`class_name EnemyData extends Resource` with `@export` fields), saved as
  `.tres`. They're text, typed and inspector-friendly. Remember that resources are shared: call
  `duplicate()` (or set `resource_local_to_scene`) before mutating per-instance data.
- **Globals:** autoloads (`[autoload] Game="*res://autoload/game.gd"` in `project.godot`).
- **Scene-unique nodes** (`%Player`) survive restructuring better than `$"../../Player"` paths.
- **MCP:** community Godot MCP servers (e.g. Coding-Solo/godot-mcp) can launch the editor, run the project
  and capture output. There was no official one as of October 2026.

## Commands
```bash
godot --path .                                     # run the main scene (add res://scenes/x.tscn to run another)
godot --path . res://scenes/test_arena.tscn -- --seed 7     # a specific scene; args after -- are yours
godot --headless --path . --import                 # (re)import assets and rebuild the class cache, then quit (4.2.2+/4.3+)
godot --headless --path . --check-only -s res://src/player.gd   # parse one script and report errors
godot --headless --path . --quit-after 600 -- --autotest smoke  # run 600 iterations with no window
godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit       # GUT tests (exit code 0/1)
addons/gdUnit4/runtest.sh -a res://test           # gdUnit4 (runtest.cmd on Windows; set GODOT_BIN); exit 0, 100 failures, 101 warnings
godot --headless --path . --export-release "Windows Desktop" build/windows/Beacon.exe   # preset name from export_presets.cfg
godot --headless --path . --export-release "Web" build/web/index.html
godot --path . --write-movie captures/take.avi --fixed-fps 60 -- --trailer   # Movie Maker: deterministic capture
```
- `--headless` uses the dummy display and audio drivers: there's **no rendering**, so viewport screenshots
  come back empty. For screenshots, run with a display (Windows/macOS desktop) or under `xvfb-run` on Linux.
- Read your own arguments with `OS.get_cmdline_user_args()`. End test runs with `get_tree().quit(code)`.
- **After adding `class_name` scripts or assets from outside the editor, run `--import` first.** Headless
  game runs don't rescan the file system, so new global classes fail with "identifier not declared" until the
  class cache in `.godot/` is rebuilt. (`--export-*` imports automatically.)

## Debug hooks and oracles
- **Dev-only code:** `if OS.is_debug_build():`, or custom feature tags (`OS.has_feature("dev")`) set per
  export preset, so release builds drop the console and bridge.
- **Screenshot:**
  ```gdscript
  await RenderingServer.frame_post_draw
  get_viewport().get_texture().get_image().save_png("user://shots/frame.png")
  ```
- **Logs:** `print`, `push_warning` and `push_error` go to stdout and to `user://logs/godot.log`. Fail the run on
  any `ERROR:` line.
- **Performance:** `Performance.get_monitor(Performance.TIME_PROCESS)` and
  `Engine.get_frames_per_second()`; the Profiler and Monitors tabs in the editor's debugger.
- **Agent bridge:** an autoload with `TCPServer.listen(port, "127.0.0.1")`, polled in `_process`, reading and
  answering JSON lines (see `skills/playtest-automation/references/per-engine.md`).
- **Input injection:** `Input.action_press("jump")` / `Input.action_release("jump")`, or
  `Input.parse_input_event()` with an `InputEventAction`.
- **Tests:** GUT 9.x or gdUnit4 6.x in `addons/`, with the plugin enabled in `project.godot`
  (`[editor_plugins] enabled=PackedStringArray("res://addons/gut/plugin.cfg")`).

## Export notes
- **Web:** since 4.3, single-threaded export ("Thread Support" off) is the default and needs no COOP/COEP
  headers. Turn threads on only if you need them, and then serve the headers. C# projects can't export to
  the web.
- **Dedicated servers:** the "Dedicated Server" export mode strips visuals and audio from resources.
- **Android/iOS:** Android needs the Android SDK and JDK configured in Editor Settings, plus a keystore the
  user keeps safe. iOS exports an Xcode project.

## Pitfalls
- **Version upgrades** convert resources. Commit before opening the project in a newer version, and never
  let two versions edit the same project.
- **Moving files outside the editor** breaks UID and path references. Move them in the editor, or move each
  file together with its `.uid` and `.import` files and re-import.
- **Physics in `_process`:** movement and physics belong in `_physics_process` (60 Hz by default). Use
  `move_and_slide()` with `CharacterBody2D/3D` for characters.
- **Shared resources:** editing one enemy's `Resource` at runtime changes them all, unless it was duplicated.
- **Pixel art** needs the Nearest default texture filter and an integer stretch scale
  (`skills/game-assets/references/engine-import.md`).
- **Web:** audio starts only after a user gesture, and `user://` is IndexedDB.
