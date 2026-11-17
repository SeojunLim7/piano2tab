"""화음 하나에 대해 '가능한 줄 배치'를 모두 만들고, 점수가 가장 좋은 배치를 고른다.

규칙: 한 화음 안에서 같은 줄을 두 번 쓸 수 없고, 누른 프렛들의 폭(span)이 너무 넓으면 손가락이 닿지 않는다.
"""
from __future__ import annotations

import itertools

import numpy as np

from .guitar import fret_of, valid_strings

MAX_SPAN = 4   # 개방현(0프렛)을 뺀 프렛 폭의 상한 (예: 3~7프렛)


def span(pitches, strings) -> int:
    frets = [fret_of(p, s) for p, s in zip(pitches, strings) if fret_of(p, s) > 0]
    return max(frets) - min(frets) if frets else 0


def hand_position(pitches, strings, prev: float) -> float:
    """손의 위치 = 누른 프렛들의 평균. 전부 개방현이면 손이 이전 위치에 그대로 있다고 본다."""
    frets = [fret_of(p, s) for p, s in zip(pitches, strings) if fret_of(p, s) > 0]
    return float(np.mean(frets)) if frets else prev


def candidates(pitches: list[int], max_span: int = MAX_SPAN) -> list[tuple[int, ...]]:
    """화음의 모든 가능한 줄 배치. 칠 수 있는 배치가 하나도 없으면 span 제한을 풀어서 다시 찾는다."""
    options = [valid_strings(p) for p in pitches]
    all_assign = [a for a in itertools.product(*options) if len(set(a)) == len(a)]
    playable = [a for a in all_assign if span(pitches, a) <= max_span]
    if playable or all_assign:
        return playable or all_assign
    # 줄을 겹치지 않고는 칠 수 없는 화음(예: E2와 F2를 동시에 = 둘 다 6번줄에서만 가능)
    # → 어쩔 수 없이 줄 중복을 허용한 배치를 돌려준다 (평가에서 playable=0으로 잡힌다)
    return list(itertools.islice(itertools.product(*options), 200))


def is_playable(pitches, strings, max_span: int = MAX_SPAN) -> bool:
    return len(set(strings)) == len(strings) and span(pitches, strings) <= max_span


def constrained_decode(pitches: list[int], logp: np.ndarray) -> tuple[int, ...]:
    """모델이 음마다 낸 줄 확률(log)을 받아, 규칙을 지키는 배치 중 확률 합이 가장 큰 것을 고른다.

    모델은 음마다 따로 예측하므로 두 음에 같은 줄을 줄 수도 있다. 이 단계가 그런 '칠 수 없는 답'을 걸러낸다.
    """
    cands = candidates(pitches)
    if not cands:  # 6개 넘는 음 등 정말 불가능한 경우: 그냥 음마다 최선
        return tuple(int(np.argmax(row)) for row in logp)
    scores = [sum(logp[i, s] for i, s in enumerate(a)) for a in cands]
    return cands[int(np.argmax(scores))]
