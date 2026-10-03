#!/usr/bin/env bash
# SessionStart hook: put universal-gamedev's bin/ on PATH for every later shell call in the session,
# so skills can just say `ugd ...` and `um ...`. Arg 1: the toolkit root (plugin root or the cloned repo).
root="${1:-${CLAUDE_PLUGIN_ROOT:-${CLAUDE_PROJECT_DIR:-}}}"
[ -n "$root" ] && [ -n "${CLAUDE_ENV_FILE:-}" ] || exit 0
# Git Bash on Windows: C:\x\y must become /c/x/y, or the drive colon splits PATH
command -v cygpath >/dev/null 2>&1 && root="$(cygpath -u "$root")"
[ -f "$root/bin/ugd" ] || exit 0
grep -qs "universal-gamedev-path" "$CLAUDE_ENV_FILE" && exit 0
printf 'export PATH="%s/bin:$PATH"  # universal-gamedev-path\n' "$root" >> "$CLAUDE_ENV_FILE"
exit 0
