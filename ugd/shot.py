"""Golden-image checks: compare a screenshot against an approved one, with a tolerance.

    ugd shot diff tests/golden/arena.png out/arena.png                     # exit 0 if close enough, 1 if not
    ugd shot diff golden.png actual.png --out diff.png --threshold 12 --max-ratio 0.002
    ugd shot diff golden.png actual.png --update                          # approve: copy actual over the golden
    ugd shot diff golden.png actual.png --json                            # machine-readable result

A pixel counts as changed when any channel (RGBA) differs by more than --threshold (0-255). The check passes
when the fraction of changed pixels is at most --max-ratio. The diff image shows the actual frame dimmed, with
changed pixels in red. Goldens only compare like with like: same resolution, renderer and platform, a fixed
seed, and juice (shake, particles) off or seeded. Approve a new golden only after looking at it.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from ugd.common import die


def _pil():
    try:
        from PIL import Image, ImageChops
    except ImportError:
        die("this command needs Pillow: `pip install pillow` (or run through bin/ugd, which uses uv)")
    return Image, ImageChops


def diff(expected: Path, actual: Path, threshold: int = 8, max_ratio: float = 0.001, out: Path | None = None) -> dict:
    Image, ImageChops = _pil()
    a = Image.open(expected).convert("RGBA")
    b = Image.open(actual).convert("RGBA")
    res = dict(expected=str(expected), actual=str(actual), threshold=threshold, max_ratio=max_ratio,
               size_expected=list(a.size), size_actual=list(b.size))
    if a.size != b.size:
        res.update(passed=False, reason=f"size differs: {a.size[0]}x{a.size[1]} vs {b.size[0]}x{b.size[1]}",
                   changed=None, ratio=None)
        return res
    d = ImageChops.difference(a, b)
    r, g, bl, al = d.split()
    worst = ImageChops.lighter(ImageChops.lighter(r, g), ImageChops.lighter(bl, al))
    mask = worst.point(lambda v: 255 if v > threshold else 0)
    changed = mask.histogram()[255]
    total = a.size[0] * a.size[1]
    ratio = changed / total if total else 0.0
    res.update(changed=changed, total=total, ratio=ratio, max_channel_diff=worst.getextrema()[1],
               passed=ratio <= max_ratio,
               reason=f"{ratio:.4%} of pixels changed ({changed} / {total}); allowed {max_ratio:.4%}")
    if out:
        base = Image.blend(Image.new("RGBA", b.size, (0, 0, 0, 255)), b.convert("L").convert("RGBA"), 0.35)
        red = Image.new("RGBA", b.size, (255, 32, 32, 255))
        base.paste(red, (0, 0), mask)
        out.parent.mkdir(parents=True, exist_ok=True)
        base.convert("RGB").save(out)
        res["diff_image"] = str(out)
    return res


def main(a):
    expected, actual = Path(a.expected), Path(a.actual)
    if not actual.exists():
        die(f"no such file: {actual}")
    if a.update:
        expected.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(actual, expected)
        print(f"APPROVED: {actual} -> {expected}")
        return
    if not expected.exists():
        die(f"no golden at {expected}: look at {actual}, then approve it with --update")
    res = diff(expected, actual, a.threshold, a.max_ratio, Path(a.out) if a.out else None)
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"{'PASS' if res['passed'] else 'FAIL'}: {res['reason']}" + (f"  diff: {res['diff_image']}" if res.get("diff_image") else ""))
    raise SystemExit(0 if res["passed"] else 1)


def register(sub):
    import argparse
    p = sub.add_parser("shot", help="golden-image checks: compare screenshots with a tolerance",
                       description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cs = p.add_subparsers(dest="cmd", metavar="<cmd>")
    q = cs.add_parser("diff", help="compare an actual screenshot with the approved golden")
    q.add_argument("expected", help="the approved golden PNG")
    q.add_argument("actual", help="the new screenshot")
    q.add_argument("--threshold", type=int, default=8, help="per-channel difference (0-255) that counts as changed (default 8)")
    q.add_argument("--max-ratio", type=float, default=0.001, help="allowed fraction of changed pixels (default 0.001 = 0.1%%)")
    q.add_argument("--out", help="write a diff image here")
    q.add_argument("--update", action="store_true", help="approve: copy actual over expected")
    q.add_argument("--json", action="store_true")
    q.set_defaults(func=main)
