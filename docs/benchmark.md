# Benchmark — does a one-document build generalize?

The headline question for a personal-humanizer factory: **if you build a voice profile
from a single document, do the numeric bands it derives still fit _other_ documents by
the same author?** If yes, the profile captured a stable voice rather than overfitting
one text. If it also *rejects* a different author, the profile is discriminative, not
just permissive.

We test this on a **public, external, reproducible** corpus — not the maintainer's own
writing — so anyone can re-run it. No third-party text is stored in this repo; only the
derived numbers and the public source URLs.

## Setup

- **Author (positive):** Paul Graham essays — famously consistent voice, all the same
  genre. Public at <https://paulgraham.com>.
  - **Build from one:** *How to Work Hard* (`hwh.html`, ~18k chars).
  - **Held-out (5):** *How to Write Usefully*, *Putting Ideas into Words*, *How to Read*,
    *Be Good*, *How to Do Great Work*.
- **Negative control:** *The Federalist* No. 10 (public domain, Project Gutenberg
  [#1404](https://www.gutenberg.org/ebooks/1404)) — formal English, a very different
  sentence architecture.
- **Pipeline:** `profile_corpus.py` (measure) → 7 axis-specialist agents (analyze) →
  `build_profile.py` (derive **9 strict baseline bands** from the build essay's numbers)
  → `roundtrip_check.py` (measure each held-out doc against those bands).

## Results

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

The Federalist text fails precisely on the **sentence-architecture signature** — mean
sentence length **33 words** vs. the PG band **[13, 22]**, and max length **81** vs. the
cap **62** — while it passes the shared formal-register bands (declarative endings, no
emoji, some long sentences). That is the honest shape of the result: discrimination
concentrates where the voices actually differ (rhythm and sentence length), not in traits
formal prose has in common. The residual ~9% on held-out PG essays is the long-sentence
ratio and glossing edge bands, which vary within a single author's output — exactly what
the `thin`-corpus widening and the 0.85 converged-threshold exist to absorb.

## What the multi-agent pass captured

The 7 axis specialists (one per style axis) read the build essay and wrote the rules the
emitted skill rewrites by. A fixed template could not have produced these — they are
*this* author's voice:

- **Register:** *keep contractions* (you're, it's, don't) and self-answered rhetorical
  questions — PG is conversational, so the analyzer overrode the formal-prose default.
- **Cohesion:** carry pivots with **But / And yet / Whereas**, never *however / therefore /
  moreover* (the quant showed 36 transition markers but 0 academic connectives).
- **Sentence:** ~17-word mean, long clause-chains alternating with **2–6 word punch-line**
  landings.
- **Paragraph landing:** end on a blunt fragment — *"There isn't." / "You need both."*

## Reproduce

```bash
SCR=skills/personal-humanizer-maker/scripts

# 1. fetch a few PG essays to /tmp/pg/*.txt (HTML -> text), then:
python3 $SCR/profile_corpus.py --lang en /tmp/pg/hwh.txt -o /tmp/pg/quant.json

# 2. run the 7 axis agents (see SKILL.md orchestration) -> /tmp/pg/realdims/*.json
#    (or synthesize minimal dims — the baseline is derived from the quant either way)

# 3. assemble the profile (bands are code-derived from the quant)
python3 $SCR/build_profile.py --quant /tmp/pg/quant.json --dims /tmp/pg/realdims \
  --name pg --display "Paul Graham (essays)" -o /tmp/pg/style_profile.json

# 4. convergence: build-from-one vs held-out five
python3 $SCR/roundtrip_check.py --profile /tmp/pg/style_profile.json \
  /tmp/pg/useful.txt /tmp/pg/words.txt /tmp/pg/read.txt /tmp/pg/good.txt /tmp/pg/greatwork.txt

# 5. discrimination: same bands vs a different author
python3 $SCR/roundtrip_check.py --profile /tmp/pg/style_profile.json /tmp/pg/federalist10.txt
```

## Notes & honesty

- **Numbers only.** No PG or Federalist text is vendored here; re-run the commands to
  regenerate everything from the public sources.
- **Genre matters.** Generalization holds *within a register*. Building from a polished
  proposal and testing on a terse lab report by the same person converges less — the
  profiler measures the text you give it, and a person writes differently across genres.
- **Korean path.** The KO profiler is calibrated on modern Korean; it reproduces a
  hand-tuned Korean baseline in the emitter's self-reproduction test. Pre-modern public
  Korean (1920s public-domain essays) is *out of distribution* for the modern-Korean
  signals and is not used as a benchmark.
