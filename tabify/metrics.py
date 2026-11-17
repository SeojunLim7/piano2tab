"""평가 지표.

- string_acc : 사람(GuitarSet 연주자)과 같은 줄을 고른 음의 비율
- chord_acc  : 화음 전체가 사람과 똑같은 비율
- playable   : 실제로 칠 수 있는 화음의 비율 (줄 중복 없음 + 프렛 폭 ≤ 4)
- avg_move   : 화음 사이 평균 손 이동 (프렛). 작을수록 편한 운지.
"""
from __future__ import annotations

import numpy as np

from .data import Song
from .decode import hand_position, is_playable


def evaluate(songs: list[Song], predictions: list[list[list[int]]]) -> dict:
    n_note = n_note_ok = n_chord = n_chord_ok = n_play = 0
    moves = []
    for song, pred in zip(songs, predictions):
        pos = None
        for chord, strings in zip(song, pred):
            pitches = [n.pitch for n in chord]
            truth = [n.string for n in chord]
            n_note += len(chord)
            n_note_ok += sum(int(a == b) for a, b in zip(strings, truth))
            n_chord += 1
            n_chord_ok += int(list(strings) == truth)
            n_play += int(is_playable(pitches, strings))
            new_pos = hand_position(pitches, strings, prev=pos if pos is not None else 0.0)
            if pos is not None:
                moves.append(abs(new_pos - pos))
            pos = new_pos
    return {
        "string_acc": n_note_ok / max(n_note, 1),
        "chord_acc": n_chord_ok / max(n_chord, 1),
        "playable": n_play / max(n_chord, 1),
        "avg_move": float(np.mean(moves)) if moves else 0.0,
    }
