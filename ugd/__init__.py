"""universal-gamedev: tools any AI agent (Claude Code, Codex, Cursor, Gemini CLI, ...) uses to make games.

Subcommands (see `ugd --help`):
  scan      fingerprint a game project (engine, version, language, tests, run/test/export commands)
            and list the engines and SDKs installed on this machine
  kb        the knowledge base: search prior field notes, write your own, check it, open a PR
  release   lint a project or an exported build before shipping: secrets, keystores, credits, licenses
  shot      golden-image checks: compare a screenshot against an approved one, with a tolerance

Assets, sprites, 3D-to-sprite renders, window capture, input and video editing come from universal-modder's
`um` CLI (https://github.com/rehan-remade/universal-modder), which this toolkit reuses rather than copies.
"""

__version__ = "0.1.0"
