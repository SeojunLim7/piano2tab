# piano2tab — 피아노 악보를 기타 tab으로

피아노 악보(MIDI/MusicXML)를 받아 **기타로 칠 수 있는 tab**으로 바꾸는 프로젝트입니다.
실제 기타 연주자의 운지 데이터(GuitarSet)로 "이 음을 어느 줄에서 칠까"를 학습합니다.

## 1. 문제 정의

기타에서는 같은 음을 여러 자리에서 낼 수 있습니다. 예를 들어 E4(MIDI 64)는
1번줄 개방현, 2번줄 5프렛, 3번줄 9프렛, 4번줄 14프렛, 5번줄 19프렛에서 모두 납니다.
줄이 정해지면 프렛은 자동으로 정해지므로(`fret = pitch − 개방현 음높이`),
핵심 문제는 **음마다 6개 줄 중 하나를 고르는 분류 문제**입니다.

좋은 배치의 조건:
- 한 화음 안에서 같은 줄을 두 번 쓸 수 없다
- 누르는 프렛의 폭이 손가락이 닿는 범위(≤ 4프렛)여야 한다
- 앞뒤 화음 사이 손 이동이 적을수록 편하다

## 2. 파이프라인

```
피아노 악보 ──(1) 편곡: 음역 접기 + 음 수 줄이기──▶ 기타 음 시퀀스
           ──(2) 줄 배정: BiLSTM + 규칙 기반 디코딩──▶ 줄/프렛
           ──(3) 출력──▶ 텍스트 tab
```

1. **편곡 (`tabify/arrange.py`, 규칙 기반)** — 기타 음역(E2~C6) 밖의 음은 옥타브를 옮기고,
   화음이 너무 크면 멜로디(최고음)와 베이스(최저음)를 우선 남긴다.
2. **줄 배정 (`tabify/model.py`, `tabify/decode.py`)** — 양방향 LSTM이 앞뒤 문맥을 보고 음마다 줄 확률을 낸다.
   그다음 "같은 줄 중복 금지, 프렛 폭 ≤ 4" 규칙을 지키는 배치 중 확률이 가장 높은 것을 고른다.
3. **출력 (`tabify/render.py`)**

## 3. 데이터

[GuitarSet](https://guitarset.weebly.com/) (Xi et al., ISMIR 2018, CC BY 4.0) — 연주자 6명, 360개 발췌.
줄마다 따로 녹음(헥사포닉 픽업)해서, 각 음을 **어느 줄에서 쳤는지**가 주석으로 들어 있습니다.
이 프로젝트는 오디오 없이 주석(JAMS)만 사용합니다.

**연주자 기준 분할**: 연주자 0~3 학습 / 4 검증 / 5 테스트.
같은 연주자의 곡이 학습과 테스트에 섞이면 그 사람의 습관을 외워 점수가 부풀려지기 때문입니다.

## 4. 비교 대상

| 방법 | 설명 |
|---|---|
| lowest fret | 음마다 가장 낮은 프렛 (가장 단순한 규칙) |
| Viterbi DP | 손 이동 + 화음 폭 비용의 합이 최소인 경로를 동적계획법으로 탐색 (학습 없음) |
| BiLSTM | 학습 모델, 음마다 독립적으로 argmax |
| BiLSTM + constrained | 학습 모델 + 화음 단위 규칙 디코딩 |

평가 지표: `string_acc`(사람과 같은 줄 비율), `chord_acc`(화음 전체 일치), `playable`(칠 수 있는 화음 비율), `avg_move`(평균 손 이동, 프렛)

## 5. 결과

테스트 연주자(5번) 기준, `python evaluate.py` 출력:

| method | string_acc | chord_acc | playable | avg_move |
|---|---:|---:|---:|---:|
| baseline: lowest fret | 0.481 | 0.441 | 0.999 | 1.21 |
| baseline: Viterbi DP | 0.592 | 0.540 | 0.999 | 0.82 |
| BiLSTM (no constraint) | 0.781 | 0.738 | 0.970 | 1.24 |
| **BiLSTM + constrained** | **0.792** | **0.756** | **0.999** | 1.25 |

**해석**
- 학습 모델(BiLSTM + constrained)은 테스트 연주자의 줄 선택을 79.2% 재현해, 손 이동 비용을 최소화하는 Viterbi DP(59.2%)보다 20%p 높았다.
- 그러나 손 이동량은 DP가 가장 작았다(0.82 vs 1.25 프렛). 실제 연주자는 손 이동 최소화만으로 운지를 정하지 않으며, 그 선호를 데이터로부터 학습할 수 있음을 보여준다.
- 화음 단위 규칙 디코딩은 정확도를 유지(+1.1%p)하면서 칠 수 없는 화음의 비율을 3.0%에서 0.1%로 줄였다. 학습은 '선호'를, 규칙은 '물리적 제약'을 맡는 역할 분담이 작동했다.
- 한계: 테스트 연주자가 1명이므로, 연주자 6명을 번갈아 테스트하는 교차검증이 필요하다.

## 6. 실행 방법

```bash
pip install -r requirements.txt
python scripts/download_guitarset.py          # 주석만 약 40MB
python train.py --epochs 30                    # CPU로 수 분
python evaluate.py                             # 결과표 출력
python convert.py corpus:bach/bwv66.6          # music21 내장 바흐 코랄 → tab
python convert.py my_song.mid --out tab.txt    # 내 MIDI 파일 변환
python scripts/inspect_score.py corpus:bach/bwv66.6   # 악보가 music21 안에서 어떻게 보이는지 확인
```

### 예시: 쇼팽 녹턴 Op.9 No.2 (1~4마디 / 전곡)

`examples/make_nocturne.py`로 입력한 악보(오른손 멜로디 그대로, 왼손은 박마다 화음으로 단순화, 장식음 생략)를
한 옥타브 내려(`--transpose -12`) 변환한 결과입니다.

```bash
python examples/make_nocturne.py
python convert.py examples/nocturne_op9no2_m1-4.musicxml --transpose -12 --max-notes 3 --out examples/nocturne_m1-4_tab_model.txt
python convert.py examples/nocturne_op9no2_m1-4.musicxml --transpose -12 --max-notes 3 --method dp --out examples/nocturne_m1-4_tab_dp.txt

# 전곡 (카덴차는 단순화)
python examples/make_nocturne_full.py
python convert.py examples/nocturne_op9no2_full.musicxml --transpose -12 --max-notes 3 --out examples/nocturne_full_tab_model.txt --musicxml examples/nocturne_full_tab_model.musicxml
```

`--musicxml`로 저장한 파일을 MuseScore에서 열면 **TAB 보표가 원곡 박자대로 보이고, 기타(나일론) 소리로 재생**됩니다.

데이터 없이 코드 동작만 확인하려면:
```bash
python tests/make_fake_guitarset.py && python train.py --data data/fake --epochs 2 --out checkpoints/fake.pt
```

## 7. 한계와 다음 단계

- GuitarSet은 재즈·록 등 기타 곡이라, 피아노 편곡을 치는 방식과는 분포가 다르다 (도메인 차이)
- 편곡 단계가 규칙 기반이라 음악적으로 중요한 내성(가운데 음)을 잃을 수 있다
- 리듬·셈여림은 무시하고 음높이 순서만 본다
- 다음 단계: DadaGP(Guitar Pro tab 2.6만 곡)로 데이터 확장, Transformer 비교, 편곡 단계도 학습으로 대체
