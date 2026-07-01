# Style-Dimension Taxonomy — English (en)

The **seven universal axes** that describe a personal voice. Each axis-specialist agent
receives this section + the raw samples + the matching slice of `quant_profile.json`, and
fills in the author's value as a `dimension_profile` (see schema). **Do not invent axes —
instantiate this frame.** That is what makes the analysis reference-grounded rather than
free-associative.

**Shared judgment rules — confidence & strictness**
- `sample_support >= 8` with a stable quant signal → `confidence: high`, rules `strict`.
- `3–7` → `medium`.
- `< 3` or a `thin` corpus → `low` → rules MUST be `advisory`; the synthesizer demotes them at emit.
- Never manufacture a rule for a trait the author does **not** exhibit. Describe only what is observed.

---

## Axis 1. sentence_architecture

**Captures** — sentence length band, simple↔complex tendency, how clauses are joined, rhythm (length variance), an upper cap.

**Quant signals** — `metrics.sentence`: `len_*` (words), `long_ratio_80` (≥25 words), `clause_chain_density`.

**Fill in** — target mean length; joining style (subordination vs. parataxis vs. semicolon chaining); rhythm (uniform vs. long/short alternation, backed by `len_stdev`); a cap that prevents run-ons.

**Rule templates**
- "Join 2–3 short clauses with `{the author's connectives}` to a mean of `{band}` words; keep any one sentence ≤ `{cap}` words with subject–verb agreement intact."
- "Alternate long and short sentences at roughly `{ratio}` for rhythm." (only for high-variance authors)

**English hooks** — subordinators: `because, although, since, while, whereas, which, that, as`; coordination: `; and`, em-dash asides; participial openers.

---

## Axis 2. register_modality

**Captures** — sentence mood (declarative / interrogative) and assertion vs. hedged, projective modality; contraction/formality level.

**Quant signals** — `metrics.ending`: `declarative_ratio`, `hedge_projection_ratio`, `spoken_count` (contractions).

**Fill in** — dominant mood; how much the author hedges (`may / could / appears / is expected`) vs. asserts flatly; contraction policy (formal prose usually 0).

**Rule templates**
- "Keep sentences declarative and contraction-free."
- "Prefer projective modality — `{author's hedges}` — over flat assertion, near a `{hedge_projection_ratio}` rate."

**English hooks** — hedges: `may, might, could, appears, seems, suggests, is expected, likely`; contractions to avoid in formal registers: `n't, 're, 've, 'll`.

---

## Axis 3. lexical_register

**Captures** — lexical elevation (Latinate/technical), term-glossing convention, vocabulary richness, intensifier budget.

**Quant signals** — `metrics.lexical`: `register_density` (Latinate/long-word proxy), `gloss_count`, `type_token_ratio`, `intensifier_density`.

**Fill in** — glossing convention (`term (Gloss, ABBR)` on first use, then which short form); Latinate vs. plain-Saxon lean; which intensifiers appear and how often.

**Rule templates**
- "Gloss technical terms on first use as `{author's gloss form}`, then reuse `{short form}` consistently."
- "Favor `{author's register}` diction; spend intensifiers sparingly (`{cap}` per paragraph)."

**English hooks** — gloss: `harmonic oscillator (HO)`; Latinate suffixes `-tion, -ment, -ity, -ous, -ize, -ical`; intensifiers `profoundly, remarkably, decisively, considerably`.

---

## Axis 4. cohesion_argument

**Captures** — connective rhythm (turn → juxtapose → converge), argument macro-structure (e.g. thesis–antithesis–synthesis), how paragraphs land.

**Quant signals** — `metrics.cohesion`: `connective_density`, `transition_markers`, `juxtaposition_markers`, `convergence_markers`.

**Fill in** — the author's actual connective palette; whether points run claim → (however: limit) → (reinterpretation) → (ultimately: synthesis); whether background paragraphs resolve to the thesis in their last sentence.

**Rule templates**
- "Re-sequence a point as claim → (however: limitation) → (reinterpretation) → (ultimately: synthesis) — **reorder and re-link only**, facts untouched."
- "Weave reversal (`{transitions}`) → juxtaposition (`{juxtapositions}`) → convergence (`{convergences}`), landing each paragraph on a convergence marker."
- "Resolve background paragraphs to the thesis in the final sentence — **restate existing claims only**, no new facts (covenant)."

**English hooks** — transition: `however, yet, nevertheless`; juxtaposition: `meanwhile, likewise, for instance, moreover`; convergence: `ultimately, thus, therefore, in the end, consequently`.

---

## Axis 5. stance_voice

**Captures** — passive/nominalization (phenomenon-first), self-reference formality, evaluation/significance-marking habit.

**Quant signals** — `metrics.stance`: `passive_nominalization_rate`, `self_reference_count`, `first_person_count`, `evaluation_density`.

**Fill in** — passive/nominalization lean (phenomenon as subject); self-reference form (`this work / this study` vs. exposed `I/we`); whether points close on a one-line significance stamp.

**Rule templates**
- "Make the phenomenon the subject: recast agentive actives via `{passive/nominalization forms}`."
- "Refer to the work as `{author's self-reference}`; avoid exposed first person."
- "Close on significance, not a neutral list: `{author's evaluation phrases}` — without over-claiming."

**English hooks** — passive `is/are/was + V-ed`; nominalizations `-tion, -ment, -ance`; self-reference `this work, this study, the present`; evaluation `crucial, central, key, essential, pivotal`.

---

## Axis 6. figuration

**Captures** — the allowance and intensity of metaphor / rhetoric.

**Quant signals** — `metrics.figuration`: `metaphor_markers`, `rhetorical_intensity`.

**Fill in** — whether the author uses restrained metaphor (`opens a horizon`, `becomes the origin point`) or stays dry; intensity kept within non-distorting bounds.

**Rule templates**
- "Allow restrained metaphor — `{author's figures}` — only where it does not distort a fact."
- (dry authors) "Use no metaphor; describe plainly."

**English hooks** — `horizon, cornerstone, foundation, opens the door, paves the way`.

**strict/advisory** — figuration is usually low-frequency → default advisory; make "no metaphor" strict only for markedly dry authors.

---

## Axis 7. formatting

**Captures** — paragraph length, bullet/heading usage, emoji, punctuation signature, citation convention.

**Quant signals** — `metrics.formatting`: `para_len_mean`, `bullet_ratio`, `heading_density`, `emoji_count`, `punct_signature`, `citation_style`, `wikilink_error_count`.

**Fill in** — paragraph band; bullet/emoji usage (often zero for formal prose); punctuation signature (em-dash, colon, parentheses); citation style — which is **preserved, not changed** (covenant).

**Rule templates**
- "Keep paragraphs around `{band}`."
- (non-bullet authors) "Carry information in prose paragraphs, not bullet lists."
- "Preserve the citation style (`{citation_style}`) verbatim — no reformatting or moving (covenant §0)."

**strict/advisory** — formatting habits (bullets/emoji present or absent) are usually distinct → strict. A nonzero `wikilink_error_count` is an *error*, not a habit: report it as a finding, never encode it as a rule.
