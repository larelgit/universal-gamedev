# Unreal Engine 5

**Pick it when** the game is high-end 3D (Nanite, Lumen, MetaHumans), the team already uses Unreal, or
designers want Blueprints. **Think twice** for 2D (Paper2D is minimal), for web (no web export), for small
machines, and for agent-only iteration: C++ compile times, binary `.uasset` files and a 50-100+ GB install
all slow an agent down.

Versions (October 2026): UE 5.8 is the latest (5.8.3 hotfix). Royalty: 5% of lifetime gross above $1M per
product. Revenue through the Epic Games Store is exempt, and the "Launch Everywhere with Epic" program lowers
the rate to 3.5%. Check current terms for commercial releases.

## Identify
- `<Project>.uproject` (JSON): `"EngineAssociation": "5.8"` (launcher build) or a GUID (source build); its
  `Modules` list means C++.
- `Source/` (C++), `Content/` (`.uasset`/`.umap`, binary), `Config/` (`Default*.ini`, text).

## Setup
- **Install** through the Epic Games Launcher (the user signs in), or build from source on GitHub (the user
  must link their Epic and GitHub accounts). For C++ on Windows, install Visual Studio 2022 with the "Game
  development with C++" workload, or Rider.
- **Git:** ignore `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, `.vs/` and the generated
  `*.sln`. Put `Content/**` (`*.uasset`, `*.umap`) in Git LFS. Large teams often use Perforce instead.

## Agent workflow
- **C++ for systems** (classes with `UCLASS`/`UPROPERTY`/`UFUNCTION`): it's text, diffable and reviewable.
  Blueprints are binary, so an agent can't diff or merge them. A good split: C++ base classes hold the logic,
  thin Blueprint subclasses only assign assets and tuning, and Data Assets or Data Tables (importable from
  CSV/JSON) hold the numbers.
- **Editor automation:** with the Python Editor Script Plugin enabled, the `unreal` module creates assets,
  imports files, places actors and sets properties. Run a script with
  `UnrealEditor-Cmd.exe <Project>.uproject -run=pythonscript -script="tools/build_level.py"`.
- **Live control:** the Remote Control API plugin exposes objects, properties and functions over
  HTTP/WebSocket on localhost.
- **MCP:** UE 5.8 ships an official, experimental Unreal MCP plugin (it serves `http://127.0.0.1:8000/mcp`
  once enabled). UE 5.7 added an experimental in-editor AI Assistant. The older community unreal-mcp
  projects are mostly stale.
- **Config is text:** `DefaultEngine.ini`, `DefaultGame.ini` and `DefaultInput.ini`, under `Config/`.
- **Iteration:** Live Coding (Ctrl+Alt+F11) handles function-body changes. Header and reflection changes
  need an editor restart; avoid the old Hot Reload, which corrupts Blueprints.

## Commands
`<UE>` is the engine root, e.g. `C:\Program Files\Epic Games\UE_5.8`.
```bash
"<UE>\Engine\Build\BatchFiles\Build.bat" <Project>Editor Win64 Development -Project="<path>\<Project>.uproject" -WaitMutex
"<UE>\Engine\Binaries\Win64\UnrealEditor.exe" "<path>\<Project>.uproject" -game -windowed -ResX=1280 -ResY=720
"<UE>\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "<path>\<Project>.uproject" -ExecCmds="Automation RunTests <Project>.;Quit" -unattended -nopause -nullrhi -nosplash -log -ReportExportPath="<dir>\TestReport"
"<UE>\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun -project="<path>\<Project>.uproject" -noP4 -platform=Win64 -clientconfig=Shipping -build -cook -stage -pak -archive -archivedirectory="<dir>\Build"
```
- The first command builds the editor target for a C++ project. The second runs the game uncooked, in a
  window.
- The third runs automation tests headless (`-nullrhi` means no GPU). Epic's 5.8 page writes the command as
  `Automation RunTest`. If a filter runs zero tests, check the log for how the command was parsed.
- The fourth packages a Shipping build. Shipping strips console commands and cheats.
- Logs: `Saved/Logs/<Project>.log`.

## Debug hooks and oracles
- **Tests:** the Automation framework. Simple and spec tests in C++ (`IMPLEMENT_SIMPLE_AUTOMATION_TEST`,
  `BEGIN_DEFINE_SPEC`), functional tests (`AFunctionalTest` actors placed in test maps, with screenshot
  comparison), and Gauntlet for whole-game sessions.
- **Cheats and console:** a `UCheatManager` subclass (stripped from Shipping), `UFUNCTION(Exec)` commands,
  `-ExecCmds="..."` at launch, and your own arguments via `FParse::Value(FCommandLine::Get(), ...)`.
- **Seeing state:** `stat fps`, `stat unit`, `stat gpu`, `showdebug`, the Gameplay Debugger (apostrophe
  key), the Visual Logger, and `UE_LOG` categories.
- **Screenshots:** `HighResShot 1920x1080` saves to `Saved/Screenshots/<Platform>/`. Use the Movie Render
  Queue or Movie Render Graph for cinematic captures.
- **Input injection:** Enhanced Input's `InjectInputForAction` on the local player subsystem.

## Pitfalls
- **Garbage collection:** raw `UObject*` members that aren't `UPROPERTY` (or `TObjectPtr`) get collected
  under you.
- **Renames break Blueprint references.** Add Core Redirects in `DefaultEngine.ini` when renaming classes or
  properties.
- **Cook and shader times are long.** Cook only the maps you need (`-map=`), and keep the Derived Data Cache
  warm.
- **Build errors hide in logs.** Read `Saved/Logs/` and the UBT output, not just the exit code.
- **Dedicated servers** need an engine built from source.
