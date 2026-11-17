"""학습 없는 기준선(baseline) 두 가지.

1) lowest_fret: 음마다 가장 낮은 프렛(=가장 굵은 줄 쪽이 아니라 개방현에 가까운 자리)을 고른다. 가장 단순한 규칙.
2) viterbi_dp : 곡 전체를 보고 '손 이동 + 화음 폭'의 총비용이 최소가 되는 배치를 동적계획법으로 찾는다.
   기타 운지 자동화의 고전적 접근(최적 경로 탐색)과 같은 아이디어다.
"""
from __future__ import annotations

from .data import Song
from .decode import candidates, hand_position, span
from .guitar import fret_of

W_MOVE = 1.0      # 화음 사이 손 이동 1프렛당 비용
W_SPAN = 0.5      # 화음 안 프렛 폭 1당 비용
W_HEIGHT = 0.1    # 높은 포지션에 대한 약한 페널티
TOP_K = 40        # 화음마다 비용이 낮은 후보 K개만 남겨 계산량을 줄인다


def lowest_fret(song: Song) -> list[list[int]]:
    out = []
    for chord in song:
        pitches = [n.pitch for n in chord]
        cands = candidates(pitches)
        best = min(cands, key=lambda a: (sum(fret_of(p, s) for p, s in zip(pitches, a)), span(pitches, a)))
        out.append(list(best))
    return out


def viterbi_dp(song: Song) -> list[list[int]]:
    if not song:
        return []
    # layers[t] = [(배치, 손 위치, 누적 비용, 이전 인덱스), ...]
    layers = []
    prev_layer = None
    for chord in song:
        pitches = [n.pitch for n in chord]
        cands = candidates(pitches)
        local = []
        for a in cands:
            pos = hand_position(pitches, a, prev=0.0)
            local.append((a, W_SPAN * span(pitches, a) + W_HEIGHT * pos))
        local.sort(key=lambda x: x[1])
        local = local[:TOP_K]

        layer = []
        for a, c_local in local:
            if prev_layer is None:
                layer.append((a, hand_position(pitches, a, 0.0), c_local, -1))
                continue
            best = None
            for j, (_, ppos, pcost, _) in enumerate(prev_layer):
                pos = hand_position(pitches, a, prev=ppos)
                cost = pcost + c_local + W_MOVE * abs(pos - ppos)
                if best is None or cost < best[2]:
                    best = (a, pos, cost, j)
            layer.append(best)
        layers.append(layer)
        prev_layer = layer

    # 역추적
    idx = min(range(len(layers[-1])), key=lambda i: layers[-1][i][2])
    path = []
    for t in range(len(layers) - 1, -1, -1):
        a, _, _, j = layers[t][idx]
        path.append(list(a))
        idx = j
    return path[::-1]
