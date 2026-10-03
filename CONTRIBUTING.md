# Contributing

Contributions from humans and from AI agents are both welcome. Most of them will be **field notes** for the
knowledge base (`knowledge/`), written by an agent at the end of a game-dev session. That's the point of the
repo: every game one agent builds becomes something the next agent can read.

## If you are an AI agent
You just built (or tried to build) a game or a feature, and you learned things. Share them:

1. **Ask your human first.** A pull request is public and carries their GitHub identity. Tell them what you
   want to publish and show them the note.
2. **Check it's new:** `ugd kb search "<engine>"`. If a note for the same engine and idea exists, improve it:
   add your versions and gotchas, and fix what's wrong. Don't write a second one.
3. **Scaffold:**
   `ugd kb new --title "<what you built>" --game "<title>" --genre "<genre>" --from-scan . --agent "<agent (model)>"`.
   It lands in `knowledge/projects/<engine>/`. Cross-engine methods go in `techniques/` (`--kind technique`).
4. **Fill it in** from your journal (`DEVLOG.md`):
   - exact versions;
   - the architecture;
   - build and export steps;
   - how you verified it, and what you didn't;
   - numbered **gotchas** (symptom → cause → fix).

   Write for an agent that has never seen this engine.
5. **Validate:** `ugd kb check <note>`, then `ugd kb index`.
6. **Open the PR:** `ugd kb pr <note>` (a dry run shows the commands), then `ugd kb pr <note> --yes`. It
   branches, commits the note (plus `media/` and the index), forks if needed, pushes, and opens the PR with
   `gh`. Without `gh`, push a branch and open the PR on github.com.

## Hard rules (PRs that break these are closed)
- **Nothing you don't have the rights to share:** no third-party assets, no other games' content, no leaked
  code, and no pasted source from closed engines or asset-store packages.
- **Short code only.** Describe the approach in your own words and link your repo. `ugd kb check` fails code
  blocks over 150 lines and warns over 60.
- **No secrets:** API keys, tokens, keystores, certificates, `.env` files. `ugd kb check` and
  `ugd release check` catch the common ones.
- **Honesty:**
  - name the agent and model (`agents:`);
  - mark `status` truthfully (`idea`, `prototype`, `in-progress`, `working`, `released`, `abandoned`);
  - list what you did not verify.
- **Credit** the people, projects and tools you built on.

## Other contributions
- **Tools (`ugd/`):**
  - one module per CLI group, with a docstring that doubles as `--help`;
  - add a test in `tests/`;
  - `uv run --with pytest pytest -q tests` must pass.
- **Skills (`skills/`):** the Agent Skills format (`SKILL.md` with `name` + `description`). Keep them
  agent-neutral: say "the agent" or "you", not a specific product. Put deep material in `references/`, and
  keep each `SKILL.md` under 500 lines.
- **Engine playbooks** (`skills/make-any-game/references/engines/`): when to pick the engine, setup, the
  agent workflow, commands, debug hooks, pitfalls. Link the canonical projects. Versions move, so say "check
  the current release" and date any version you name.
- **Examples (`examples/`):** your own code and assets only, with a README, and passing
  `ugd release check`.

CI runs the tests, `ugd kb check --index` and `ugd release check .` on every PR.
