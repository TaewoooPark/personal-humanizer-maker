<h1 align="center">personal-humanizer-maker</h1>

<p align="center">
  <strong>Turn your own writing into a personal humanizer skill.</strong><br>
  <em>Feed it one document you wrote; it fingerprints your voice — quantitatively and axis-by-axis — and emits a standalone Claude Code skill that rewrites any text into your style, without touching a single fact.</em>
</p>

<p align="center">
  <a href="./README.ko.md">한국어 README</a>
  &nbsp;·&nbsp;
  <a href="./skills/personal-humanizer-maker/SKILL.md">SKILL.md</a>
  &nbsp;·&nbsp;
  <a href="./schemas">Contracts</a>
  &nbsp;·&nbsp;
  <a href="#benchmark">Benchmark</a>
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

> **One sentence:** point it at a sample you wrote, and get back a ready-to-use skill that
> rewrites *other* text into *your* voice — measured against your own numbers, with the
> meaning frozen.

- 🧬 **Voice from a sample** — build a personal humanizer from as little as one document you wrote.
- 📐 **Quantitative fingerprint** — a stdlib profiler measures sentence architecture, ending register, lexical density, connective rhythm, stance, and formatting as *distributions*, not vibes.
- 🧵 **Multi-agent analysis** — one specialist agent per style axis fans out over your text, then a synthesizer merges them into a single profile.
- 🏭 **Emits a real skill** — output is a standalone `humanize-<name>/` skill: `SKILL.md` + a `style_metrics.py` with *your* baselines baked in + before/after examples mined from your own sentences.
- 🔒 **Meaning stays frozen** — every emitted skill inherits an ironclad covenant: facts, numbers, citations, and order never change; only phrasing, rhythm, and arrangement do.
- 🇰🇷 🇬🇧 **Korean or English** — pick the language at the start; the taxonomy and the metrics switch with it.
- ✅ **Self-verifying** — fully automatic, so the factory round-trips each emitted skill on held-out text and won't silently ship an overfit voice.

## Not Just "Rewrite This in My Style"

A normal prompt like *"make this sound like this sample"* is a one-off imitation. It asks
the model to notice whatever it notices in the moment, and the next request starts over
from scratch.

`personal-humanizer-maker` turns the sample into a reusable, inspectable artifact:

| One-off prompt | personal-humanizer-maker |
|---|---|
| Reads a sample and improvises | Measures the sample into a `quant_profile.json` first |
| Style is whatever the model remembers | Seven axis specialists write explicit rules for sentence shape, register, lexicon, cohesion, stance, figuration, and formatting |
| No persistent baseline | Emits `style_metrics.py` with the author's numeric bands baked in |
| Hard to audit | Emits `style_profile.md` and examples mined from the author's own sentences |
| Can drift or over-edit | Injects the same meaning-invariance covenant into every generated skill |
| Every rewrite repeats the analysis | One build creates `humanize-<name>/`; every later rewrite reuses that skill |

The output is not a vibe prompt. It is closer to a tiny style compiler: sample in,
measured profile out, reusable skill emitted.

## Why It Exists

Writing a style guide for your *own* voice by hand is slow and subjective. The seed skill
[`personal_humanize`](https://github.com/TaewoooPark) is exactly that — a hand-authored
`S1–S8` / `A1–A3` ruleset plus hardcoded metric thresholds, all derived by staring at one
author's corpus until the patterns fell out.

`personal-humanizer-maker` generalizes that labor. Point it at a writing sample and it does
the profiling, the axis-by-axis dimension analysis, the threshold calibration, and the skill
packaging for you — and hands back a skill shaped exactly like the hand-made one, so it
"just works" the same way. The hand-tuned instance becomes one *output* of the factory
rather than a bespoke artifact.

## How It Works

```
sample doc + language (ko/en)
   │  [CODE] profile_corpus.py
   ▼
quant_profile.json   7-axis distributions: sentence length · ending mix · gloss rate · connective density · passive/nominalization · formatting
   │  [MULTI-AGENT] one specialist agent per axis, fanned out   ← references/taxonomy.{lang}.md
   ▼
dimension_profiles[]  per-axis value + confidence + rules + before/after mined from your text
   │  [MULTI-AGENT] synthesizer (barrier): merge, dedup, demote weak axes
   ▼
style_profile.json   unified rules + calibrated baselines + canonical examples
   │  [CODE] emit_skill.py + templates   ← references/ironclad.md (covenant injected)
   ▼
humanize-<name>/     standalone skill: SKILL.md + style_metrics.py (your bands) + examples.md
   │  [CODE+AGENT] roundtrip_check.py + fidelity audit   ← automatic safety gate
   ▼
  PASS → ship  /  FAIL → widen bands · demote low-confidence axes · re-emit once · else ship with CONFIDENCE note
```

Three layers, kept deliberately separate:

| Layer | Does | Artifacts |
|---|---|---|
| **CODE** (deterministic, stdlib-only) | corpus profiler · skill emitter · round-trip checker | `scripts/profile_corpus.py`, `scripts/emit_skill.py`, `scripts/roundtrip_check.py` |
| **REFERENCE** (static knowledge) | style-dimension taxonomy (ko/en) · signal→axis map · covenant · templates | `references/taxonomy.{ko,en}.md`, `references/signal-map.md`, `references/ironclad.md`, `templates/*` |
| **LLM / multi-agent** (interpretive) | axis specialists · synthesizer · fidelity auditor | orchestrated from `SKILL.md` |

## What It Learns

The generated skill is readable. For a Korean public-rhetoric test built from Kim Gu's
*My Wish* excerpts, the emitted `SKILL.md` learned rules like:

```text
SA1. Combine short explanatory sentences into longer declarative sentences around
65-85 Korean characters, without exceeding 135 characters.

RM1. End sentences with -다, -것이다, -이라 믿는다, or -하기 때문이다;
avoid modern polite explanatory endings.

SV1. Use "나는" to state public conviction and responsibility, not private preference.
Expand individual judgment into "우리 사회", "나라", or "민족" when the source supports it.
```

For an English public-oratory test built from Lincoln texts, it learned a different rule
set:

```text
SA2. Use parallel clause chains with repeated openings such as "if", "we", "that",
or "it is" when the source presents alternatives or obligations.

RM1. Keep the prose formal and contraction-free.

CA3. End paragraphs on commitment, preservation, judgment, or consequence rather than
on a neutral summary.
```

Those rules are paired with numeric bands such as mean sentence length, long-sentence
ratio, declarative-ending ratio, passive/nominalization rate, bullet ratio, and emoji
count. A rewrite can then be checked mechanically:

```bash
python3 humanize-kimgu-ko-test/scripts/style_metrics.py rewritten.md
# strict 8/8, CONVERGED
```

## Before / After

### Korean

Neutral modern input:

```text
한국 사회가 기술을 잘 활용하려면 몇 가지 조건이 필요하다. 먼저 시민이 기술의 원리를 이해하고
비판적으로 판단할 수 있어야 한다. 기업은 빠른 성장만 추구하지 말고 이용자의 권리와 안전을 함께
고려해야 한다.
```

Generated Kim Gu-style rewrite:

```text
나는 우리 사회가 기술을 잘 쓰는 나라가 되려면 먼저 시민이 그 기술의 원리를 알고, 스스로 옳고 그름을
판단할 힘을 길러야 한다고 믿는다. 기업도 빠른 성장만을 소원할 것이 아니라 이용자의 권리와 안전이
함께 보장되어야 할 것이요, 정부도 규제를 세울 때에는 현장의 빠른 걸음과 공익의 큰 길이 서로
어그러지지 않도록 해야 할 일이다.
```

The original matched **5 / 8** strict Korean bands. The rewrite matched **8 / 8**.

### English

Scientific input:

```text
Natural selection in each well-stocked country, must act chiefly through the competition
of the inhabitants one with another, and consequently will produce perfection, or strength
in the battle for life, only according to the standard of that country.
```

Generated Lincoln-style rewrite:

```text
Natural selection, in each well-stocked country, must act chiefly through competition,
one inhabitant with another. It may therefore produce perfection, or strength in the
battle for life, only by the standard of that country.
```

The original matched **10 / 12** strict Lincoln bands. The rewrite matched **12 / 12**.

## Install

```bash
git clone https://github.com/TaewoooPark/personal-humanizer-maker.git
cd personal-humanizer-maker

# Claude Code (default) -> ~/.claude/skills
bash setup/install.sh

# Codex -> ~/.codex/skills (+ ~/.agents/skills mirror)
bash setup/install.sh --target codex

# Both
bash setup/install.sh --target both
```

Pure standard-library Python 3.9+. No venv, no third-party packages, no network at install time.

<details>
<summary><b>🤖 …or just let an AI agent install it for you</b></summary>

<br>

Too busy to run three commands? You're already talking to a coding agent — make it earn its keep. Paste the repo link and one of these into Claude Code / Codex / Cursor:

**English**
> Clone `https://github.com/TaewoooPark/personal-humanizer-maker` and install it for this host (`bash setup/install.sh` in Claude Code, or `bash setup/install.sh --target codex` in Codex), then confirm the `personal-humanizer-maker` skill is active in my session. Once it's in, build a personal humanizer from a sample of my writing.

**한국어**
> `https://github.com/TaewoooPark/personal-humanizer-maker` 클론해서 현재 호스트에 맞게 설치해줘(Claude Code면 `bash setup/install.sh`, Codex면 `bash setup/install.sh --target codex`). 그리고 `personal-humanizer-maker` 스킬이 활성화됐는지 확인해줘. 되면 내가 쓴 글 샘플로 개인 휴머나이저 하나 만들어줘.

Yes — the tool for not sounding like an AI, installed by an AI. We're aware.

</details>

## Usage

Inside Claude Code or Codex, trigger it in natural language and hand it a sample:

```
build a personal humanizer from this document I wrote: <path or paste>
내가 쓴 이 글로 개인 휴머나이저 스킬 만들어줘
```

It asks one thing up front — **Korean or English** — then runs the pipeline and drops the
emitted skill into the active host's skill root: `~/.claude/skills/humanize-NAME/` in
Claude Code, or `${CODEX_HOME:-~/.codex}/skills/humanize-NAME/` in Codex. From then on you
humanize any text with *that* skill:

```
humanize this draft in my voice
이 초안 내 문체로 다듬어줘
```

The maker is the factory; the emitted skill is the tool. One profiling run per author; the
skill it produces is reusable forever.

## Outputs

An emitted skill mirrors the hand-made seed exactly, so nothing new has to be learned:

```
~/.claude/skills/humanize-NAME/                  # Claude Code
${CODEX_HOME:-~/.codex}/skills/humanize-NAME/    # Codex
├── SKILL.md                  # §0 covenant + your per-axis rules + workflow + self-check
├── scripts/style_metrics.py  # your baseline bands baked in (+ language flag)
└── references/
    ├── style_profile.md      # the full profile, for transparency / debugging
    └── examples.md           # before/after pairs mined from your own writing
```

## Benchmark

**Two questions:** can a one-document profile generalize to other texts by the same author,
and can an emitted skill actually move a different input into the learned style bands?
Tested with public corpora and smoke-test rewrites in both English and Korean. Full method:
[`docs/benchmark.md`](./docs/benchmark.md).

**Generalization:** build from one Paul Graham essay (*How to Work Hard*), test on five
held-out essays:

| Evaluation | Strict bands | Convergence | Verdict |
|---|:--:|:--:|:--:|
| Paul Graham — 5 held-out essays (pooled) | 41 / 45 | **91%** | ✅ CONVERGED |
| *per essay* | 8–9 / 9 | 89–100% | ✅ |
| Federalist No. 10 — **different author** (control) | 7 / 9 | 78% | ❌ DIVERGED |

A one-document build **generalizes to 91%** of strict bands across the author's other
essays, and the same bands **reject a different author** — which fails precisely on the
sentence-length signature (mean **33 words** vs. the PG band **[13, 22]**), not on traits
formal prose shares. The 7-axis multi-agent pass captured *this* voice, not a template:
**keep contractions**, pivot on **"But / And yet"** (never *however / therefore*), land
paragraphs on a **blunt fragment** (*"There isn't."*).

**Rewrite smoke tests:**

| Test | Before | After | Verdict |
|---|:--:|:--:|:--:|
| Kim Gu-style Korean rewrite | 5 / 8 | **8 / 8** | CONVERGED |
| Lincoln-style English rewrite | 10 / 12 | **12 / 12** | CONVERGED |

These are not claims of perfect authorship cloning. They show the intended product
behavior: the factory creates a measurable, reusable voice skill, and a consumer model can
use that skill to move a draft toward the learned profile while preserving facts.

## Repository Layout

```
personal-humanizer-maker/
├── README.md · README.ko.md · LICENSE
├── schemas/                          # the three code↔agent contracts
│   ├── quant_profile.schema.json
│   ├── dimension_profile.schema.json
│   └── style_profile.schema.json
├── setup/install.sh
└── skills/personal-humanizer-maker/
    ├── SKILL.md                      # orchestrator
    ├── agents/openai.yaml            # Codex UI metadata
    ├── references/                   # taxonomy.{ko,en}.md · signal-map.md · ironclad.md
    ├── scripts/                      # profile_corpus.py · emit_skill.py · roundtrip_check.py
    └── templates/                    # SKILL.md.tmpl · style_metrics.py.tmpl
```

## Notes & Limitations

- **Fully automatic, so overfitting is the real risk.** A thin sample can't support a strong
  claim on every axis — under-supported axes ship as *advisory*, the bands widen, and the
  round-trip gate is the backstop. The factory never ships a voice it couldn't reproduce.
- **Generation costs tokens.** The multi-agent analysis is a one-time cost per author; the
  emitted skill is free to run afterward.
- **Korean is the calibrated path.** The metrics and taxonomy were first derived on a Korean
  corpus; English is supported and switches in at the start, but is the newer path.
- **No third-party text is vendored.** When a public author's writing is used for testing,
  only aggregate metrics are reported — never their text republished.
- **The covenant is not optional.** Meaning-invariance is injected into every emitted skill
  regardless of the author's own style.

## License

Original work in this repository is released under the [MIT License](./LICENSE).
