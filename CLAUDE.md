@AGENTS.md

## Claude Code specifics
- Installed as a plugin, the skills are namespaced (`/universal-gamedev:make-any-game`), and the fal MCP
  server comes from `.mcp.json` (it needs `FAL_KEY` in the environment). A SessionStart hook puts `bin/`
  (`ugd`, `um`) on PATH for the Bash tool.
- In a clone, `.claude/settings.json` adds the same PATH hook. Run `tools/link-skills.sh` (or
  `tools\link-skills.ps1` on Windows) once to link `.claude/skills` to `skills/`.
- On Windows the PATH hook covers the Bash tool. From PowerShell, call `bin\ugd.cmd` by its path, or add
  `bin\` to PATH.
