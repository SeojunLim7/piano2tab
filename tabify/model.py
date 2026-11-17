"""줄 배정 모델: 양방향 LSTM(BiLSTM).

왜 양방향인가? 사람은 다음에 칠 음까지 보고 지금 손 위치를 정한다. BiLSTM은 앞뒤 문맥을 모두 본다.
마지막에 '칠 수 없는 줄'의 점수를 아주 작게 만들어(마스킹) 불가능한 답을 내지 않게 한다.
"""
from __future__ import annotations

import torch
import torch.nn as nn

from .features import FEAT_DIM, NUM_PITCH


class TabNet(nn.Module):
    def __init__(self, emb: int = 32, hidden: int = 64, layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.embed = nn.Embedding(NUM_PITCH, emb)
        self.proj = nn.Linear(emb + FEAT_DIM, hidden)
        self.lstm = nn.LSTM(hidden, hidden, num_layers=layers, batch_first=True,
                            bidirectional=True, dropout=dropout)
        self.head = nn.Linear(2 * hidden, 6)

    def forward(self, pitch_idx, feats):
        x = torch.cat([self.embed(pitch_idx), feats], dim=-1)
        x = torch.relu(self.proj(x))
        h, _ = self.lstm(x)
        logits = self.head(h)
        mask = feats[..., -6:]                       # 칠 수 있는 줄 마스크
        return logits.masked_fill(mask == 0, -1e4)
