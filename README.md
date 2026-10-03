# universal-gamedev

**Skills, tools and a shared knowledge base that let any AI coding agent make a game, in almost any engine,
from an idea to a tested, playable, shareable build.**

Works with Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode, or anything that reads
`AGENTS.md`. The agent plans the game and picks the engine, then builds it:
- gets the core loop working first;
- makes art, 3D and sound with [fal](https://fal.ai);
- **proves the game works with oracles** (tests, headless simulations, screenshots it actually looks at,
  golden images, replays), with you as the playtester;
- polishes the feel, exports builds and cuts a trailer;
- writes down what it learned for the next agent.

It's the game-*making* sibling of [universal-modder](https://github.com/rehan-remade/universal-modder), which
mods games you don't have the source for. It follows universal-modder's method and layout, and reuses its
`um` CLI for assets, sprites, capture and video.

## Install
Pick your agent. Each gets the same skills (Agent Skills format), the fal MCP server, and the `ugd` CLI.

| Agent | Install |
|---|---|
| **Claude Code** | `/plugin marketplace add larelgit/universal-gamedev`, then `/plugin install universal-gamedev@universal-gamedev`. From a local folder: `/plugin marketplace add C:\path\to\universal-gamedev` (or a POSIX path) |
| **Codex** | `codex plugin marketplace add larelgit/universal-gamedev`, then `codex plugin add universal-gamedev@universal-gamedev` |
| **Gemini CLI** | `gemini extensions install https://github.com/larelgit/universal-gamedev` |
| **VS Code / Copilot** | Enable `chat.plugins.enabled`, run **Chat: Install Plugin From Source**, and enter `https://github.com/larelgit/universal-gamedev` |
| **Cursor** | Clone it (Cursor reads `AGENTS.md` and `.cursor/mcp.json`) |
| **Skills only** (any agent) | `npx skills add https://github.com/larelgit/universal-gamedev` |
| **Anything else** | `git clone https://github.com/larelgit/universal-gamedev` and start your agent inside it |

In a clone, run `tools/link-skills.sh` (or `tools\link-skills.ps1` on Windows) once. It links `skills/` to
the places each agent looks: `.claude/skills`, `.agents/skills`, `.gemini/skills` and `.github/skills`.
Instructions live in `AGENTS.md`, which `CLAUDE.md` and `GEMINI.md` import. MCP config is in `.mcp.json`,
`.codex/config.toml`, `.cursor/mcp.json`, `.vscode/mcp.json` and `gemini-extension.json`.

**Requirements:**
- Python 3.10+ through [uv](https://docs.astral.sh/uv/), recommended: `bin/ugd` sets itself up with it.
- For assets, a [fal API key](https://fal.ai/dashboard/keys) in `FAL_KEY`. It powers both the fal MCP server
  and `um fal`.
- ffmpeg for video, and Blender for 3D-to-sprite renders.
- The engine you build with. The agent asks before installing one.

## Try it
> Make a survivors-like for the browser where you're a lighthouse keeping sea monsters off the rocks. Phaser +
> TypeScript, pixel art from fal.

> Which engine should I use for a 2D metroidvania I want on Steam and Switch?

> Add a two-phase boss fight to my Godot game, with tests that prove both phases trigger.

> My platformer's jump feels floaty. Fix it and show me before and after.

> Export my game for itch.io, then draft the store page and the launch post.

The agent starts with the **make-any-game** skill and runs the same loop every time:
1. search the knowledge base;
2. plan: pick the engine, define the vertical slice, write `GAME_PLAN.md`;
3. set up the project with one-command run/test/build and debug hooks;
4. get the core loop working in graybox, and hand it to you to play;
5. build systems one at a time, each with its test;
6. generate assets;
7. verify with oracles;
8. polish the game feel;
9. export early and often;
10. cut a trailer;
11. ship (you press the button);
12. write a field note for the next agent.

## A knowledge base that AIs write for AIs
[`knowledge/`](knowledge/) holds **field notes**: how specific games and features were actually built. Each
note records:
- the exact engine versions that worked;
- the architecture;
- how it was verified;
- the gotchas (symptom → cause → fix).

**It starts empty, on purpose.** Notes are only worth reading when they come from real sessions with real
verification, so this toolkit ships none. Every agent that finishes a game can open a pull request with its
note, so the next one starts where it left off.

```bash
ugd kb search "godot survivors"                         # before you start: prior art
ugd kb new --title "A survivors-like in Godot" --game "Beacon" --genre survivors-like --from-scan . --agent "Codex (gpt-6)"
ugd kb check knowledge/projects/godot/a-survivors-like-in-godot.md
ugd kb pr knowledge/projects/godot/a-survivors-like-in-godot.md --yes    # after your human says OK
```
The contribution rules, for humans and AIs, are in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## What's inside

**Skills** (`skills/`, Agent Skills format)

| Skill | What it does |
|---|---|
| `make-any-game` | The whole loop and the hard rules, with **12 engine playbooks**: Godot, Unity, Unreal, web (Phaser, three.js, PixiJS, Babylon.js, Kaplay), Bevy/Rust, LÖVE, Python (pygame-ce, Arcade, Pyxel, Ursina), .NET (MonoGame, FNA, KNI), native (raylib, SDL3, SFML), GameMaker, narrative (Ren'Py, Ink, Yarn Spinner, Twine, RPG Maker) and the rest (Defold, GDevelop, Ebitengine, Haxe, Roblox, fantasy consoles...). Also genre recipes with starting numbers, a systems cookbook and multiplayer |
| `game-plan` | Pitch, core loop, engine choice (weighted for agent-friendliness), vertical slice, scope and cut list, style bible, oracle plan; or a fingerprint of an existing project → `GAME_PLAN.md` |
| `game-assets` | fal-generated sprites, tilesets, UI, textures, PBR, 3D, rigs, SFX, music and voice → engine-exact frames → the right import settings per engine → credits |
| `playtest-automation` | The oracle ladder: unit tests, headless simulation, scene smoke tests, in-game screenshots, golden images, replays, bots, frame budgets, exported-build smoke tests, CI, an in-game agent bridge, and preparing human playtests |
| `game-feel` | Responsiveness, hit-stop, trauma-based shake, particles, layered sound, easing, camera, readability, the first minute; every effect tunable and switchable |
| `trailer-video` | A deterministic trailer mode, in-engine capture at a fixed frame rate, contact sheets, an EDL edit, store and social formats |
| `ship-game` | Release lint, exports per platform, versioning, itch.io/Steam/Epic/web portals/mobile (checked October 2026), store page, press kit, the post |
| `gamedev-field-notes` | Search the knowledge base, keep `DEVLOG.md`, write your note, open the PR |

**The `ugd` CLI** (Python; every command has `--help` with examples)

| | |
|---|---|
| `ugd scan` | Fingerprints a project: engine and version (~45 engines and frameworks), language, tests, CI, the commands that run/test/export it, and the playbook to read. `--tools` lists installed engines, SDKs and tools |
| `ugd kb` | The knowledge base: `search`, `show`, `new`, `check`, `index`, `sync`, `pr` |
| `ugd release check` | Blocks shipping secrets, keystores, certificates, Steam credentials and `steam_appid.txt`; warns about missing credits and licenses, case collisions, root-absolute web paths |
| `ugd shot diff` | Golden-image comparison with a tolerance and a diff image, for any engine that can save a PNG |

**Reused from universal-modder: `um`** (`bin/um` runs an installed `um`, or a pinned commit via `uvx`)

| | |
|---|---|
| `um fal` | Sprites, images, edits, background removal, pixel art, upscales, seamless textures, PBR, image-to-3D, rigs, SFX, music, voice, video; with a manifest of every generation |
| `um sprite`, `um render3d` | Cutout, fit, pixelate, palettes, sheets, team masks, seamless tiles; GLB → sprite frames from the game's camera (Blender) |
| `um win` | Launch, screenshot (GPU-safe), drive input and record a running desktop build on Windows |
| `um video` | Contact sheets, EDL-compiled trailers with titles and music |

## Rules it follows
- **Original work.** Genres and mechanics are free to use; names, characters, art, music, levels and the
  look of existing games are not. No ripped or leaked assets or code.
- **Credits and licenses** for every asset it didn't make from scratch, and honest AI disclosure where stores
  ask for it.
- **No secrets** (API keys, keystores, certificates, store credentials) in repos or builds, and no fal or LLM
  key inside a game client.
- **It asks before** installing engines, driving your mouse and keyboard, or uploading or publishing
  anything (PRs included). You enter your own store credentials.

Full reasoning: [`skills/make-any-game/references/rules.md`](skills/make-any-game/references/rules.md).

## Status, honestly
- **Version 0.1.0 (October 2026).**
- **Sources:** the skills and playbooks were written from engine documentation and established game-dev
  practice. Version-sensitive claims (CLI flags, engine versions, store rules) were fact-checked against
  official docs in October 2026.
- **Untested in practice:** no game has been built *with this toolkit* yet, so there are no worked examples
  and no field notes. Treat the playbooks as a strong starting point, and let the first real projects
  correct them.
- **`ugd` is covered by tests**, which also check every skill's front matter, that every referenced file
  exists, and that every `ugd`/`um` command the docs cite is real.

## Forking it
- `ugd kb sync`, `ugd kb search` (outside a clone) and `ugd kb pr` use the knowledge base in
  `larelgit/universal-gamedev`. Point them at your fork with `UGD_KB_REPO=<you>/<repo>`.
- The scripts are committed as executable, and `.gitattributes` keeps their line endings correct on every
  OS. If you add a script from Windows, mark it with `git update-index --chmod=+x <file>`.

## Credits
- **[universal-modder](https://github.com/rehan-remade/universal-modder)** by Rehan and contributors (MIT):
  the method, the repo layout, the knowledge-base format, the fal recipes and prompting rules, and the
  showcase-video and field-notes skills are adapted from it, and its `um` CLI is reused for assets, capture
  and video.
- [fal](https://fal.ai) for generative assets; every engine, framework and tool named in the playbooks.

MIT licensed (see [`LICENSE`](LICENSE), which also carries universal-modder's notice).
