# signal-map — quant_profile 신호 ↔ 축 ↔ 방출 밴드

`profile_corpus.py`가 낸 각 수치가 **어느 축을 뒷받침하는지**, 그리고 그 수치가 방출 스킬의
`style_metrics.py` **밴드로 어떻게 변환되는지**를 규정한다. 분석가는 왼쪽(축 귀속)을, 방출기
(`emit_skill.py`)는 오른쪽(밴드 도출)을 읽는다.

## 신호 → 축 귀속

| quant_profile 경로 | 축 | 읽는 법 |
|---|---|---|
| `sentence.len_mean/median/p90/max/stdev` | 1 문장건축 | 길이대·상한·리듬 |
| `sentence.long_ratio_80` | 1 문장건축 | 만연체 강도 |
| `sentence.clause_chain_density` | 1 문장건축 | 종속절 직렬 성향 |
| `ending.declarative_ratio` | 2 종결·화법 | 지배 종결체 |
| `ending.hedge_projection_ratio` | 2 종결·화법 | 가능·전망 화법 |
| `ending.spoken_count` | 2 종결·화법 | 구어/경어 회피(목표 0) |
| `lexical.register_density` | 3 어휘층위 | 한자어/Latinate 격 |
| `lexical.gloss_count` | 3 어휘층위 | 전문용어 병기 관례 |
| `lexical.type_token_ratio` | 3 어휘층위 | 어휘 다양성 |
| `lexical.intensifier_density` | 3 어휘층위 | 강조 부사 예산 |
| `cohesion.connective_density` | 4 결속·논증 | 접속 밀도 |
| `cohesion.transition/juxtaposition/convergence_markers` | 4 결속·논증 | 전환→병치→수렴 리듬 |
| `stance.passive_nominalization_rate` | 5 태도·시점 | 현상 중심 서술 |
| `stance.self_reference_count` | 5 태도·시점 | 격식 자기지칭 |
| `stance.first_person_count` | 5 태도·시점 | 1인칭 노출(대개 회피) |
| `stance.evaluation_density` | 5 태도·시점 | 평가·의의 부각 |
| `figuration.metaphor_markers` / `rhetorical_intensity` | 6 수사 | 은유 허용 폭 |
| `formatting.para_len_mean` | 7 포맷 | 문단 길이 |
| `formatting.bullet_ratio` / `heading_density` / `emoji_count` | 7 포맷 | 레이아웃 습관 |
| `formatting.punct_signature` | 7 포맷 | 구두점 시그니처 |
| `formatting.citation_style` | 7 포맷 | 인용 표기(보존 대상) |
| `formatting.wikilink_error_count` | — | **오류**(습관 아님) → 규칙화 금지, 발견 보고만 |

## 밴드 도출 규칙 (emit_skill.py)

측정값 `v`(분포는 `mean`, `stdev`)를 방출 스킬의 목표 밴드로 변환한다. 세 종류:

- **양방향 밴드 `[min,max]`** — 중심값 주변 허용대. 기본 폭은 `max(0.15*v, 0.5*stdev)`.
  - 예: `len_mean=93.6, stdev=34.8` → `[78, 109]` 정도(≈ `v ± 0.5·stdev`를 반올림, 하한은 가독성 고려).
  - 코퍼스가 `thin`이면 폭을 1.5배로 넓힌다(과적합 방지).
- **하한 `{min}`** — "이상"이어야 하는 신호. 관측값의 `0.75*v`를 바닥으로.
  - 예: `long_ratio_80=62` → `min 45`; `declarative_ratio=1.0` → `min 0.9`.
- **상한 `{max}`** — "이하"여야 하는 신호(과윤문·오류 방지).
  - 예: `len_max=244` → `max 245`; `spoken_count=0` → `max 0`.

**strictness 반영** — 축의 `confidence`가 `low`(또는 `thin`)면 해당 밴드는 방출 스킬에서 PASS/WARN의
`WARN`으로만 쓰고 실패로 승격하지 않는다. 즉 밴드는 유지하되 강제력을 낮춘다.

**의미 불변 우선** — 어떤 밴드도 철칙(§0)을 이기지 못한다. 방출 스킬의 자가검증 문구에
"WARN이 곧 실패는 아니다 — 의미 불변을 어기면서까지 수치를 맞추지 말 것"을 항상 포함한다.

## 예시 — URP 기준선 → 밴드 (참고용, 씨앗 재현 목표)

| 신호 | 관측 | 방출 밴드 |
|---|---|---|
| `sentence.len_mean` | 93.6 | `[70,115]` |
| `sentence.long_ratio_80` | 62 | `min 45` |
| `sentence.len_max` | 244 | `max 245` |
| `ending.declarative_ratio` | 1.0 | `min 0.9` |
| `ending.spoken_count` | 0 | `max 0` |
| `lexical.gloss_count` | 65 | `min 1`(일관 병기 → 존재 요구) |
| `stance.self_reference_count` | 49 | `min 1` |
| `formatting.wikilink_error_count` | 6 | 밴드 없음(발견 보고만) |

이 표는 손으로 만든 `personal_humanize`의 하드코딩 임계값을 방출기가 **자동 재현**할 수 있어야
함을 보여주는 참조점이다(M3 자기재현 검증).
