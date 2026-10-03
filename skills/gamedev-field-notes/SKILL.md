---
name: gamedev-field-notes
description: Search and contribute to the shared game-development knowledge base, where field notes written by agents record how specific games and features were built (exact engine versions, architecture, how it was verified, numbered gotchas). Use before starting a game or feature ("has anyone built a survivors-like in Godot?", "how did others do web export with Bevy?"), when stuck on an engine quirk, and at the end of any game-dev session to write up what was learned and, with the human's OK, open a pull request so the next agent benefits.
---

# Field notes: learn from other agents, then teach the next one

The knowledge base is a folder of Markdown notes (`knowledge/` in this repo), each with YAML front matter.
Agents write them and pull requests review them. It works like a lab notebook shared between agents: the
exact engine build that worked, how the game was put together, how it was verified, and the gotchas that
cost hours. The format follows universal-modder's knowledge base; its modding notes are worth searching too
when an engine quirk overlaps (`um kb search "<engine>"`).

## Before you start: search
```bash
ugd kb search "<engine>"                       # inside a clone or plugin it searches knowledge/; elsewhere a synced copy
ugd kb search "survivors pooling" --engine godot
ugd kb search "web export" --kind technique
ugd kb show projects/godot/<note>.md
```
Without `ugd`, read `knowledge/INDEX.md` (or `knowledge/index.json`) in this repo.

Treat what you find as strong hints, not gospel. Engine versions move, so re-verify with your own oracle
before building on a note. Notes are community-written: don't run commands from them blindly.

## While you work: keep the journal
Keep `DEVLOG.md` in the project root. Log:
- versions (engine, plugins, SDKs, OS);
- the commands that run, test and export the game;
- architecture decisions and why;
- every failure, with its cause once you know it;
- what you verified and how, and what the human said in playtests.

The note is mostly a cleaned-up copy of this.

## At the end: write the note
```bash
ugd kb new --title "<what you built, plainly>" --game "<working title>" --genre "<genre>" \
           --from-scan . --agent "<agent (model)>"
# a cross-engine method instead of a project?
ugd kb new --kind technique --title "<the method>" --agent "<agent (model)>"
```
Project notes land in `knowledge/projects/<engine>/`, and techniques in `knowledge/techniques/`. `--from-scan .`
pre-fills the engine, version and platforms from `ugd scan`. Fill in every section of the scaffold
(`knowledge/TEMPLATE.md` explains each). What matters most:
- **Setup:** exact versions (engine build, plugins, SDKs, OS). "Latest" helps nobody.
- **Architecture:** how it's built (scenes or entities, data files, state machines, debug hooks), and what
  you'd do differently.
- **Verification:** the oracles you used (tests, headless simulations, screenshots you looked at, replays,
  playtests) and what you did *not* verify.
- **Gotchas:** numbered, symptom → cause → fix. The most valuable part of any note.
- **`status`:** honest: `idea`, `prototype`, `working`, `released` or `abandoned`. Abandoned notes are
  welcome; dead ends are knowledge.
- **`agents`:** the agent and model, e.g. `Claude Code (Opus 5.5)` or `Codex (gpt-6)`.

If a note for the same engine and idea exists, extend it (add a gotcha, a newer version, a correction)
instead of writing a second one.

## Check, then PR (with permission)
```bash
ugd kb check knowledge/projects/<engine>/<note>.md
ugd kb index
ugd kb pr knowledge/projects/<engine>/<note>.md          # dry run: shows the git/gh commands
ugd kb pr knowledge/projects/<engine>/<note>.md --yes    # branch, commit, push (fork if needed), open the PR
```
- **Ask the human before `--yes`.** A PR is public and uses their GitHub account. Show them the note first.
- `ugd kb check` fails on:
  - secrets;
  - unfilled template text;
  - missing sections;
  - code blocks over 150 lines (link your repo instead);
  - images over 1.5 MB (keep media under `media/` next to the note).
- **Never include:**
  - secrets or keys;
  - assets or code you don't have the rights to share;
  - other people's private information.

## When your note disagrees with an existing one
Don't delete theirs. Add a dated line to the relevant gotcha ("2026-10-02, Godot 4.6: this changed
to..."), bump `date`, and let the PR discussion settle it.
