---
name: personal-humanizer-maker
description: >-
  Feed in a Korean or English sample of your own writing, and this meta-skill
  (a skill factory) decomposes its style and argument flow with a quantitative
  profiler plus one specialist agent per axis, then auto-generates a personal
  humanizer skill. The output is a standalone humanize-NAME skill for the
  current host: Claude Code emits under ~/.claude/skills, while Codex emits
  under the Codex skill root. It includes SKILL.md, style_metrics.py with the
  author's baselines baked in, and before/after examples mined from the
  author's own text. A meaning-invariance covenant is injected into every
  generated skill. Triggers — "make a personal humanizer from my writing",
  "build a humanizer skill in my voice", "personal humanizer maker", "profile
  my writing style into a skill", "내 문체로 다듬는 스킬 만들어줘", "이 글로 개인
  휴머나이저 빌드", "내 voice 스킬 제작", "샘플 넣으면 내 문체 뽑아주는 거".
  Rewriting a single text is the job of an already-generated personal skill;
  THIS skill is the factory that stamps those personal skills out.
---

# personal-humanizer-maker — a personal-voice humanizer skill factory

Sample document → **quantitative profile + qualitative analysis** → a humanizer skill
(`humanize-NAME/`) that is that person's alone, emitted automatically. It is the
pipeline that stamps out — from any author's writing — the kind of hand-tuned instance a
human would otherwise build by hand (e.g. `personal_humanize`).

## 0. The covenant — meaning is invariant (injected into every output)

Every generated skill inherits the covenant in `references/ironclad.md` as its §0.
Whatever the author's style, **this contract is fixed, author-independent**.

- **Facts, numbers, units, years, names, proper nouns, causality, and order** never change — not by a single token.
- **Citations, links, and footnotes are preserved verbatim.** No reformatting, moving, or deleting.
- **No new claims, evidence, or citations.** Invent nothing that wasn't there.
- **No over-editing.** Only phrasing, rhythm, sentence joining, and within-paragraph arrangement change.

## Three layers (code · reference · LLM)

| Layer | Does | Artifacts |
|---|---|---|
| **CODE** (deterministic, stdlib-only) | quantitative profiler · skill emitter · round-trip checker | `scripts/profile_corpus.py`, `scripts/emit_skill.py`, `scripts/roundtrip_check.py`, `scripts/build_profile.py` |
| **REFERENCE** (static knowledge) | style-dimension taxonomy (ko/en) · signal→axis map · covenant · templates | `references/taxonomy.{ko,en}.md`, `references/signal-map.md`, `references/ironclad.md`, `templates/*` |
| **LLM / multi-agent** (interpretive) | axis specialists · synthesizer · fidelity auditor | orchestration below |

## Pipeline

```
sample doc + language (ko/en)
   │  [CODE] profile_corpus.py
   ▼
quant_profile.json  (7-axis distributions: sentence length · ending mix · connective density · passive rate · gloss rate · formatting …)
   │  [MULTI-AGENT] one specialist agent per axis, fanned out  ← references/taxonomy.{lang}.md
   ▼
dimension_profiles[]  (per-axis value + confidence + rules + exemplars mined from the author)
   │  [MULTI-AGENT] synthesizer (barrier)
   ▼
style_profile.json  (unified rules + calibrated baselines + canonical examples) + style_profile.md
   │  [CODE] emit_skill.py + templates  ← references/ironclad.md (covenant injected)
   ▼
humanize-NAME/ skill package
   │  [CODE+AGENT] roundtrip_check.py + fidelity audit  ← automatic safety gate
   ▼
  PASS → ship / FAIL → widen bands · demote low-confidence axes · re-emit once → ship with CONFIDENCE note
```

## Language selection (ko/en)

At the start, pick **Korean or English**. That choice selects `taxonomy.{lang}.md`, the
profiler's language module, and the emitted skill's language mode together. The shared
skeleton + per-language module design means a third language is one taxonomy file plus one
profiler module.

## Automatic-mode safety (no human review)

With no reviewer in the loop, overfitting is defended in code.
- **Thin-corpus check**: below the character threshold, confidence is demoted and bands widen.
- **Per-axis confidence**: based on exemplar count. Low-confidence axes ship as `advisory`, not `strict`.
- **Round-trip gate**: right after emit, the skill is applied to a neutralized held-out text to confirm (a) the baseline bands converge and (b) meaning is preserved. On failure it re-emits once; if it still fails, it ships with a `CONFIDENCE.md` warning. **An overfit skill is never shipped silently.**

## Orchestration procedure (how to run)

When invoked, proceed in order. **CODE steps are deterministic; agent steps are interpretive.**

**0. Gather input.** Confirm the language (ko/en), and take the sample path(s) + a
`profile_name` (slug) + a `display_name`. Warn if the corpus is thin (below threshold).

**1. Quantitative profile (CODE).**
```bash
python3 scripts/profile_corpus.py --lang <ko|en> <sample...> -o runs/<name>/quant_profile.json
```

**2. Axis-specialist fan-out (multi-agent).** Launch one subagent **in parallel** per axis
(`sentence_architecture, register_modality, lexical_register, cohesion_argument, stance_voice, figuration, formatting`). Prompt each with:

> You are the **<axis>** specialist. Read: (a) the <axis> section of `references/taxonomy.<lang>.md`, (b) the author sample, (c) the <axis> slice of `quant_profile.json`. Emit one `dimension_profile` JSON (schema `schemas/dimension_profile.schema.json`) describing how this author handles the axis. Include — `observations` (with evidence), `confidence` (by exemplar count: ≥8 high / 3–7 medium / <3 low), `rules` for a rewriter (imperative, with the author's observed values filled in), and before/after `exemplars` copied **verbatim from the sample** (after = a real author sentence, before = a plainer same-meaning paraphrase). **Do not invent axes — fill the taxonomy frame. Facts/content are not your concern — only the shape of the style.** Do not manufacture a rule for a trait the author does not exhibit.

Save each agent's output to `runs/<name>/dims/<axis>.json`. (Use `parallel(7 agents)` when a Workflow is available, otherwise 7 concurrent Agent-tool calls.)

**3. Assemble (CODE).** Baseline bands are derived **by code, not the LLM**, from the quant profile (reproducibility).
```bash
python3 scripts/build_profile.py --quant runs/<name>/quant_profile.json --dims runs/<name>/dims \
  --name <name> --display "<display_name>" -o runs/<name>/style_profile.json
```

**4. Emit (CODE).**
```bash
python3 scripts/emit_skill.py runs/<name>/style_profile.json --host auto
```
`--host auto` emits to the active host's skill root: `~/.claude/skills` for Claude Code,
`${CODEX_HOME:-~/.codex}/skills` for Codex. Use `--host claude`, `--host codex`, or `-o`
to override explicitly.

**5. Round-trip gate (CODE + agent).** Apply the fresh skill to a neutralized held-out
text to confirm baseline convergence + meaning preservation. On failure, widen bands /
demote low-confidence axes / re-emit once; if it still fails, ship with `CONFIDENCE.md`.

> **Optional synthesizer agent.** When axis outputs conflict (e.g. the lexical and
> figuration axes propose opposing rules) or exemplars are excessive, a synthesizer agent
> may tidy the dims before `build_profile.py`. The default code-merge path is enough.

## Components

| Component | File | Role |
|---|---|---|
| Contract schemas | `schemas/*.schema.json` | code↔agent glue; installed copies are bundled inside the skill |
| Quantitative profiler | `scripts/profile_corpus.py` | 7-axis distributions → `quant_profile.json` |
| Taxonomy references | `references/taxonomy.{ko,en}.md` + `signal-map.md` | per-axis rule frame + band derivation |
| Profile assembler | `scripts/build_profile.py` | derive baselines + merge dims → `style_profile.json` |
| Skill emitter | `scripts/emit_skill.py` + `templates/*` | `style_profile.json` → `humanize-<name>/` |
| Round-trip gate | `scripts/roundtrip_check.py` | convergence check + relaxation |

## Contracts (schemas/)

The three contracts that join code and agents:
- `quant_profile.schema.json` — the profiler's output.
- `dimension_profile.schema.json` — one axis specialist's output.
- `style_profile.schema.json` — the synthesizer's output, the emitter's sole input.
