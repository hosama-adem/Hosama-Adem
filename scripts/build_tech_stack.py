"""Builds assets/tech-stack.svg: skillicons logos clipped into glowing circles.

GitHub strips CSS from README HTML, so circular icons have to be baked into an SVG.
Run: python scripts/build_tech_stack.py
"""

import re
import urllib.request
from pathlib import Path

ROWS = [
    ["go", "python", "fastapi", "cpp", "ts", "js", "bash", "postgres"],
    ["mongodb", "redis", "mysql", "pytorch", "tensorflow", "sklearn", "opencv", "docker"],
    ["kubernetes", "githubactions", "linux", "vercel", "git", "postman", "vscode"],
]

ICON = 256
GAP = 72
RING = 14
PAD = 56
OUT = Path(__file__).resolve().parent.parent / "assets" / "tech-stack.svg"


def fetch_icon(name: str) -> str:
    url = f"https://skillicons.dev/icons?i={name}&theme=dark"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        wrapper = resp.read().decode("utf-8")
    inner = re.search(r"<g transform=\"translate\(0, 0\)\">\s*(<svg.*</svg>)\s*</g>", wrapper, re.S)
    if not inner:
        raise RuntimeError(f"unexpected SVG format for {name}")
    svg = inner.group(1)
    ids = set(re.findall(r'id="([^"]+)"', svg))
    for old in sorted(ids, key=len, reverse=True):
        new = f"{name}-{old}"
        svg = svg.replace(f'id="{old}"', f'id="{new}"')
        svg = svg.replace(f"url(#{old})", f"url(#{new})")
        svg = svg.replace(f'href="#{old}"', f'href="#{new}"')
    return svg


def build() -> str:
    cols = max(len(r) for r in ROWS)
    cell = ICON + GAP
    width = PAD * 2 + cols * cell - GAP
    height = PAD * 2 + len(ROWS) * cell - GAP
    r = ICON / 2

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width // 4}" height="{height // 4}" viewBox="0 0 {width} {height}" fill="none">',
        "<defs>",
        f'<clipPath id="circle"><circle cx="{r}" cy="{r}" r="{r}"/></clipPath>',
        '<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#58a6ff"/><stop offset="0.5" stop-color="#1f6feb"/>'
        '<stop offset="1" stop-color="#a371f7"/></linearGradient>',
        '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="10" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        "</defs>",
        "<style>"
        ".halo{animation:pulse 3.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
        "@keyframes pulse{0%,100%{opacity:.35}50%{opacity:1}}"
        "</style>",
    ]

    index = 0
    for row_i, row in enumerate(ROWS):
        offset = (cols - len(row)) * cell / 2
        for col_i, name in enumerate(row):
            x = PAD + offset + col_i * cell
            y = PAD + row_i * cell
            delay = (index % 8) * 0.4
            parts.append(f'<g transform="translate({x}, {y})"><title>{name}</title>')
            parts.append(
                f'<circle class="halo" style="animation-delay:{delay:.1f}s" cx="{r}" cy="{r}" '
                f'r="{r + RING}" stroke="url(#ring)" stroke-width="{RING / 1.4}" filter="url(#glow)"/>'
            )
            parts.append(f'<g clip-path="url(#circle)">{fetch_icon(name)}</g>')
            parts.append("</g>")
            index += 1

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT}")
