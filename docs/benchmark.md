# Benchmark — does the generated voice skill actually work?

`personal-humanizer-maker` makes two claims, and they need different tests.

1. **Profile generalization:** if a profile is built from one document, do its numeric
   bands still fit other documents by the same author, and reject a different author?
2. **Rewrite convergence:** if the factory emits a `humanize-<name>/` skill, can a
   consumer model use that skill to move a new input toward the learned bands while
   preserving meaning?

The first test checks whether the *profile* is overfit. The second checks whether the
emitted skill is more useful than a one-off prompt like "rewrite this in that style."

No third-party source texts are vendored in this repository. The benchmark records source
URLs, derived metrics, and short illustrative snippets only.

## What Gets Measured

The code layer measures shape, not content. For each language it emits a
`quant_profile.json` with signals such as:

| Axis | Examples of measured signals |
|---|---|
| Sentence architecture | mean / median / p90 / max length, long-sentence ratio, clause-chain density |
| Register & modality | declarative ratio, hedge/projection ratio, contraction or spoken-ending count |
| Lexical register | register density, gloss count, intensifier density, type-token ratio |
| Cohesion & argument | transition / juxtaposition / convergence marker density |
| Stance & voice | passive/nominalization rate, first-person count, formal self-reference count |
| Figuration | rhetorical intensity, restrained metaphor markers |
| Formatting | paragraph length, bullet ratio, emoji count, punctuation signature, citation style |

The agent layer then turns those measurements plus the raw sample into explicit rules.
The emitter bakes both into the output skill:

```text
humanize-<name>/
├── SKILL.md                  # covenant + axis rules + workflow
├── scripts/style_metrics.py  # author baseline bands baked in
└── references/
    ├── style_profile.md      # human-readable bands and dimensions
    └── examples.md           # before/after exemplars mined from the sample
```

That means a rewrite can be tested with:

```bash
python3 humanize-<name>/scripts/style_metrics.py rewritten.md
python3 skills/personal-humanizer-maker/scripts/roundtrip_check.py \
  --profile style_profile.json rewritten.md
```

## Test 1 — One-Document Generalization

The headline question for a personal-humanizer factory: **if you build a voice profile
from a single document, do the numeric bands it derives still fit _other_ documents by
the same author?** If yes, the profile captured a stable voice rather than overfitting
one text. If it also *rejects* a different author, the profile is discriminative, not
just permissive.

### Setup

- **Author (positive):** Paul Graham essays, public at <https://paulgraham.com>.
  - **Build from one:** *How to Work Hard* (`hwh.html`, ~18k chars).
  - **Held-out (5):** *How to Write Usefully*, *Putting Ideas into Words*, *How to Read*,
    *Be Good*, *How to Do Great Work*.
- **Negative control:** *The Federalist* No. 10, public domain, Project Gutenberg
  [#1404](https://www.gutenberg.org/ebooks/1404). This is formal English, but with very
  different sentence architecture.
- **Pipeline:** `profile_corpus.py` -> 7 axis-specialist agents -> `build_profile.py`
  -> `roundtrip_check.py`.

### Results

**Within-author generalization** — profile built from *one* essay, tested on five held-out essays:

| Held-out essay | Strict bands passed | Convergence |
|---|:--:|:--:|
| How to Write Usefully | 8 / 9 | 89% |
| Putting Ideas into Words | 8 / 9 | 89% |
| How to Read | 8 / 9 | 89% |
| Be Good | 8 / 9 | 89% |
| How to Do Great Work | 9 / 9 | **100%** |
| **Pooled** | **41 / 45** | **91% — CONVERGED** |

**Discrimination** — the same PG-derived bands against a different author:

| Evaluation doc | Strict bands passed | Convergence | Verdict |
|---|:--:|:--:|:--:|
| Paul Graham (held-out, pooled) | 41 / 45 | **91%** | CONVERGED |
| Federalist No. 10 (different author) | 7 / 9 | **78%** | **DIVERGED** |

The Federalist text fails precisely on the **sentence-architecture signature**: mean
sentence length **33 words** vs. the PG band **[13, 22]**, and max length **81** vs. the
cap **62**. It still passes shared formal-register bands such as declarative endings and
no emoji. That is the desired behavior: discrimination concentrates where the voices
actually differ, not in traits formal prose has in common.

The residual ~9% miss on held-out PG essays comes from long-sentence ratio and glossing
edge bands, which vary within a single author's output. That is why the default
convergence threshold is 0.85 instead of 1.0.

### What the Agents Captured

The 7 axis specialists wrote rules specific to Paul Graham rather than a generic essay
template:

- **Register:** keep contractions and self-answered rhetorical questions.
- **Cohesion:** pivot with **But / And yet / Whereas**, not academic transitions like
  *however / therefore / moreover*.
- **Sentence:** ~17-word mean, alternating clause-chains with short punch-line landings.
- **Paragraph landing:** end on blunt fragments such as *"There isn't."* or *"You need both."*

## Test 2 — English Rewrite Convergence

This test asks whether an emitted skill can guide an actual rewrite. The target voice was
an Abraham Lincoln public-oratory profile built from three public-domain texts:

- Letter to Horace Greeley
- Gettysburg Address
- Second Inaugural Address

Source: Project Gutenberg, [Speeches and Letters of Abraham Lincoln, 1832-1865](https://www.gutenberg.org/files/14721/14721-h/14721-h.htm).

The control input was a scientific passage from Darwin's *On the Origin of Species*.
Source: Project Gutenberg [#1228](https://www.gutenberg.org/files/1228/1228-h/1228-h.htm).

### Learned Skill Shape

The generated Lincoln test skill learned rules like:

```text
SA2. Use parallel clause chains with repeated openings such as "if", "we", "that",
or "it is" when the source presents alternatives or obligations.

RM1. Keep the prose formal and contraction-free.

CA3. End paragraphs on commitment, preservation, judgment, or consequence rather than
on a neutral summary.
```

It also baked in **12 strict bands**, including:

- `sentence.len_mean`: `[13, 29]`
- `sentence.long_ratio_80`: `>= 20.0`
- `sentence.clause_chain_density`: `>= 0.63`
- `ending.declarative_ratio`: `>= 0.79`
- `ending.spoken_count`: `<= 0`
- `stance.passive_nominalization_rate`: `>= 0.37`

### Before / After

Original scientific input:

```text
Natural selection in each well-stocked country, must act chiefly through the competition
of the inhabitants one with another, and consequently will produce perfection, or strength
in the battle for life, only according to the standard of that country.
```

Lincoln-style rewrite:

```text
Natural selection, in each well-stocked country, must act chiefly through competition,
one inhabitant with another. It may therefore produce perfection, or strength in the
battle for life, only by the standard of that country.
```

### Result

| Document | Strict bands passed | Notes |
|---|:--:|---|
| Darwin input | 10 / 12 | Failed hedge/projection and mean sentence length |
| Lincoln-style rewrite | **12 / 12** | `roundtrip_check.py`: **CONVERGED** |

This is not "Lincoln wrote Darwin." It is a narrower and more useful claim: the emitted
skill exposed enough structure for a consumer model to shorten, re-cadence, and formalize
the passage into the learned profile without changing the core claims.

## Test 3 — Korean Rewrite Convergence

This test uses Korean because style transfer is easier to judge visually in the project's
primary language path. The target voice was built from public web excerpts of Kim Gu's
*My Wish* / *Baekbeom Ilji* public-rhetoric style.

Source used for sampling: Kim Koo Foundation page,
<https://www.kimkoo.org/board/kimgu_view.asp?idx=310&skey=&stext=>.

The control input was a neutral modern Korean paragraph about technology, education, and
shared civic responsibility.

### Learned Skill Shape

The generated Korean test skill learned rules like:

```text
SA1. 짧은 설명문은 2~3개씩 묶어 평균 65~85자 안팎의 긴 평서문으로 늘리되,
한 문장은 135자를 넘기지 않는다.

RM1. 문장 끝은 '-다', '-것이다', '-이라 믿는다', '-하기 때문이다' 중심으로 통일하고,
현대적인 설명체 '~합니다/~해요'는 쓰지 않는다.

SV1. '나는'은 사적인 취향이 아니라 신념과 책임을 밝힐 때 쓴다.
개인의 판단은 '우리 사회', '나라', '민족'의 과제로 넓혀 말한다.
```

It baked in **8 strict bands**, including:

- `sentence.len_mean`: `[58, 89]`
- `sentence.long_ratio_80`: `>= 26.0`
- `sentence.len_max`: `<= 136`
- `ending.declarative_ratio`: `>= 0.9`
- `stance.passive_nominalization_rate`: `>= 0.29`
- `formatting.bullet_ratio`: `<= 0.1`
- `formatting.emoji_count`: `<= 0`

### Before / After

Neutral modern input:

```text
한국 사회가 기술을 잘 활용하려면 몇 가지 조건이 필요하다. 먼저 시민이 기술의 원리를 이해하고
비판적으로 판단할 수 있어야 한다. 기업은 빠른 성장만 추구하지 말고 이용자의 권리와 안전을 함께
고려해야 한다.
```

Kim Gu-style rewrite:

```text
나는 우리 사회가 기술을 잘 쓰는 나라가 되려면 먼저 시민이 그 기술의 원리를 알고, 스스로 옳고 그름을
판단할 힘을 길러야 한다고 믿는다. 기업도 빠른 성장만을 소원할 것이 아니라 이용자의 권리와 안전이
함께 보장되어야 할 것이요, 정부도 규제를 세울 때에는 현장의 빠른 걸음과 공익의 큰 길이 서로
어그러지지 않도록 해야 할 일이다.
```

### Result

| Document | Strict bands passed | Notes |
|---|:--:|---|
| Neutral Korean input | 5 / 8 | Failed mean length, long-sentence ratio, passive/nominalization |
| Kim Gu-style rewrite | **8 / 8** | `roundtrip_check.py`: **CONVERGED** |

This shows the Korean path doing the intended thing: the output became longer,
declarative, public-duty oriented, and more explicitly civic in stance, while preserving
the input's claims about technology, citizens, companies, government, education, and
shared responsibility.

## Reproduce

```bash
SCR=skills/personal-humanizer-maker/scripts

# 1. Build the quantitative profile from one or more sample docs.
python3 $SCR/profile_corpus.py --lang en sample.txt -o quant.json

# 2. Run the 7 axis agents described in SKILL.md.
#    They write one JSON per axis into dims/.

# 3. Assemble a style_profile.json. Numeric bands are derived by code.
python3 $SCR/build_profile.py --quant quant.json --dims dims \
  --name demo --display "Demo Voice" -o style_profile.json

# 4. Emit the skill.
python3 $SCR/emit_skill.py style_profile.json -o humanize-demo

# 5. Check a rewrite against the generated bands.
python3 humanize-demo/scripts/style_metrics.py rewritten.md
python3 $SCR/roundtrip_check.py --profile style_profile.json rewritten.md
```

## Notes & Honesty

- **The skill is not a magic clone.** It builds a reusable, measurable style specification.
  Rewrite quality still depends on the model or agent consuming the emitted skill.
- **Numbers are shape-only.** Passing `style_metrics.py` means the output resembles the
  measured form of the voice; it does not certify authorship or literary quality.
- **Meaning beats metrics.** The covenant wins over the bands. A rewrite should never
  change facts, numbers, names, citations, or causal order just to hit a metric.
- **Genre matters.** Build from the genre you plan to rewrite. A public speech profile,
  a lab note profile, and a casual DM profile by the same person will differ.
- **Thin samples are demoted.** Below the language-specific character threshold, weak axes
  are marked advisory and bands widen. The factory should not silently ship a brittle
  voice.
