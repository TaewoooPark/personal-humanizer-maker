---
name: personal-humanizer-maker
description: 사용자가 자신이 쓴 한국어/영어 샘플 문서를 넣으면, 그 글의 문체(문장 건축·종결 화법·어휘 층위·결속·태도·수사·포맷)와 논증 전개를 정량 프로파일러(코드)와 축별 전문 분석 에이전트(다중 에이전트)로 분해해, 그 사람만의 '개인 맞춤 휴머나이저 스킬'을 자동 생성하는 메타 스킬(스킬 공장). 산출물은 ~/.claude/skills/humanize-<이름>/ 에 떨어지는 독립 스킬 — SKILL.md + 저자 기준선이 baked-in 된 style_metrics.py + 본인 텍스트에서 뽑은 before/after 예문. 내용·사실·수치·인용·고유명사는 한 글자도 바꾸지 않는 '의미 불변' 철칙을 모든 생성물에 강제 주입한다. 트리거 — "내 문체로 다듬는 스킬 만들어줘", "이 글로 개인 휴머나이저 빌드", "personal humanizer maker", "내 voice 스킬 제작", "샘플 넣으면 내 문체 뽑아주는 거", "make a personal humanizer from my writing". 단일 글 윤문 자체는 이미 생성된 개인 스킬(예: personal_humanize)이 담당하고, 이 스킬은 그 개인 스킬을 '찍어내는' 공장이다.
---

# personal-humanizer-maker — 개인 문체 휴머나이저 스킬 공장

샘플 문서 → **정량 프로파일 + 정성 분석** → 그 사람만의 윤문 스킬(`humanize-<이름>/`)을 자동 방출한다. 손으로 만든 한 사람의 인스턴스(예: `personal_humanize`)를, 아무 저자의 글에서 **자동으로 찍어내는** 파이프라인이다.

## 0. 철칙 — 의미 불변 (모든 생성물에 주입)

생성되는 모든 스킬은 `references/ironclad.md`의 철칙을 §0로 그대로 물려받는다. 저자의 문체가 무엇이든 **이 계약은 사람 무관하게 고정**이다.

- **사실·수치·단위·연도·인명·고유명사·인과·순서**의 의미는 한 글자도 바꾸지 않는다.
- **인용·링크·각주는 원형 보존.** 형식 변경·이동·삭제 금지.
- **새 주장·새 근거·새 인용 금지.** 없던 사실을 만들지 않는다.
- **과윤문 금지.** 바꾸는 것은 표현·리듬·문장 결합·문단 내 배열뿐.

## 세 층 분리 (코드 · 레퍼런스 · LLM)

| 층 | 담당 | 산출물 |
|---|---|---|
| **CODE** (결정적, stdlib-only) | 정량 프로파일러 · 스킬 방출기 · 왕복 검증기 | `scripts/profile_corpus.py`, `scripts/emit_skill.py`, `scripts/roundtrip_check.py` |
| **REFERENCE** (정적 지식) | style-dimension taxonomy(ko/en) · 신호↔축 매핑 · 철칙 · 템플릿 | `references/taxonomy.{ko,en}.md`, `references/signal-map.md`, `references/ironclad.md`, `templates/*` |
| **LLM / 다중 에이전트** (해석) | 축별 전문 분석가 · 종합기 · 내용충실도 감사관 | 아래 오케스트레이션 |

## 파이프라인

```
샘플문서 + 언어(ko/en)
   │  [CODE] profile_corpus.py
   ▼
quant_profile.json  (7축 분포: 문장길이·종결분포·접속밀도·피동율·병기빈도·포맷…)
   │  [MULTI-AGENT] 축별 전문 분석가 fan-out  ← references/taxonomy.{lang}.md
   ▼
dimension_profiles[]  (축별 값 + confidence + 규칙 + 본인 예문)
   │  [MULTI-AGENT] synthesizer (barrier)
   ▼
style_profile.json  (통합 규칙 + 보정 기준선 + 대표 예문) + style_profile.md
   │  [CODE] emit_skill.py + templates  ← references/ironclad.md (철칙 주입)
   ▼
humanize-<이름>/ 스킬 패키지
   │  [CODE+AGENT] roundtrip_check.py + 충실도 감사   ← 전자동 안전핀
   ▼
  PASS → 배포 / FAIL → 밴드 완화·저신뢰 축 강등·재방출 1회 → CONFIDENCE 경고 동봉
```

## 언어 선택 (ko/en)

호출 시작 시 **한국어/영어**를 선택한다. 선택은 `taxonomy.{lang}.md`, 프로파일러의 언어 모듈, 방출 스킬의 언어 모드를 함께 고른다. 공유 골격 + 언어별 모듈 구조라 3번째 언어 확장은 taxonomy 1개 + 프로파일러 모듈 1개 추가로 끝난다.

## 전자동 모드의 안전장치 (사용자 검토 없음)

검토자가 없으므로 과적합을 코드로 방어한다.
- **얇은 코퍼스 검사**: 총 글자수가 임계 미만이면 confidence를 강등하고 밴드를 넓힌다.
- **축별 confidence**: 근거 예문 수 기반. 저신뢰 축의 규칙은 `strict`가 아닌 `advisory`로 방출.
- **왕복검증 게이트**: 방출 직후 중립화 홀드아웃에 스스로 적용해 (a) 기준선 밴드 수렴 (b) 의미 보존을 확인. 실패 시 재방출 1회, 그래도 실패면 `CONFIDENCE.md` 경고를 동봉해 배포한다. **과적합 스킬을 조용히 배포하지 않는다.**

## 구현 상태

> 이 저장소는 마일스톤별로 커밋·릴리스된다. 각 컴포넌트의 현재 상태:

| 컴포넌트 | 파일 | 상태 |
|---|---|---|
| 계약 스키마 | `schemas/*.schema.json` | ✅ (M0) |
| 정량 프로파일러 | `scripts/profile_corpus.py` | ✅ (M1) |
| taxonomy 레퍼런스 | `references/taxonomy.{ko,en}.md` 외 | ✅ (M2) |
| 스킬 방출기 | `scripts/emit_skill.py` + `templates/*` | ✅ (M3) |
| 다중 에이전트 오케스트레이션 | 본 SKILL.md 상세 절 | ⏳ (M4) |
| 왕복검증 게이트 | `scripts/roundtrip_check.py` | ⏳ (M5) |

## 계약 (schemas/)

코드와 에이전트를 잇는 세 계약:
- `quant_profile.schema.json` — 프로파일러 출력.
- `dimension_profile.schema.json` — 축별 분석가 1인의 출력.
- `style_profile.schema.json` — 종합기 출력, 방출기의 유일한 입력.
