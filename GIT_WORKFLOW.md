# 브랜치 → PR → merge 흐름으로 올리기

혼자 하는 프로젝트라도 기능마다 브랜치를 나누고 PR로 합치면, 실제 팀 협업과 같은 흐름을 연습할 수 있다.

## 0. 처음 한 번
```bash
git init
git add .gitignore README.md requirements.txt tabify/guitar.py tabify/data.py tabify/__init__.py scripts/
git commit -m "feat: GuitarSet 로더와 기타 기본 상수"
git branch -M main
git remote add origin https://github.com/<내아이디>/piano2tab.git
git push -u origin main
```

## 1. 기능마다 브랜치 → PR
```bash
git switch -c feature/baseline-dp
git add tabify/decode.py tabify/baseline.py tabify/metrics.py
git commit -m "feat: 화음 후보 생성과 Viterbi DP 기준선"
git push -u origin feature/baseline-dp
```
→ GitHub에서 **Compare & pull request** → 설명에 *무엇을, 왜* 바꿨는지 적고 → **Merge** → 로컬로 돌아와서:
```bash
git switch main && git pull
```

## 추천 브랜치 순서
| 브랜치 | 파일 | PR 설명에 쓸 것 |
|---|---|---|
| `feature/baseline-dp` | decode.py, baseline.py, metrics.py | 기준선 설계와 비용 함수 |
| `feature/bilstm` | features.py, model.py, predict.py, train.py | 모델 구조, 연주자 기준 분할 이유 |
| `feature/evaluate` | evaluate.py, tests/ | **결과표와 해석** (PR이 실험 노트가 된다) |
| `feature/piano-arrange` | arrange.py, render.py, convert.py | 편곡 규칙, 예시 tab |

## 커밋 메시지 규칙 (Conventional Commits)
`feat:` 기능 추가 · `fix:` 버그 수정 · `docs:` 문서 · `refactor:` 구조 변경 · `exp:` 실험 결과
