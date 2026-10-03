# universal-gamedev

A game-development toolkit and a shared knowledge base for AI coding agents: Claude Code, Codex, Cursor,
Gemini CLI, GitHub Copilot, OpenCode and anything else that reads `AGENTS.md`. When someone opens an agent in
this repo, or installs it as a plugin, they almost always want to **make a game**, extend a game they're
making, or learn how a game was built. To change a game they don't have the source for, that's modding: use
universal-modder (https://github.com/rehan-remade/universal-modder).

## Start here
1. **Read `skills/make-any-game/SKILL.md` and follow its loop:** intake → plan → project setup → vertical
   slice → systems → assets → verify with oracles → game feel → export → trailer → ship → field note.
2. **Search the knowledge base first:** `bin/ugd kb search "<engine or genre>"`. Other agents may already
   have written down the exact versions, architecture and gotchas (`knowledge/INDEX.md`).
3. **At the end, share what you learned:** write a field note (`bin/ugd kb new ...`) and, once your human
   agrees, open a PR (`bin/ugd kb pr <note> --yes`). See `knowledge/README.md` and `CONTRIBUTING.md`.

## Tools
- **`bin/ugd`** is this toolkit's Python CLI, set up through `uv` (`bin/ugd.cmd` for cmd and PowerShell).
  Every group has `--help`:
  - `scan`: fingerprint a project (engine, version, tests, run/test/export commands); `--tools` lists
    installed engines and SDKs;
  - `kb`: the knowledge base;
  - `release`: the pre-release lint;
  - `shot`: golden-image comparison.
- **`bin/um`** is universal-modder's CLI, reused rather than copied, for fal assets, sprites, 3D-to-sprite
  renders, window capture and input on Windows, and video editing. It runs an installed `um`, or a pinned
  commit through `uvx`.
- **fal MCP server:** `https://mcp.fal.ai/mcp` with the header `Authorization: Bearer $FAL_KEY`.
  - It's pre-configured per agent: `.mcp.json` (Claude Code), `.codex/config.toml` (Codex),
    `.cursor/mcp.json` (Cursor), `.vscode/mcp.json` (VS Code / Copilot), `gemini-extension.json`
    (Gemini CLI).
  - No MCP? `um fal` does the same over REST.
- **Skills** (`skills/*/SKILL.md`, Agent Skills format). In a clone, `tools/link-skills.sh` (or
  `tools/link-skills.ps1`) links them where each agent looks: `.agents/skills`, `.claude/skills`,
  `.gemini/skills` and `.github/skills`.
- **Engine playbooks:** `skills/make-any-game/references/engines/`. Genre recipes, the systems cookbook,
  multiplayer and the rules sit next to them in `references/`.

## Rules (full reasoning in `skills/make-any-game/references/rules.md`)
- **Original work:** genres and mechanics yes; the names, characters, art, music, levels and look of
  existing games no. No ripped or leaked assets or code.
- **Credits and licenses:** every asset that wasn't made from scratch gets a line in the game's
  `CREDITS.md`, generated ones included (with the model).
- **Secrets:** no API keys, keystores, certificates or store credentials in repos or builds, and never a fal
  or LLM key inside a game client.
- **Honesty:** disclose AI-generated content where stores ask, and never claim verification that didn't
  happen.
- **Ask first** before:
  - installing engines or SDKs, or changing global settings;
  - driving the user's mouse and keyboard;
  - uploading builds, creating store pages, posting, or opening PRs (publishing is the user's call). The
    human enters their own credentials.
- **Processes and network:** kill by exact PID only. Bind agent bridges and dev servers to `127.0.0.1`.
- **Keep a journal:** `DEVLOG.md` in the game's project root. It becomes your field note at the end.

## Working on the toolkit itself
- **Python:** 3.10+, with PyYAML and Pillow (`uv` handles them via `bin/ugd`). Code lives in `ugd/`, one
  module per CLI group, each with `register(sub)` and a docstring that doubles as `--help`.
- **Tests:** `uv run --with pytest pytest -q tests`. They also check every skill's front matter, that
  referenced files exist, and that every `ugd`/`um` command cited in the docs is real. CI also runs
  `ugd kb check --index` and `ugd release check .`.
- **Wording:** keep skills and docs agent-neutral ("the agent", "you"), except in sections about one specific
  agent. Versions move: write stable facts, and say "check the current release" for versions.
