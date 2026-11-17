"""악보 파일이 music21 안에서 어떻게 생겼는지 들여다보는 스크립트.

사용법:
    python scripts/inspect_score.py corpus:bach/bwv66.6        # music21 내장 바흐 코랄
    python scripts/inspect_score.py 내곡.musicxml --measures 4  # 내 악보 파일
"""
import argparse
from collections import defaultdict

from music21 import converter, corpus


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("score")
    ap.add_argument("--measures", type=int, default=2, help="파트별로 보여줄 마디 수")
    args = ap.parse_args()

    # 1) 악보 불러오기: 'corpus:'로 시작하면 music21 내장 악보, 아니면 파일 경로
    if args.score.startswith("corpus:"):
        score = corpus.parse(args.score[len("corpus:"):])
    else:
        score = converter.parse(args.score)

    # 2) 곡 전체 정보: 파트(성부/손) 이름, 박자, 조성, 마디 수
    first_part = score.parts[0]
    ts = first_part.recurse().getElementsByClass("TimeSignature")
    print("파트:", [p.partName for p in score.parts])
    print("박자:", ts[0].ratioString if ts else "?")
    print("조성(추정):", score.analyze("key"))
    print("마디 수:", len(first_part.getElementsByClass("Measure")))

    # 3) 파트별로 앞쪽 마디의 음표 출력
    #    p.measure(k): k번째 마디 / m.notes: 그 마디의 음표와 화음
    for p in score.parts:
        print(f"\n[{p.partName}]")
        for k in range(1, args.measures + 1):
            m = p.measure(k)
            if m is None:
                continue
            items = []
            for n in m.notes:
                if n.isChord:   # 화음이면 구성음을 모두
                    name = "+".join(x.nameWithOctave for x in n.pitches)
                    midi = [x.midi for x in n.pitches]
                else:           # 단음
                    name, midi = n.nameWithOctave, n.pitch.midi
                items.append(f"{name}({midi}) @박{float(n.offset)} 길이{float(n.quarterLength)}")
            print(f"  마디 {k}: " + ", ".join(items))

    # 4) piano2tab이 실제로 쓰는 형태: 파트 구분 없이, 같은 시점의 음을 한 화음으로
    #    flatten(): 모든 파트를 한 줄로 펼치고, offset을 '곡 시작부터의 박'으로 바꿔 준다
    by_offset = defaultdict(list)
    for el in score.flatten().notes:
        pitches = el.pitches if el.isChord else [el.pitch]
        by_offset[float(el.offset)].extend(x.midi for x in pitches)
    print("\n[piano2tab 입력 형태: 시점(박) → MIDI 음높이]")
    for off in sorted(by_offset)[:12]:
        print(f"  {off:6.2f} → {sorted(by_offset[off])}")


if __name__ == "__main__":
    main()
