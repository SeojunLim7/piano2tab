"""GuitarSet 주석(JAMS)을 읽어서 '화음(동시에 치는 음) 단위의 시퀀스'로 바꾼다.

GuitarSet의 .jams 파일은 JSON이다. namespace가 "note_midi"인 주석이 줄마다 하나씩(총 6개) 있고,
annotation_metadata.data_source 가 "0"~"5" 로 줄 번호를 알려준다. 즉 사람이 실제로 어느 줄에서
쳤는지가 정답 라벨로 들어 있다.
"""
from __future__ import annotations

import glob
import json
import os
from dataclasses import dataclass

from .guitar import MAX_FRET, fret_of


@dataclass
class Note:
    onset: float          # 시작 시각 (초)
    pitch: int            # MIDI 음높이
    string: int | None    # 정답 줄 (변환할 피아노 악보에는 없음 → None)


Chord = list[Note]        # 거의 동시에 시작하는 음들의 묶음 (음 1개짜리도 Chord)
Song = list[Chord]


def load_jams(path: str) -> list[Note]:
    with open(path) as f:
        jam = json.load(f)
    notes = []
    for ann in jam["annotations"]:
        if ann["namespace"] != "note_midi":
            continue
        string = int(ann["annotation_metadata"]["data_source"])
        for ev in ann["data"]:
            pitch = int(round(ev["value"]))
            # 벤딩 등으로 개방현보다 낮거나 너무 높게 기록된 음은 제외
            if 0 <= fret_of(pitch, string) <= MAX_FRET:
                notes.append(Note(onset=float(ev["time"]), pitch=pitch, string=string))
    notes.sort(key=lambda n: (n.onset, n.pitch))
    return notes


def group_chords(notes: list[Note], tol: float = 0.03) -> Song:
    """시작 시각이 tol(초) 이내인 음들을 하나의 화음으로 묶는다. 화음 안은 낮은 음부터."""
    song: Song = []
    for n in notes:
        if song and n.onset - song[-1][0].onset <= tol:
            # 같은 줄이 한 화음에 두 번 나오면(빠른 연타 등) 새 화음으로 분리
            if n.string is not None and any(m.string == n.string for m in song[-1]):
                song.append([n])
            else:
                song[-1].append(n)
        else:
            song.append([n])
    for ch in song:
        ch.sort(key=lambda n: n.pitch)
    return song


def player_of(path: str) -> int:
    """GuitarSet 파일명은 '00_BN1-129-Eb_comp.jams' 형식이고, 앞 두 자리가 연주자 번호다."""
    return int(os.path.basename(path)[:2])


def load_songs(data_dir: str, players: list[int]) -> list[Song]:
    paths = sorted(glob.glob(os.path.join(data_dir, "**", "*.jams"), recursive=True))
    if not paths:
        raise FileNotFoundError(f"{data_dir} 아래에 .jams 파일이 없습니다. scripts/download_guitarset.py 를 먼저 실행하세요.")
    return [group_chords(load_jams(p)) for p in paths if player_of(p) in players]
