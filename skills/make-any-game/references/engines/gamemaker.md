# GameMaker

**Pick it when** the user already knows GameMaker and GML, or wants its fast 2D workflow and huge tutorial
base. **Think twice** for agent-led development: the IDE creates and registers resources, there's no
built-in test framework or headless mode, and 3D is minimal.

Licensing (October 2026): free for non-commercial use; a one-time Professional license (~$99.99) for
commercial desktop, web and mobile releases; an Enterprise subscription for consoles. Check current terms.

## Identify
- A `.yyp` project file: JSON-like text whose metadata holds `"IDEVersion"`.
- Per-resource folders with `.yy` files (`objects/`, `sprites/`, `rooms/`, `scripts/`).
- Object events are separate GML files: `objects/obj_player/Create_0.gml`, `Step_0.gml`, `Draw_0.gml`.

## Agent workflow
- **Edit GML freely:** scripts and object event files are plain text, and that's where the agent adds the
  most value.
- **Let the IDE create resources.** New objects, sprites and rooms must be registered in the `.yyp`, with
  consistent `.yy` files and UUID-like references. Hand-made resources are easy to corrupt. Ask the human to
  create the resource in the IDE (or duplicate an existing one there), then fill in its code. If you must
  create one by hand, copy the structure of a working sibling exactly and reopen the project to confirm.
- **Data:** structs and arrays in GML scripts, or JSON files in Included Files read with
  `json_parse(buffer_read(...))`. Both are text and agent-friendly.
- **Version control:** the 2023+ project format is diff-friendly. Commit everything except the
  cache/output folders, and keep the IDE and runtime versions in `DEVLOG.md`.

## Commands
- **Building from the command line uses Igor** (documented in the manual under "Building via Command Line").
  It needs a licence file from an earlier IDE login (`/lf=` or `/uf=`) and a local runtime (`/rp=`). The
  general shape:
  ```text
  Igor.exe /lf=<licence file> /rp=<runtime folder> /project=<path>\Beacon.yyp /of=<output> -- Windows PackageZip
  ```
  Copy the exact invocation from the IDE's build output (it prints its Igor command line) rather than
  writing one from memory.
- Runs and debugging otherwise happen in the IDE: the human presses Run. You read the output log and the
  files the game writes.

## Debug hooks and oracles
- **A test room:** read launch parameters with `parameter_count()` / `parameter_string(i)`. When `--autotest`
  is present, jump to a test room that runs assertions, prints results with `show_debug_message`, and ends
  with `game_end(code)` where supported. Otherwise exit with a marker line the runner can grep.
- **Screenshots:** `screen_save("shot.png")`, or `surface_save()` for a specific surface.
- **Determinism:** `random_set_seed(seed)` (and avoid `randomize()` in tests). Write movement in
  `delta_time` (microseconds) or a fixed `game_set_speed`, consistently.
- **Agent bridge:** GameMaker has networking functions (`network_create_server`, async networking events)
  for a localhost command server in debug builds. It's more work than in code-first engines; a file-drop
  (the game polls a commands file) is often simpler.

## Pitfalls
- **Event order:** Begin Step → Step → End Step → Draw. Logic split across them causes one-frame bugs.
- **Instance deactivation** hides instances from `with` and collisions.
- **Texture pages:** group sprites into texture groups per level, or memory and swaps balloon.
- **YYC vs VM:** the compiled target and the VM can behave differently. Test the target you ship.
- **Web exports** (HTML5 and GX.games/WASM) differ from desktop. Test early if the web matters.
