"""BiLSTM 줄 배정 모델 학습.

데이터 분할은 '연주자 기준'으로 한다: 연주자 0~3 학습, 4 검증, 5 테스트.
같은 연주자의 곡이 학습과 테스트에 섞이면 그 사람의 습관을 외워서 점수가 부풀려지기 때문이다.

사용법:
    python train.py --data data/guitarset --epochs 30
"""
import argparse
import os
import random

import numpy as np
import torch
import torch.nn as nn

from tabify.data import load_songs
from tabify.features import WindowDataset, collate
from tabify.metrics import evaluate
from tabify.model import TabNet
from tabify.predict import predict_song

TRAIN_PLAYERS, VAL_PLAYERS = [0, 1, 2, 3], [4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/guitarset")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--hidden", type=int, default=64)
    ap.add_argument("--out", default="checkpoints/tabnet.pt")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)

    train_songs = load_songs(args.data, TRAIN_PLAYERS)
    val_songs = load_songs(args.data, VAL_PLAYERS)
    train_ds = WindowDataset(train_songs)
    loader = torch.utils.data.DataLoader(train_ds, batch_size=args.batch, shuffle=True, collate_fn=collate)
    print(f"학습 곡 {len(train_songs)}개 / 검증 곡 {len(val_songs)}개 / 학습 조각 {len(train_ds)}개")

    config = {"hidden": args.hidden}
    model = TabNet(**config)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = nn.CrossEntropyLoss(ignore_index=-100)

    best = -1.0
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    for epoch in range(1, args.epochs + 1):
        model.train()
        total, count = 0.0, 0
        for P, F, Y in loader:
            logits = model(P, F)
            loss = loss_fn(logits.reshape(-1, 6), Y.reshape(-1))
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            total += loss.item() * P.size(0); count += P.size(0)

        model.eval()
        val = evaluate(val_songs, [predict_song(model, s) for s in val_songs])
        print(f"epoch {epoch:3d} | train loss {total / count:.4f} | val string_acc {val['string_acc']:.3f} "
              f"| playable {val['playable']:.3f}")
        if val["string_acc"] > best:
            best = val["string_acc"]
            torch.save({"config": config, "state_dict": model.state_dict()}, args.out)
    print(f"최고 검증 정확도 {best:.3f} → {args.out} 저장")


if __name__ == "__main__":
    main()
