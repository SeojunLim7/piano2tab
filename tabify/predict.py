"""학습된 모델로 곡 하나의 줄 배치를 예측한다 (모델 확률 + 규칙 기반 화음 디코딩)."""
from __future__ import annotations

import numpy as np
import torch

from .data import Song
from .decode import constrained_decode
from .features import song_to_arrays
from .model import TabNet


def load_model(path: str) -> TabNet:
    ckpt = torch.load(path, map_location="cpu")
    model = TabNet(**ckpt["config"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    return model


@torch.no_grad()
def predict_song(model: TabNet, song: Song, constrained: bool = True) -> list[list[int]]:
    if not song:
        return []
    p, f, _, chord_id = song_to_arrays(song)
    logits = model(torch.from_numpy(p)[None], torch.from_numpy(f)[None])[0]
    logp = torch.log_softmax(logits, dim=-1).numpy()
    out = []
    for ci, chord in enumerate(song):
        rows = logp[chord_id == ci]
        pitches = [n.pitch for n in chord]
        if constrained:
            out.append(list(constrained_decode(pitches, rows)))
        else:
            out.append([int(np.argmax(r)) for r in rows])
    return out
