"""실제 데이터 없이 코드가 끝까지 돌아가는지 확인하기 위한 가짜 GuitarSet.
GuitarSet과 같은 JAMS 형식으로, 무작위 음 + DP 기준선이 고른 줄을 정답으로 저장한다.
(점수는 의미 없음. 파이프라인 동작 확인용.)

    python tests/make_fake_guitarset.py && python train.py --data data/fake --epochs 2
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tabify.baseline import viterbi_dp  # noqa: E402
from tabify.data import Note  # noqa: E402

OUT = os.path.join("data", "fake")


def random_song(n_chords=120):
    song, t, p = [], 0.0, random.randint(45, 70)
    for _ in range(n_chords):
        p = min(max(p + random.randint(-4, 4), 40), 80)
        size = random.choice([1, 1, 1, 2, 3])
        pitches = sorted({p - random.choice([0, 3, 4, 7, 12]) * (i > 0) for i in range(size)})
        pitches = [x for x in pitches if 40 <= x <= 84]
        song.append([Note(t, x, None) for x in pitches])
        t += random.choice([0.25, 0.5])
    return song


def main():
    random.seed(0)
    os.makedirs(OUT, exist_ok=True)
    for player in range(6):
        for k in range(4):
            song = random_song()
            strings = viterbi_dp(song)
            per_string = {s: [] for s in range(6)}
            for chord, ss in zip(song, strings):
                for n, s in zip(chord, ss):
                    per_string[s].append({"time": n.onset, "duration": 0.2, "value": float(n.pitch), "confidence": None})
            jam = {"annotations": [
                {"namespace": "note_midi", "annotation_metadata": {"data_source": str(s)}, "data": per_string[s]}
                for s in range(6)]}
            with open(os.path.join(OUT, f"{player:02d}_fake{k}_comp.jams"), "w") as f:
                json.dump(jam, f)
    print("가짜 데이터 생성:", OUT)


if __name__ == "__main__":
    main()
