"""피아노 악보를 기타 tab으로 변환한다.

사용법:
    python convert.py corpus:bach/bwv66.6                       # music21 내장 바흐 코랄
    python convert.py my_piano.mid --method dp                  # 학습 없이 DP 기준선으로
    python convert.py my_piano.musicxml --max-notes 3 --out tab.txt
    python convert.py my_piano.musicxml --transpose -12         # 멜로디가 너무 높으면 한 옥타브 내리기
    python convert.py my_piano.musicxml --musicxml tab.musicxml  # MuseScore용 TAB 악보(기타 소리)도 저장
"""
import argparse

from tabify.arrange import score_to_song
from tabify.baseline import viterbi_dp
from tabify.render import render_tab


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("score", help="MIDI/MusicXML 경로, 또는 corpus:이름")
    ap.add_argument("--method", choices=["model", "dp"], default="model")
    ap.add_argument("--checkpoint", default="checkpoints/tabnet.pt")
    ap.add_argument("--max-notes", type=int, default=4, help="화음당 최대 음 수 (기타는 최대 6)")
    ap.add_argument("--transpose", type=int, default=0, help="반음 단위 이동 (예: -12 = 한 옥타브 아래)")
    ap.add_argument("--out", default=None, help="텍스트 tab 저장 경로")
    ap.add_argument("--musicxml", default=None, help="TAB 보표 + 기타 음색 MusicXML 저장 경로 (MuseScore로 열기)")
    args = ap.parse_args()

    song = score_to_song(args.score, max_notes=args.max_notes, transpose=args.transpose)
    if args.method == "model":
        from tabify.predict import load_model, predict_song
        assignment = predict_song(load_model(args.checkpoint), song)
    else:
        assignment = viterbi_dp(song)

    tab = render_tab(song, assignment)
    print(tab)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(tab + "\n")
    if args.musicxml:
        from tabify.arrange import score_info
        from tabify.export import write_tab_musicxml
        measures, fifths, title = score_info(args.score)
        write_tab_musicxml(song, assignment, measures, args.musicxml, title=title, fifths=fifths)
        print(f"\nTAB 악보 저장: {args.musicxml}  (MuseScore로 열면 tab이 보이고 기타 소리로 재생됩니다)")


if __name__ == "__main__":
    main()
