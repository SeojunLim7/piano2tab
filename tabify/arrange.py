"""피아노 악보(MIDI / MusicXML) → 기타로 칠 수 있는 음 시퀀스로 편곡(규칙 기반).

피아노는 88건반이고 열 손가락으로 치지만, 기타는 음역이 좁고(E2~C6) 동시에 최대 6음이다.
그래서 두 가지를 한다.
  1) 음역 접기: 기타 음역 밖의 음은 옥타브 단위로 옮겨 넣는다.
  2) 음 줄이기: 화음이 max_notes개를 넘으면 멜로디(가장 높은 음)와 베이스(가장 낮은 음)를 우선 남긴다.
"""
from __future__ import annotations

from collections import defaultdict

from .data import Note, Song
from .guitar import HIGHEST, LOWEST

SECONDS_PER_QUARTER = 0.5   # 템포 정보가 없을 때 4분음표 = 0.5초(♩=120)로 가정


def fold(pitch: int) -> int:
    while pitch < LOWEST:
        pitch += 12
    while pitch > HIGHEST:
        pitch -= 12
    return pitch


def reduce_chord(pitches: list[int], max_notes: int) -> list[int]:
    ps = sorted(set(fold(p) for p in pitches))
    if len(ps) <= max_notes:
        return ps
    keep = [ps[-1], ps[0]]                 # 멜로디, 베이스
    for p in reversed(ps[1:-1]):           # 나머지는 위쪽 음부터 채운다
        if len(keep) >= max_notes:
            break
        keep.append(p)
    return sorted(keep)


def load_score(path: str):
    from music21 import converter, corpus
    if path.startswith("corpus:"):         # 예) corpus:bach/bwv66.6  (music21 내장 악보)
        return corpus.parse(path[len("corpus:"):])
    return converter.parse(path)


def score_to_song(path: str, max_notes: int = 4, transpose: int = 0) -> Song:
    """transpose: 전체를 반음 단위로 옮긴다 (예: -12 = 한 옥타브 아래). 피아노 멜로디는 기타보다 높은 경우가 많다."""
    from music21 import chord as m21chord, harmony, note as m21note

    score = load_score(path)
    by_offset = defaultdict(list)
    for el in score.flatten().notes:
        if isinstance(el, harmony.ChordSymbol):          # 코드 이름 기호는 실제 음이 아니므로 제외
            continue
        if el.tie is not None and el.tie.type in ("stop", "continue"):
            continue                                     # 붙임줄로 이어진 음은 다시 치지 않는다
        if isinstance(el, m21note.Note):
            by_offset[float(el.offset)].append(el.pitch.midi + transpose)
        elif isinstance(el, m21chord.Chord):
            by_offset[float(el.offset)].extend(p.midi + transpose for p in el.pitches)

    song: Song = []
    for off in sorted(by_offset):
        pitches = reduce_chord(by_offset[off], max_notes)
        song.append([Note(onset=off * SECONDS_PER_QUARTER, pitch=p, string=None) for p in pitches])
    return song


def score_info(path: str):
    """TAB 악보를 만들 때 필요한 원곡 정보: 마디 구조, 조표, 제목."""
    from music21 import key as m21key, meter

    score = load_score(path)
    part = score.parts[0]
    measures, ts = [], (4, 4)
    for m in part.getElementsByClass("Measure"):
        found = m.getElementsByClass(meter.TimeSignature)
        if found:
            ts = (found[0].numerator, found[0].denominator)
        measures.append((float(m.offset), float(m.duration.quarterLength), ts))
    keys = part.recurse().getElementsByClass(m21key.KeySignature)
    fifths = keys[0].sharps if keys else 0
    md = score.metadata
    title = (md.title or md.movementName) if md else None
    title = title or "Guitar Tab"
    return measures, fifths, title
