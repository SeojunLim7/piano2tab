"""쇼팽 녹턴 Op.9 No.2 (1832, 퍼블릭 도메인) 못갖춘마디 + 1~4마디를 music21로 직접 입력해 MusicXML로 저장한다.

- 오른손: 악보의 멜로디 그대로 (턴·꾸밈음 같은 장식음은 생략)
- 왼손: '베이스 → 2음 → 3음' 반주 패턴을 박마다 그 박의 화음으로 단순화
  (piano2tab은 음높이와 시작 시점만 쓰므로, 이 정도 단순화로 충분하다)

    python examples/make_nocturne.py
"""
import os

from music21 import chord, clef, key, metadata, meter, note, stream

E = 0.5  # 8분음표 길이 (4분음표 = 1)

# ── 오른손: (음, 길이). 'r' = 쉼표. 음이름의 '-'는 플랫 (E-5 = 미♭5)
RH = {
    0: [("B-4", 0.5)],
    1: [("G5", 1.5), ("G5", E), ("F5", E), ("G5", E), ("F5", 1.5), ("E-5", 1.0), ("B-4", E)],
    2: [("G5", 1.0), ("E5", E), ("C6", 1.0), ("G5", E), ("B-5", 1.5), ("A-5", 1.0), ("G5", E)],
    3: [("F5", 1.5), ("G5", 1.0), ("D5", E), ("E-5", 1.5), ("C5", 1.5)],
    4: [("B-4", E), ("D6", E), ("C6", E), ("B-5", .25), ("A-5", .25), ("G5", .25), ("A-5", .25),
        ("C5", .25), ("D5", .25), ("E-5", 1.5), ("r", 1.0), ("B-4", E)],
}

# ── 왼손: 박(점4분음표)마다 (베이스, 2음, 3음), 각각 8분음표
LH = {
    1: [("E-2", "G3 E-4", "B-3 E-4 G4"),     # E♭
        ("E-3", "G3 D-4", "B-3 D-4 G4"),     # E♭7
        ("E-2", "G3 E-4", "B-3 E-4 G4"),
        ("E-2", "G3 E-4", "B-3 E-4 G4")],
    2: [("C2", "G3 E4", "B-3 E4 G4"),        # C7
        ("C3", "G3 E4", "B-3 E4 G4"),
        ("F2", "B-3 D-4", "B-3 D-4 F4"),     # B♭m/F
        ("F2", "A-3 C4", "A-3 C4 F4")],      # Fm
    3: [("B-2", "F3 D4", "B-3 D4 F4"),       # B♭
        ("B2", "G3 F4", "G3 D4 F4"),         # G7/B
        ("C3", "G3 E-4", "G3 C4 E-4"),       # Cm
        ("A2", "G-3 E-4", "C4 E-4 G-4")],    # A°7
    4: [("B-2", "F3 D4", "B-3 D4 F4"),       # B♭
        ("B-1", "F3 A-3", "A-3 D4 F4"),      # B♭7
        ("E-2", "G3 E-4", "B-3 E-4 G4"),     # E♭
        ("E-3", "G3 E-4", "B-3 E-4 G4")],
}


def make_part(name, measures, filler):
    part = stream.Part()
    part.partName = name
    for num in sorted(measures):
        m = stream.Measure(number=num)
        if num == 0:
            m.append(clef.BassClef() if name == "Left hand" else clef.TrebleClef())
            m.append(key.KeySignature(-3))          # 플랫 3개 = E♭장조
            m.append(meter.TimeSignature("12/8"))
        for el in filler(measures[num]):
            m.append(el)
        if num == 0:
            m.paddingLeft = 6.0 - m.highestTime    # 못갖춘마디
        part.append(m)
    return part


def rh_elements(items):
    return [note.Rest(quarterLength=d) if p == "r" else note.Note(p, quarterLength=d) for p, d in items]


def lh_elements(beats):
    out = []
    for bass, dyad, triad in beats:
        out += [note.Note(bass, quarterLength=E), chord.Chord(dyad.split(), quarterLength=E),
                chord.Chord(triad.split(), quarterLength=E)]
    return out


def main():
    lh = {0: [], **LH}
    score = stream.Score()
    score.metadata = metadata.Metadata(title="Nocturne Op.9 No.2 m.1-4 (Chopin) - guitar tab")
    score.insert(0, make_part("Right hand", RH, rh_elements))
    left = make_part("Left hand", lh, lh_elements)
    left.measure(0).append(note.Rest(quarterLength=E))
    score.insert(0, left)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nocturne_op9no2_m1-4.musicxml")
    score.write("musicxml", fp=out)
    print("저장:", out)


if __name__ == "__main__":
    main()
