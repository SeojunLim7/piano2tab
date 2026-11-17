"""화음 시퀀스(Song)를 모델 입력 텐서로 바꾼다.

음 하나 = 시퀀스의 한 칸. 화음은 낮은 음부터 차례로 펼친다.
각 칸의 입력:
  - pitch_idx : 음높이(40~84)를 0~44 정수로 → 임베딩
  - feats     : [시간 간격, 화음 크기, 화음 안 순서, 직전 음과의 음정, 칠 수 있는 줄 마스크 6개]  (총 10차원)
정답: 줄 번호(0~5)
"""
from __future__ import annotations

import math

import numpy as np
import torch

from .data import Song
from .guitar import HIGHEST, LOWEST, valid_mask

NUM_PITCH = HIGHEST - LOWEST + 1   # 45
FEAT_DIM = 10


def song_to_arrays(song: Song):
    pitch_idx, feats, labels, chord_id = [], [], [], []
    prev_onset, prev_pitch = None, None
    for ci, chord in enumerate(song):
        dt = 0.0 if prev_onset is None else chord[0].onset - prev_onset
        for k, n in enumerate(chord):
            interval = 0.0 if prev_pitch is None else (n.pitch - prev_pitch) / 12.0
            pitch_idx.append(min(max(n.pitch - LOWEST, 0), NUM_PITCH - 1))
            feats.append([
                math.log1p(max(dt, 0.0)) if k == 0 else 0.0,
                len(chord) / 6.0,
                k / max(len(chord) - 1, 1),
                max(min(interval, 2.0), -2.0),
                *valid_mask(n.pitch),
            ])
            labels.append(-100 if n.string is None else n.string)   # -100 = 손실 계산에서 무시
            chord_id.append(ci)
            prev_pitch = n.pitch
        prev_onset = chord[0].onset
    return (np.array(pitch_idx, dtype=np.int64), np.array(feats, dtype=np.float32),
            np.array(labels, dtype=np.int64), np.array(chord_id, dtype=np.int64))


class WindowDataset(torch.utils.data.Dataset):
    """긴 곡을 길이 win짜리 조각으로 잘라 학습 샘플로 쓴다 (절반씩 겹치게)."""

    def __init__(self, songs: list[Song], win: int = 64):
        self.items = []
        for song in songs:
            p, f, y, _ = song_to_arrays(song)
            step = win // 2
            for start in range(0, max(len(p) - win, 0) + 1, step):
                sl = slice(start, start + win)
                self.items.append((p[sl], f[sl], y[sl]))

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]


def collate(batch):
    """길이가 다른 조각들을 패딩해서 한 배치로 만든다."""
    L = max(len(p) for p, _, _ in batch)
    P = torch.zeros(len(batch), L, dtype=torch.long)
    F = torch.zeros(len(batch), L, FEAT_DIM)
    Y = torch.full((len(batch), L), -100, dtype=torch.long)
    for i, (p, f, y) in enumerate(batch):
        n = len(p)
        P[i, :n] = torch.from_numpy(p)
        F[i, :n] = torch.from_numpy(f)
        Y[i, :n] = torch.from_numpy(y)
    return P, F, Y
