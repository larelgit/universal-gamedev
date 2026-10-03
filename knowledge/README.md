# The AI game-dev knowledge base

Field notes on how games were actually built with AI agents. **Agents write them for the next agent**, and
pull requests review them. Each note records what one project learned the hard way:
- the exact engine and plugin versions that worked;
- how the game is put together;
- how it was verified;
- and above all the **gotchas** (symptom → cause → fix).

The next agent that builds the same kind of game, or uses the same engine, starts with that instead of
rediscovering it. The format follows
[universal-modder's knowledge base](https://github.com/rehan-remade/universal-modder/tree/main/knowledge),
which does the same for game modding.

**It starts empty.** No notes ship with the toolkit, because notes are only worth reading when they come
from real sessions with real verification. The first agent to finish a game here writes the first one.

- [`INDEX.md`](INDEX.md) lists every note (`index.json` is the same data for tools).
- `projects/<engine>/<note>.md`: one project or feature each (a game, a prototype, a system inside a game).
- `techniques/<note>.md`: cross-engine methods (oracles for games, golden images, deterministic replays, web
  export, trailer capture...).
- Engine playbooks (routes, commands and pitfalls per engine) live with the skills, in
  [`../skills/make-any-game/references/engines/`](../skills/make-any-game/references/engines/).

## Before you start a game: search
```bash
ugd kb search "<engine>"                       # in a clone or plugin; elsewhere it syncs this folder from GitHub
ugd kb search "deckbuilder" --engine phaser
ugd kb show projects/godot/<note>.md
```
No `ugd`? Read [`INDEX.md`](INDEX.md).

## After you finish (or get stuck): write it up and open a PR
A note is worth writing whenever you learned something the next agent would otherwise lose an hour to, even
if the game isn't finished. `status: prototype` and `abandoned` are welcome; dead ends are knowledge.

```bash
ugd kb new --title "<what you built>" --game "<title>" --genre "<genre>" --from-scan . --agent "<agent (model)>"
# fill it in: Setup (exact versions), Architecture, Verification, Gotchas
ugd kb check knowledge/projects/<engine>/<note>.md
ugd kb pr knowledge/projects/<engine>/<note>.md          # dry run; add --yes once your human agrees
```
The full rules for contributors, human or AI, are in [`../CONTRIBUTING.md`](../CONTRIBUTING.md). In short:
- no secrets, and nothing you don't have the rights to share;
- describe what you learned in your own words;
- name the agent and model;
- say honestly what you did and didn't verify.

## What makes a good note
- **Versions.** "Godot 4.5.1 + GUT 9.4 on Windows 11" beats "latest".
- **Gotchas with causes.** "The web build was silent because browsers block audio until a user gesture;
  fixed with a click-to-start screen" is reusable. "Audio was broken" isn't.
- **The oracle.** How you knew it worked, so the next agent can re-verify it after an engine update.
- **Short code.** A snippet of *your own* code is fine. Link to the repo for the rest.
