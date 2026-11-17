"""테스트 연주자(5번)에 대해 기준선 2개와 학습 모델을 비교한다.

사용법:
    python evaluate.py --data data/guitarset --checkpoint checkpoints/tabnet.pt
"""
import argparse

from tabify.baseline import lowest_fret, viterbi_dp
from tabify.data import load_songs
from tabify.metrics import evaluate
from tabify.predict import load_model, predict_song

TEST_PLAYERS = [5]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/guitarset")
    ap.add_argument("--checkpoint", default="checkpoints/tabnet.pt")
    args = ap.parse_args()

    songs = load_songs(args.data, TEST_PLAYERS)
    model = load_model(args.checkpoint)
    methods = {
        "baseline: lowest fret": lambda s: lowest_fret(s),
        "baseline: Viterbi DP": lambda s: viterbi_dp(s),
        "BiLSTM (no constraint)": lambda s: predict_song(model, s, constrained=False),
        "BiLSTM + constrained": lambda s: predict_song(model, s, constrained=True),
    }
    print(f"테스트 곡 {len(songs)}개\n")
    print(f"| {'method':<24} | string_acc | chord_acc | playable | avg_move |")
    print(f"|{'-' * 26}|-----------:|----------:|---------:|---------:|")
    for name, fn in methods.items():
        r = evaluate(songs, [fn(s) for s in songs])
        print(f"| {name:<24} | {r['string_acc']:10.3f} | {r['chord_acc']:9.3f} | {r['playable']:8.3f} | {r['avg_move']:8.2f} |")


if __name__ == "__main__":
    main()
