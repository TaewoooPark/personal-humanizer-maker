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

## Install

```bash
git clone https://github.com/TaewoooPark/personal-humanizer-maker.git
cd personal-humanizer-maker

# Claude Code (default) -> ~/.claude/skills
bash setup/install.sh

# Codex -> ~/.agents/skills
bash setup/install.sh --target codex

# Both
bash setup/install.sh --target both
```

Pure standard-library Python 3.9+. No venv, no third-party packages, no network at install time.

## Usage

Inside Claude Code or Codex, trigger it in natural language and hand it a sample:

```
build a personal humanizer from this document I wrote: <path or paste>
내가 쓴 이 글로 개인 휴머나이저 스킬 만들어줘
```

It asks one thing up front — **Korean or English** — then runs the pipeline and drops the
emitted skill into `~/.claude/skills/humanize-<name>/`. From then on you humanize any text
with *that* skill:

```
humanize this draft in my voice
이 초안 내 문체로 다듬어줘
```

The maker is the factory; the emitted skill is the tool. One profiling run per author; the
skill it produces is reusable forever.

## Outputs

An emitted skill mirrors the hand-made seed exactly, so nothing new has to be learned:

```
~/.claude/skills/humanize-<name>/
├── SKILL.md                  # §0 covenant + your per-axis rules + workflow + self-check
├── scripts/style_metrics.py  # your baseline bands baked in (+ language flag)
└── references/
    ├── style_profile.md      # the full profile, for transparency / debugging
    └── examples.md           # before/after pairs mined from your own writing
```

## Benchmark

> Populated at **v1.0.0**, after the end-to-end test. The headline experiment: **build a
> profile from a single document, then humanize a _different, held-out_ document by the same
> author and measure whether the output lands inside that author's own metric bands** — i.e.
> does a one-document build generalize to the rest of the author's corpus? Numbers, deltas,
> and a meaning-preservation check will land here.

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
