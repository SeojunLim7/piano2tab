"""기타의 기본 상수와 '이 음을 어느 줄에서 칠 수 있나' 계산.

줄 번호 규칙 (GuitarSet과 동일):
    0 = 6번줄(낮은 E), 1 = A, 2 = D, 3 = G, 4 = B, 5 = 1번줄(높은 e)
"""

TUNING = [40, 45, 50, 55, 59, 64]   # 표준 튜닝 개방현의 MIDI 음높이 (E2 A2 D3 G3 B3 E4)
NUM_STRINGS = 6
MAX_FRET = 20
LOWEST = TUNING[0]                  # 40 (E2)
HIGHEST = TUNING[-1] + MAX_FRET     # 84 (C6)
STRING_NAMES = ["E", "A", "D", "G", "B", "e"]


def fret_of(pitch: int, string: int) -> int:
    """pitch를 string에서 칠 때의 프렛 번호. fret = pitch - 개방현 음높이."""
    return pitch - TUNING[string]


def valid_strings(pitch: int) -> list[int]:
    """pitch를 낼 수 있는 줄 목록 (0 <= fret <= MAX_FRET)."""
    return [s for s in range(NUM_STRINGS) if 0 <= fret_of(pitch, s) <= MAX_FRET]


def valid_mask(pitch: int) -> list[float]:
    """모델 입력용 0/1 마스크 (길이 6)."""
    ok = set(valid_strings(pitch))
    return [1.0 if s in ok else 0.0 for s in range(NUM_STRINGS)]
