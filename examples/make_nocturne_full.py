"""쇼팽 녹턴 Op.9 No.2 (1832, 퍼블릭 도메인) 전곡(못갖춘마디 + 1~37마디)을 music21로 입력해 MusicXML로 저장한다.

입력 원칙 (piano2tab은 '음높이 + 시작 시점'만 쓰므로 이 정도 단순화로 충분하다)
- 오른손: 멜로디의 주요 음은 악보대로. 트릴·턴·꾸밈음은 생략하고, 빠른 장식 런은 비슷한 음형으로 단순화.
- 왼손: '베이스 → 2음 → 3음' 반주를 박마다 그 박의 화음으로 단순화.
- 32~35마디 카덴차(senza tempo)는 반복 음형과 하강 런을 짧게 정리. 8va 구간은 적힌 음 그대로 입력.

    python examples/make_nocturne_full.py
"""
import os

from music21 import chord, clef, key, metadata, meter, note, stream

# ───────────────────────── 오른손: 마디 → [(음 또는 "음 음" 화음 또는 "r", 길이)]
q = lambda notes, d: [(n, d) for n in notes.split(",")]     # 같은 길이 음들을 한 번에

M1 = [("G5", 1.5), ("G5", .5), ("F5", .5), ("G5", .5), ("F5", 1.5), ("E-5", 1.0), ("B-4", .5)]
M2 = [("G5", 1.0), ("E5", .5), ("C6", 1.0), ("G5", .5), ("B-5", 1.5), ("A-5", 1.0), ("G5", .5)]
M3 = [("F5", 1.5), ("G5", 1.0), ("D5", .5), ("E-5", 1.5), ("C5", 1.5)]
M4 = [("B-4", .5), ("D6", .5), ("C6", .5), *q("B-5,A-5,G5,A-5,C5,D5", .25), ("E-5", 1.5), ("r", 1.0), ("B-4", .5)]
M5 = [("G5", 1.5), *q("F5,G5,F5,E5,F5,G5", .25), ("G5", .5), ("E-5", 1.0), *q("E-5,F5,E-5,D5,E-5,F5", .25)]
M6 = [*q("G5,B4,C5,D-5,C5,F5", .25), *q("E5,A-5,G5,D-6,C6,G5", .25), ("B-5", 1.5), ("A-5", 1.0), ("G5", .5)]
M7 = [("F5", 1.5), ("G5", 1.0), ("D5", .5), ("E-5", 1.5), ("C5", 1.5)]
M8 = [("B-4", .5), ("D6", .5), ("C6", .5), *q("B-5,A-5,G5,A-5,C5,D5", .25), ("E-5", 1.5), *q("E-5,D5,E-5", .5)]
M9 = [("F5", 1.5), ("G5", 1.0), ("F5", .5), ("F5", 1.5), ("C5", 1.5)]
M10 = [*q("E-5,E-5,E-5", .5), ("E-5", .5), *q("D5,E-5,F5,E-5", .25), ("E-5", 1.5), ("B-4", 1.5)]
M11 = [("B-5", 1.5), ("A5", 1.5), ("A4 F5", 1.5), ("B-4 D5", 1.5)]
M12 = [("G4 E-5", 1.5), *q("A4 D5,A4 D5,A4 D5", .5), *q("F4 B-4,F#4 B4,E4 B-4", .5),
       *q("E-4 B-4 C5,F4 A4 C5,F4 A-4 D5", .5)]
M13 = [("A4", .25), ("B-4", .25), ("C-5", .5), ("B-4", .25), ("C#5", .25), ("D5", .25), ("G5", .75), ("F5", .5),
       ("F5", 1.0), ("E-5", .5), *q("E-5,F5,E-5,D5,E-5,F5", .25)]
M16 = [("B-4", .5), ("D-6", .5), ("C6", .5), *q("C6,B5,B-5,A5,A-5,G5,F5,D5,C-5,B-4,D5,F5", .125),
       ("E-5", 1.5), *q("E-5,D5,E-5", .5)]
M19 = [("B-5", 1.5), ("A5", 1.0), ("G5", .5), ("A4 F5", 1.5), ("B-4 D5", 1.5)]
M24 = [("B-4", .25), ("D6", .5), ("C#6", .25), ("C6", .25), ("B5", .25), *q("B-5,A5,A-5,A4,B-4,C5", .25),
       *q("D5,E-5,E5,F5,G5,F5", .25), ("E-5", 1.5)]
M25 = [("E-5", 1.5), *q("F5,E-5,F5", .5), ("G5", 3.0)]
M26 = [("E-5", 1.5), *q("E-5,F5,E-5,F5,E-5,F5", .25), ("G5", 1.0), ("E-5", .5), *q("E-6,D6,C6", .5)]
M27 = [("B-5", 1.0), ("A5", .5), *q("A-5,C5,D5", .5), ("E-5", .5), *q("F5,E-5,D5,E-5", .25),
       ("E-6", .5), *q("D6,C6,B-5,A-5", .25)]
M28 = [*q("C-6,B-5,A5", .5), *q("B-5,A-5,A-5,G5,G5,F5", .25), ("E-5", 3.0)]
M29 = [("E-5", 1.5), *q("E-5,F5,E-5,F5,E-5,F5,E-5,F5", .1875), ("E-5", 3.0)]
M30 = [("E-5", .5), *q("A-4,B-4,A-4,G4", .25), *q("A-4,C-5,E-5,A-5", .25), ("C6", .5),
       *q("D6,E-6", .25), ("E-5 E-6", 1.0), ("D5 D6", 1.0), ("C5 C6", .5)]
M31 = [*q("C-5 C-6,B-4 B-5,A4 A5", .5), *q("A-4 A-5,G4 G5,E-4 E-5", .5), ("E-5 E-6", 1.5),
       ("F4 F5", .5), ("C5 C6", 1.0)]
M32 = [("C-5 A-5", 3.0), ("B-4 B-5", 3.0)]
M33 = q(",".join(["C-6,B-5,C6,A-5"] * 6), .25)
M35 = q("C-6,B-5,D-6,C6,B5,B-5,A5,A-5,G5,F5,E-5,D5,C5,B-4,A-4,D4", .125)
M36 = q(",".join(["G4 E-5,B-4,G5"] * 4), .5)
M37 = [("G4 E-5", 1.5), ("G5 E-6", 1.5), ("B-3 E-4 G4", 3.0)]

RH = {0: [("B-4", .5)], 1: M1, 2: M2, 3: M3, 4: M4, 5: M5, 6: M6, 7: M7, 8: M8, 9: M9, 10: M10, 11: M11,
      12: M12, 13: M13, 14: M6, 15: M7, 16: M16, 17: M9, 18: M10, 19: M19, 20: M12, 21: M13, 22: M6,
      23: M7, 24: M24, 25: M25, 26: M26, 27: M27, 28: M28, 29: M29, 30: M30, 31: M31, 32: M32,
      33: M33, 34: M33, 35: M35, 36: M36, 37: M37}

# ───────────────────────── 왼손: 박마다 (베이스, 2음, 3음) 패턴, 또는 RH와 같은 형식의 직접 목록
L1 = [("E-2", "G3 E-4", "B-3 E-4 G4"), ("E-3", "G3 D-4", "B-3 D-4 G4"),
      ("E-2", "G3 E-4", "B-3 E-4 G4"), ("E-2", "G3 E-4", "B-3 E-4 G4")]                 # E♭ – E♭7
L2 = [("C2", "G3 E4", "B-3 E4 G4"), ("C3", "G3 E4", "B-3 E4 G4"),
      ("F2", "B-3 D-4", "B-3 D-4 F4"), ("F2", "A-3 C4", "A-3 C4 F4")]                   # C7 – B♭m/F – Fm
L3 = [("B-2", "F3 D4", "B-3 D4 F4"), ("B2", "G3 F4", "G3 D4 F4"),
      ("C3", "G3 E-4", "G3 C4 E-4"), ("A2", "G-3 E-4", "C4 E-4 G-4")]                   # B♭ – G7/B – Cm – A°7
L4 = [("B-2", "F3 D4", "B-3 D4 F4"), ("B-1", "F3 A-3", "A-3 D4 F4"),
      ("E-2", "G3 E-4", "B-3 E-4 G4"), ("E-3", "G3 E-4", "B-3 E-4 G4")]                 # B♭7 – E♭
L5 = [("E-3", "B-3 E-4", "B-3 E-4 G4"), ("E-3", "B-3 D-4", "B-3 D-4 G4"),
      ("E-3", "B-3 E-4", "B-3 E-4 G4"), ("D3", "B-3 F4", "B-3 D4 F4")]                  # E♭ – E♭7 – B♭/D
L9 = [("B-2", "F3 D4", "A-3 D4 F4")] * 2 + [("A2", "F3 E-4", "C4 E-4 F4")] * 2          # B♭7 – F7/A
L10 = [("A-2", "E-3 C4", "A-3 C4 E-4"), ("E-2", "G3 D-4", "B-3 D-4 G4"),
       ("E-2", "G3 E-4", "B-3 E-4 G4"), ("E-3", "G3 E-4", "B-3 E-4 G4")]                # A♭ – E♭7 – E♭
L11 = [("E2", "G3 B-3", "B-3 C4 G4"), ("E2", "G3 C4", "B-3 C4 E4"),
       ("F2", "A3 C4", "A3 C4 F4"), ("G2", "B3 F4", "B3 D4 F4")]                        # C7/E – F – G7
L12 = q("C2,G3 E-4,C4 E-4 G4,F2,C4 E-4,A3 C4 E-4,B-3 D4,A3 C#4,G#3 B3,B-2,A-3 D4,A-3 D4 F4", .5)
L25 = [("C2", "A-3 C4", "A-3 C4 F4"), ("E-3", "A-3 C4", "A-3 C4 F4"),
       ("C2", "G3 C4", "G3 C4 E-4"), ("E-3", "G3 C4", "G3 C4 E-4")]                     # Fm/C – Cm
L27 = [("E-3", "F3 A-3", "A-3 D4 F4")] * 2 + [("E-3", "G3 E-4", "B-3 E-4 G4"), ("A2", "F3 E-4", "C4 E-4 F4")]
L29 = [("C2", "A-3 C4", "A-3 C4 F4"), ("F2", "A-3 C4", "A-3 C4 F4"),
       ("E-2", "G3 E-4", "B-3 E-4 G4"), ("E-3", "G3 E-4", "B-3 E-4 G4")]
L30 = q("A-1,E-3 A-3,A-3 C4 E-4,A-3 C4 E-4,A-3 C4 E-4,F3 A-3 C4,E-2,G3 E-4,B-3 E-4 G4,A2,F3 C4,A3 C4 E-4", .5)
L32 = [*q("B-1,F2,D3,A-3,F3,D4,A-4,F4", .375), ("D4 A-4", 3.0)]
L36 = q("E-2,B-3,B-2,E-3,G3,B-2,E-2,B-3,B-2,E-3,G3,B-2", .5)
L37 = [("E-3 G3 B-3", 1.5), ("B-3 E-4 G4", 1.5), ("E-2 B-2", 3.0)]

LH = {0: [("r", .5)], 1: L1, 2: L2, 3: L3, 4: L4, 5: L5, 6: L2, 7: L3, 8: L4, 9: L9, 10: L10, 11: L11,
      12: L12, 13: L5, 14: L2, 15: L3, 16: L4, 17: L9, 18: L10, 19: L11, 20: L12, 21: L1, 22: L2, 23: L3,
      24: L4, 25: L25, 26: L25, 27: L27, 28: L4, 29: L29, 30: L30, 31: L3, 32: L32,
      33: [("r", 6.0)], 34: [("r", 6.0)], 35: [("r", 2.0)], 36: L36, 37: L37}

TIME_SIG = {0: "12/8", 35: "2/4", 36: "12/8"}
BAR_LEN = {0: .5, 35: 2.0}            # 그 외 마디는 12/8 = 6.0 (4분음표 기준)


def expand(items):
    """패턴(베이스, 2음, 3음)이면 8분음표 셋으로 펼치고, 직접 목록이면 그대로."""
    if items and len(items[0]) == 3:
        return [(x, .5) for beat in items for x in beat]
    return items


def element(pitches, dur):
    if pitches == "r":
        return note.Rest(quarterLength=dur)
    ps = pitches.split()
    return note.Note(ps[0], quarterLength=dur) if len(ps) == 1 else chord.Chord(ps, quarterLength=dur)


def make_part(name, measures):
    part = stream.Part()
    part.partName = name
    for num in sorted(measures):
        items = expand(measures[num])
        total = sum(d for _, d in items)
        assert abs(total - BAR_LEN.get(num, 6.0)) < 1e-9, f"{name} {num}마디 길이 {total}"
        m = stream.Measure(number=num)
        if num == 0:
            m.append(clef.BassClef() if name == "Left hand" else clef.TrebleClef())
            m.append(key.KeySignature(-3))    # 플랫 3개 = E♭장조
        if num in TIME_SIG:
            m.append(meter.TimeSignature(TIME_SIG[num]))
        for p, d in items:
            m.append(element(p, d))
        if num == 0:
            m.paddingLeft = 6.0 - total       # 못갖춘마디
        part.append(m)
    return part


def main():
    score = stream.Score()
    score.metadata = metadata.Metadata(title="Nocturne Op.9 No.2 (Chopin) - guitar tab")
    score.insert(0, make_part("Right hand", RH))
    score.insert(0, make_part("Left hand", LH))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nocturne_op9no2_full.musicxml")
    score.write("musicxml", fp=out)
    print("저장:", out)


if __name__ == "__main__":
    main()
