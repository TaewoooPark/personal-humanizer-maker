<h1 align="center">personal-humanizer-maker</h1>

<p align="center">
  <strong>내가 쓴 글을, 내 문체로 윤문하는 스킬로 바꾼다.</strong><br>
  <em>직접 쓴 문서 한 편을 넣으면 그 글의 voice를 정량적으로, 또 축별로 지문화해, 어떤 텍스트든 내 문체로 다듬는 독립 Claude Code 스킬을 — 사실은 한 글자도 건드리지 않고 — 자동으로 방출한다.</em>
</p>

<p align="center">
  <a href="./README.md">English README</a>
  &nbsp;·&nbsp;
  <a href="./skills/personal-humanizer-maker/SKILL.md">SKILL.md</a>
  &nbsp;·&nbsp;
  <a href="./schemas">계약(schemas)</a>
  &nbsp;·&nbsp;
  <a href="#벤치마크">벤치마크</a>
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/TaewoooPark/personal-humanizer-maker?style=flat-square&labelColor=000000&color=333333&cacheSeconds=3600" alt="License">
  <img src="https://img.shields.io/github/stars/TaewoooPark/personal-humanizer-maker?style=flat-square&logo=github&logoColor=white&labelColor=000000&color=333333&cacheSeconds=3600" alt="GitHub stars">
  <img src="https://img.shields.io/github/last-commit/TaewoooPark/personal-humanizer-maker?style=flat-square&labelColor=000000&color=333333&cacheSeconds=3600" alt="Last commit">
  <img src="https://img.shields.io/github/languages/top/TaewoooPark/personal-humanizer-maker?style=flat-square&labelColor=000000&color=333333&cacheSeconds=3600" alt="Top language">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-000000?style=flat-square&logo=anthropic&logoColor=white&labelColor=000000&cacheSeconds=3600" alt="Claude Code">
  <img src="https://img.shields.io/badge/OpenAI%20Codex-000000?style=flat-square&logo=openai&logoColor=white&labelColor=000000&cacheSeconds=3600" alt="OpenAI Codex">
  <img src="https://img.shields.io/badge/Skill%20factory-000000?style=flat-square&labelColor=000000&color=000000&cacheSeconds=3600" alt="Skill factory">
  <img src="https://img.shields.io/badge/Python%20stdlib--only-000000?style=flat-square&logo=python&logoColor=white&labelColor=000000&cacheSeconds=3600" alt="Python stdlib only">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Korean%20%C2%B7%20English-000000?style=flat-square&labelColor=000000&color=000000&cacheSeconds=3600" alt="Korean and English">
  <img src="https://img.shields.io/badge/Multi--agent%20analysis-000000?style=flat-square&labelColor=000000&color=000000&cacheSeconds=3600" alt="Multi-agent analysis">
  <img src="https://img.shields.io/badge/Code%20%2B%20Reference%20driven-000000?style=flat-square&labelColor=000000&color=000000&cacheSeconds=3600" alt="Code plus reference driven">
  <img src="https://img.shields.io/badge/Round--trip%20verified-000000?style=flat-square&labelColor=000000&color=000000&cacheSeconds=3600" alt="Round-trip verified">
</p>

---

> **한 줄 요약:** 내가 쓴 샘플 한 편을 가리키면, *다른* 글을 *내* 문체로 다듬는 스킬을 돌려준다 —
> 내 문체 수치를 기준으로 재고, 의미는 얼려둔 채로.

- 🧬 **샘플에서 voice 추출** — 직접 쓴 문서 단 한 편만으로 개인 휴머나이저를 빌드한다.
- 📐 **정량 지문** — stdlib 프로파일러가 문장 건축·종결 화법·어휘 밀도·접속 리듬·태도·포맷을 감이 아니라 *분포*로 측정한다.
- 🧵 **다중 에이전트 분석** — 문체 축마다 전문 분석가 1명이 글에 팬아웃한 뒤, 종합기가 하나의 프로파일로 병합한다.
- 🏭 **진짜 스킬을 방출** — 산출물은 독립 `humanize-<이름>/` 스킬이다: `SKILL.md` + *내* 기준선이 baked-in 된 `style_metrics.py` + 내 문장에서 뽑은 before/after 예문.
- 🔒 **의미는 얼어 있다** — 방출되는 모든 스킬은 철칙을 물려받는다: 사실·수치·인용·순서는 결코 바뀌지 않고, 표현·리듬·배열만 바뀐다.
- 🇰🇷 🇬🇧 **한국어 또는 영어** — 시작 시 언어를 고르면 taxonomy와 metrics가 함께 전환된다.
- ✅ **자가검증** — 전자동이므로, 공장은 방출된 스킬을 홀드아웃 텍스트에 왕복 적용해 과적합된 voice를 조용히 내보내지 않는다.

## 왜 필요한가

*자기* 문체의 스타일 가이드를 손으로 써 내려가는 일은 더디고 주관적일 수밖에 없는바, 씨앗 스킬
[`personal_humanize`](https://github.com/TaewoooPark)가 바로 그 수고의 산물이다 — 한 저자의
코퍼스를 패턴이 드러날 때까지 들여다본 끝에 도출한, 손수 벼려낸 `S1–S8` / `A1–A3` 규칙과
하드코딩된 지표 임계값의 묶음인 것이다.

`personal-humanizer-maker`는 바로 그 수고를 일반화한다. 글 샘플을 가리키기만 하면 프로파일링과
축별 dimension 분석, 임계값 보정, 스킬 패키징에 이르는 일련의 과정을 대신 수행하고 — 손으로 만든
것과 한 치도 다르지 않은 모양의 스킬을 돌려주는 만큼, 사용 방식 또한 동일하게 "그냥 작동한다".
결국 손으로 튜닝한 인스턴스는 별도의 맞춤 산출물이 아니라, 공장이 찍어내는 하나의 *출력*으로
자리매김하는 셈이다.

## 작동 방식

```
샘플문서 + 언어(ko/en)
   │  [CODE] profile_corpus.py
   ▼
quant_profile.json   7축 분포: 문장길이 · 종결분포 · 병기율 · 접속밀도 · 피동/명사화 · 포맷
   │  [MULTI-AGENT] 축별 전문 분석가 팬아웃   ← references/taxonomy.{lang}.md
   ▼
dimension_profiles[]  축별 값 + confidence + 규칙 + 본인 텍스트에서 뽑은 before/after
   │  [MULTI-AGENT] 종합기(barrier): 병합·중복제거·저신뢰 축 강등
   ▼
style_profile.json   통합 규칙 + 보정 기준선 + 대표 예문
   │  [CODE] emit_skill.py + templates   ← references/ironclad.md (철칙 주입)
   ▼
humanize-<이름>/     독립 스킬: SKILL.md + style_metrics.py(내 밴드) + examples.md
   │  [CODE+AGENT] roundtrip_check.py + 충실도 감사   ← 전자동 안전 게이트
   ▼
  PASS → 배포  /  FAIL → 밴드 완화 · 저신뢰 축 강등 · 재방출 1회 · 그래도 실패면 CONFIDENCE 동봉
```

세 층을 일부러 분리해 둔다:

| 층 | 담당 | 산출물 |
|---|---|---|
| **CODE** (결정적, stdlib-only) | 코퍼스 프로파일러 · 스킬 방출기 · 왕복 검증기 | `scripts/profile_corpus.py`, `scripts/emit_skill.py`, `scripts/roundtrip_check.py` |
| **REFERENCE** (정적 지식) | style-dimension taxonomy(ko/en) · 신호→축 매핑 · 철칙 · 템플릿 | `references/taxonomy.{ko,en}.md`, `references/signal-map.md`, `references/ironclad.md`, `templates/*` |
| **LLM / 다중 에이전트** (해석) | 축별 분석가 · 종합기 · 충실도 감사관 | `SKILL.md`에서 오케스트레이션 |

## 설치

```bash
git clone https://github.com/TaewoooPark/personal-humanizer-maker.git
cd personal-humanizer-maker

# Claude Code (기본) -> ~/.claude/skills
bash setup/install.sh

# Codex -> ~/.codex/skills (+ ~/.agents/skills mirror)
bash setup/install.sh --target codex

# 둘 다
bash setup/install.sh --target both
```

순수 표준 라이브러리 Python 3.9+. 설치 시 venv·서드파티 패키지·네트워크가 필요 없다.

<details>
<summary><b>🤖 …아니면 그냥 AI 에이전트한테 설치를 시켜라</b></summary>

<br>

명령어 세 줄 치기도 귀찮다면 — 어차피 코딩 에이전트와 대화 중이잖은가. 레포 링크와 아래 프롬프트 중 하나를 Claude Code / Codex / Cursor에 붙여넣어라:

**English**
> Clone `https://github.com/TaewoooPark/personal-humanizer-maker` and install it for this host (`bash setup/install.sh` in Claude Code, or `bash setup/install.sh --target codex` in Codex), then confirm the `personal-humanizer-maker` skill is active in my session. Once it's in, build a personal humanizer from a sample of my writing.

**한국어**
> `https://github.com/TaewoooPark/personal-humanizer-maker` 클론해서 현재 호스트에 맞게 설치해줘(Claude Code면 `bash setup/install.sh`, Codex면 `bash setup/install.sh --target codex`). 그리고 `personal-humanizer-maker` 스킬이 활성화됐는지 확인해줘. 되면 내가 쓴 글 샘플로 개인 휴머나이저 하나 만들어줘.

그렇다 — AI 티 안 나게 해주는 도구를, AI가 설치한다. 우리도 안다.

</details>

## 사용법

Claude Code나 Codex 안에서 자연어로 트리거하며 샘플을 건넨다:

```
내가 쓴 이 문서로 개인 휴머나이저 만들어줘: <경로 또는 붙여넣기>
build a personal humanizer from this document I wrote
```

시작 시 **한국어/영어** 하나만 물은 뒤 파이프라인을 돌리고, 방출된 스킬을 현재 호스트의 스킬
루트에 떨어뜨린다. Claude Code에서는 `~/.claude/skills/humanize-NAME/`, Codex에서는
`${CODEX_HOME:-~/.codex}/skills/humanize-NAME/`이다. 이후로는 *그* 스킬로 아무 텍스트나 윤문한다:

```
이 초안 내 문체로 다듬어줘
humanize this draft in my voice
```

요컨대 maker가 공장이라면 방출된 스킬은 그 공장이 벼려낸 도구다. 저자당 프로파일링은 단 한 번에
그치되 그렇게 만들어진 스킬은 이후로도 거듭 재사용되는 만큼, 분석의 수고는 일회로 수렴하고 그
산물은 오래도록 남는다.

## 산출물

방출된 스킬은 손으로 만든 씨앗과 똑같은 모양이라, 새로 익힐 것이 없다:

```
~/.claude/skills/humanize-NAME/                  # Claude Code
${CODEX_HOME:-~/.codex}/skills/humanize-NAME/    # Codex
├── SKILL.md                  # §0 철칙 + 내 축별 규칙 + 워크플로 + 자가검증
├── scripts/style_metrics.py  # 내 기준선 밴드 baked-in (+ 언어 플래그)
└── references/
    ├── style_profile.md      # 전체 프로파일 — 투명성/디버깅용
    └── examples.md           # 내 글에서 뽑은 before/after 쌍
```

## 벤치마크

**물음은 이렇다.** 문서 *한 편*으로 voice 프로파일을 빌드했을 때, 그 수치 밴드가 같은 저자의
*다른* 문서들에도 들어맞는가(일반화), 그리고 *다른* 저자는 밀어내는가(판별)? **공개·외부·재현
가능한** 코퍼스 — **Paul Graham 에세이**(문체가 일관되고 전부 공개) — 로 검증했다. 유지자 본인의
글이 아니다. 서드파티 원문은 담지 않고 도출 수치만 싣는다. 방법론과 재현:
[`docs/benchmark.md`](./docs/benchmark.md).

**에세이 한 편**(*How to Work Hard*)으로 빌드해 **홀드아웃 다섯 편**에 검증:

| 평가 대상 | strict 밴드 | 수렴 | 판정 |
|---|:--:|:--:|:--:|
| Paul Graham — 홀드아웃 5편(pooled) | 41 / 45 | **91%** | ✅ 수렴 |
| *에세이별* | 8–9 / 9 | 89–100% | ✅ |
| Federalist No. 10 — **다른 저자**(대조군) | 7 / 9 | 78% | ❌ 발산 |

한 편으로 빌드한 프로파일이 저자의 다른 에세이 전반에서 strict 밴드의 **91%로 일반화**되고, 같은
밴드가 **다른 저자는 거부**한다 — 그것도 문장 길이 시그니처(평균 **33단어** vs PG 밴드 **[13, 22]**)
에서 정확히 갈리며, 격식 산문이 공유하는 특성에서 갈리지 않는다. 7축 다중 에이전트 분석은 템플릿이
아니라 *그* 저자의 voice를 잡아냈다 — **축약형 보존**, **"But / And yet"**로 전환(*however /
therefore*가 아니라), 문단을 **짧은 단정 조각**(*"There isn't."*)으로 착지.

## 저장소 구조

```
personal-humanizer-maker/
├── README.md · README.ko.md · LICENSE
├── schemas/                          # 코드↔에이전트 세 계약
│   ├── quant_profile.schema.json
│   ├── dimension_profile.schema.json
│   └── style_profile.schema.json
├── setup/install.sh
└── skills/personal-humanizer-maker/
    ├── SKILL.md                      # 오케스트레이터
    ├── agents/openai.yaml            # Codex UI metadata
    ├── references/                   # taxonomy.{ko,en}.md · signal-map.md · ironclad.md
    ├── scripts/                      # profile_corpus.py · emit_skill.py · roundtrip_check.py
    └── templates/                    # SKILL.md.tmpl · style_metrics.py.tmpl
```

## 유의사항과 한계

- **전자동이므로 과적합이 진짜 위험이다.** 얇은 샘플은 모든 축을 강하게 주장할 근거가 못 된다 —
  근거가 부족한 축은 *advisory*로 방출하고, 밴드를 넓히며, 왕복 게이트가 최후의 방어선이 된다.
  공장은 스스로 재현하지 못하는 voice를 내보내지 않는다.
- **생성에는 토큰이 든다.** 다중 에이전트 분석은 저자당 한 번의 비용이고, 방출된 스킬은 이후
  무료로 돌아간다.
- **한국어가 보정된 경로다.** 지표와 taxonomy는 한국어 코퍼스에서 먼저 도출됐다. 영어도
  시작 시 전환되어 지원되지만 더 새로운 경로다.
- **서드파티 텍스트는 담지 않는다.** 공개 저자의 글을 테스트에 쓸 때도 집계 지표만 보고하며,
  그들의 텍스트를 재배포하지 않는다.
- **철칙은 선택이 아니다.** 의미 불변은 저자의 문체가 무엇이든 모든 방출 스킬에 주입된다.

## 라이선스

이 저장소의 원본 작업물은 [MIT License](./LICENSE)로 배포된다.
