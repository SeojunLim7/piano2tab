"""줄 배치 결과를 'TAB 보표 + 기타 음색' MusicXML로 저장한다.

MuseScore로 열면 기타 tab 악보가 원곡 박자대로 보이고, 재생하면 기타 소리가 난다.

MusicXML에서 tab을 표현하는 방법
- <clef><sign>TAB</sign>  + <staff-details>(6줄, 표준 튜닝)  → TAB 보표
- 음표마다 <technical><string>줄</string><fret>프렛</fret>  → 어느 줄 몇 프렛인지
  (MusicXML의 줄 번호는 1 = 가장 높은 e줄, 6 = 가장 낮은 E줄. 우리 코드의 0 = 낮은 E와 반대)
- <midi-program>25</midi-program>  → General MIDI 25번 = 어쿠스틱 기타(나일론)
"""
from __future__ import annotations

from xml.sax.saxutils import escape

from .arrange import SECONDS_PER_QUARTER
from .data import Song
from .guitar import TUNING, fret_of

DIV = 48   # 4분음표 하나를 48로 나눔 (셋잇단, 점32분음표까지 정수로 표현 가능)

# 표현 가능한 음표 길이(4분음표 = 1) → (MusicXML type, 점 개수)
NOTE_TYPES = [(4.0, "whole", 0), (3.0, "half", 1), (2.0, "half", 0), (1.5, "quarter", 1), (1.0, "quarter", 0),
              (0.75, "eighth", 1), (0.5, "eighth", 0), (0.375, "16th", 1), (0.25, "16th", 0),
              (0.1875, "32nd", 1), (0.125, "32nd", 0), (0.0625, "64th", 0)]

SHARP_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]


def split_duration(length: float) -> list[tuple[float, str, int]]:
    """길이를 표현 가능한 음표들의 합으로 쪼갠다 (예: 1.25 → 4분음표 + 16분음표, 붙임줄로 연결)."""
    parts, rest = [], round(length, 6)
    while rest > 1e-6:
        for ql, typ, dots in NOTE_TYPES:
            if ql <= rest + 1e-6:
                parts.append((ql, typ, dots))
                rest = round(rest - ql, 6)
                break
        else:   # 64분음표보다 짧은 자투리는 버림
            break
    return parts


def pitch_xml(midi: int, use_flats: bool) -> str:
    # 기타는 '적힌 음보다 한 옥타브 낮게 소리 나는' 악기라서, 악보에는 실제 음보다 한 옥타브 높게 적는다.
    # (이걸 안 하면 MuseScore가 모든 음을 한 옥타브 낮게 읽고 줄·프렛을 다시 계산해 버린다)
    written = midi + 12
    name = (FLAT_NAMES if use_flats else SHARP_NAMES)[written % 12]
    octave = written // 12 - 1
    alter = {"#": 1, "b": -1}.get(name[1:], 0)
    alter_xml = f"<alter>{alter}</alter>" if alter else ""
    return f"<pitch><step>{name[0]}</step>{alter_xml}<octave>{octave}</octave></pitch>"


def note_xml(midi, string, ql, typ, dots, in_chord, tie_start, tie_stop, use_flats) -> str:
    ties = ("<tie type=\"stop\"/>" if tie_stop else "") + ("<tie type=\"start\"/>" if tie_start else "")
    tieds = ("<tied type=\"stop\"/>" if tie_stop else "") + ("<tied type=\"start\"/>" if tie_start else "")
    return ("<note>" + ("<chord/>" if in_chord else "") + pitch_xml(midi, use_flats)
            + f"<duration>{round(ql * DIV)}</duration>{ties}<voice>1</voice><type>{typ}</type>" + "<dot/>" * dots
            + f"<notations>{tieds}<technical><string>{6 - string}</string><fret>{fret_of(midi, string)}</fret>"
            + "</technical></notations></note>")


def rest_xml(ql, typ, dots) -> str:
    return f"<note><rest/><duration>{round(ql * DIV)}</duration><voice>1</voice><type>{typ}</type>" + "<dot/>" * dots + "</note>"


def write_tab_musicxml(song: Song, assignment: list[list[int]], measures, path: str,
                       title: str = "Guitar Tab", fifths: int = 0, tempo: int = 80) -> None:
    """measures: [(시작 위치, 길이, (박자 분자, 분모)), ...]  — 단위는 4분음표 = 1."""
    use_flats = fifths < 0
    onsets = [round(ch[0].onset / SECONDS_PER_QUARTER, 6) for ch in song]
    song_end = measures[-1][0] + measures[-1][1]

    # 화음마다 '다음 화음까지'의 길이를 갖는다고 본다 (마지막 화음은 곡 끝까지)
    events = []
    for i, (chord, strings) in enumerate(zip(song, assignment)):
        end = onsets[i + 1] if i + 1 < len(song) else song_end
        events.append((onsets[i], end, [(n.pitch, s) for n, s in zip(chord, strings)]))

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
           '"http://www.musicxml.org/dtds/partwise.dtd">',
           '<score-partwise version="4.0">',
           f"<work><work-title>{escape(title)}</work-title></work>",
           '<part-list><score-part id="P1"><part-name>Guitar</part-name>'
           '<score-instrument id="P1-I1"><instrument-name>Acoustic Guitar (nylon)</instrument-name></score-instrument>'
           '<midi-instrument id="P1-I1"><midi-channel>1</midi-channel><midi-program>25</midi-program></midi-instrument>'
           '</score-part></part-list>', '<part id="P1">']

    first_len, first_ts = measures[0][1], measures[0][2]
    pickup = first_len < first_ts[0] * 4 / first_ts[1] - 1e-6     # 첫 마디가 못갖춘마디인가
    prev_ts = None
    for mi, (m_start, m_len, ts) in enumerate(measures):
        m_end = m_start + m_len
        implicit = ' implicit="yes"' if mi == 0 and pickup else ""
        out.append(f'<measure number="{mi if pickup else mi + 1}"{implicit}>')
        attrs = ""
        if mi == 0:
            tuning = "".join(
                f'<staff-tuning line="{k + 1}"><tuning-step>{SHARP_NAMES[p % 12][0]}</tuning-step>'
                f"<tuning-octave>{p // 12 - 1}</tuning-octave></staff-tuning>" for k, p in enumerate(TUNING))
            attrs += (f"<divisions>{DIV}</divisions><key><fifths>{fifths}</fifths></key>")
        if ts != prev_ts:
            attrs += f"<time><beats>{ts[0]}</beats><beat-type>{ts[1]}</beat-type></time>"
        if mi == 0:
            attrs += f'<clef><sign>TAB</sign><line>5</line></clef><staff-details><staff-lines>6</staff-lines>{tuning}</staff-details>'
        if attrs:
            out.append(f"<attributes>{attrs}</attributes>")
        if mi == 0:
            out.append(f'<direction placement="above"><direction-type><metronome><beat-unit>quarter</beat-unit>'
                       f'<per-minute>{tempo}</per-minute></metronome></direction-type><sound tempo="{tempo}"/></direction>')
        prev_ts = ts

        # 이 마디에 걸치는 이벤트들을 시간순으로 채운다 (빈 곳은 쉼표)
        cursor = m_start
        for start, end, notes in events:
            seg_start, seg_end = max(start, m_start), min(end, m_end)
            if seg_end - seg_start <= 1e-6:
                continue
            if seg_start - cursor > 1e-6:
                out += [rest_xml(*p) for p in split_duration(seg_start - cursor)]
            pieces = split_duration(seg_end - seg_start)
            for pi, (ql, typ, dots) in enumerate(pieces):
                tie_stop = pi > 0 or start < m_start - 1e-6
                tie_start = pi < len(pieces) - 1 or end > m_end + 1e-6
                for ni, (midi, s) in enumerate(notes):
                    out.append(note_xml(midi, s, ql, typ, dots, ni > 0, tie_start, tie_stop, use_flats))
            cursor = seg_end
        if m_end - cursor > 1e-6:
            out += [rest_xml(*p) for p in split_duration(m_end - cursor)]
        out.append("</measure>")

    out += ["</part>", "</score-partwise>"]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
