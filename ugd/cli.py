"""`ugd` command line: one entry point for every tool, so skills can say `ugd <group> <cmd>`."""
from __future__ import annotations

import argparse
import importlib
import sys

from ugd import __doc__ as DOC, __version__

GROUPS = ["scan", "kb", "release", "shot"]


def main(argv=None):
    # Piped output on Windows defaults to the ANSI code page (cp1252), which can't encode "→" or "LÖVE";
    # agents read pipes, so always speak UTF-8.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(prog="ugd", description=DOC, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"universal-gamedev {__version__}")
    sub = ap.add_subparsers(dest="group", metavar="<group>")
    for g in GROUPS:
        importlib.import_module(f"ugd.{g}").register(sub)
    args = ap.parse_args(argv)
    if not getattr(args, "func", None):
        # a group without a command: show that group's help
        if args.group:
            ap.parse_args([args.group, "--help"])
        ap.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
