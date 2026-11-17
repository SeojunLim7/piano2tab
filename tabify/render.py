"""줄 배치 결과를 텍스트 tab으로 출력한다 (위에서부터 1번줄 e ~ 6번줄 E)."""
from __future__ import annotations

from .data import Song
from .guitar import STRING_NAMES, fret_of


def render_tab(song: Song, assignment: list[list[int]], per_line: int = 16) -> str:
    columns = []
    for chord, strings in zip(song, assignment):
        col = {s: str(fret_of(n.pitch, s)) for n, s in zip(chord, strings)}
        width = max(len(v) for v in col.values()) if col else 1
        columns.append([col.get(s, "-").ljust(width, "-") for s in range(6)])

    blocks = []
    for start in range(0, len(columns), per_line):
        chunk = columns[start:start + per_line]
        lines = []
        for s in reversed(range(6)):          # 높은 e 줄을 맨 위에
            body = "-".join(c[s] for c in chunk)
            lines.append(f"{STRING_NAMES[s]}|-{body}-|")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)
