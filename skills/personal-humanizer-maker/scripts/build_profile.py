#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_profile.py — assemble a style_profile.json (CODE half of the analysis).

The multi-agent layer writes one dimension_profile JSON per axis (qualitative rules +
mined exemplars). This script does the DETERMINISTIC half:

  1. derive the numeric `baseline` bands straight from quant_profile.json (per
     references/signal-map.md) — reproducible, not hand-written by an LLM;
  2. merge the agents' dimension_profiles, ordered and deduped;
  3. compute overall confidence + weak_axes from per-axis confidence + corpus thinness;
  4. select canonical before/after examples;
  5. emit a schema-conforming style_profile.json for emit_skill.py.

    python3 build_profile.py --quant quant.json --dims dims/ \
        --name taewoo-urp --display "박태우 · URP 문체" -o style_profile.json

Standard library only.
"""
import sys
import os
import re
import json
import glob
import argparse

MAKER_VERSION = "1.0-m4"

AXIS_ORDER = [
    "sentence_architecture", "register_modality", "lexical_register",
    "cohesion_argument", "stance_voice", "figuration", "formatting",
]


def rnd(x, n=2):
    return round(float(x), n)


# ---------------------------------------------------------------- baseline derivation
def derive_baseline(q):
    """quant_profile -> baseline bands. Presence-aware: only emit a band for a trait
    the author actually exhibits, so we never force a trait the corpus lacks."""
    m = q["metrics"]
    thin = q["corpus"].get("thin", False)
    widen = 1.5 if thin else 1.0
    b = {}

    # sentence.len_mean — two-sided band around the mean
    s = m["sentence"]
    v = s.get("len_mean", 0)
    if v:
        w = max(0.15 * v, 0.5 * s.get("len_stdev", 0)) * widen
        b["sentence.len_mean"] = {"min": int(round(v - w)), "max": int(round(v + w)),
                                  "note": "mean sentence length band"}
    # long-sentence ratio — floor (characteristic "more")
    if s.get("long_ratio_80", 0) >= 10:
        b["sentence.long_ratio_80"] = {"min": rnd(0.75 * s["long_ratio_80"], 0),
                                       "note": "long-sentence ratio floor"}
    # clause chaining — floor
    if s.get("clause_chain_density", 0) >= 0.3:
        b["sentence.clause_chain_density"] = {"min": rnd(0.6 * s["clause_chain_density"]),
                                              "note": "clause-chaining floor"}
    # sentence cap — ceiling (guards over-editing)
    if s.get("len_max", 0):
        b["sentence.len_max"] = {"max": int(round(1.02 * s["len_max"])),
                                 "note": "run-on ceiling"}

    # ending
    e = m["ending"]
    if e.get("declarative_ratio", 0) >= 0.6:
        b["ending.declarative_ratio"] = {"min": rnd(0.9 * e["declarative_ratio"]),
                                         "note": "dominant ending register floor"}
    if e.get("hedge_projection_ratio", 0) >= 0.15:
        b["ending.hedge_projection_ratio"] = {"min": rnd(0.6 * e["hedge_projection_ratio"]),
                                              "note": "possibility/projection modality floor"}
    if e.get("spoken_count", 0) == 0:
        b["ending.spoken_count"] = {"max": 0, "note": "no colloquial/honorific endings"}

    # lexical
    lx = m["lexical"]
    if lx.get("gloss_count", 0) >= 3:
        b["lexical.gloss_count"] = {"min": 1, "note": "term-glossing is habitual -> require presence"}
    if lx.get("register_density", 0) >= 5:
        b["lexical.register_density"] = {"min": rnd(0.6 * lx["register_density"]),
                                         "note": "elevated register floor"}

    # cohesion
    ch = m["cohesion"]
    if ch.get("connective_density", 0) >= 0.15:
        b["cohesion.connective_density"] = {"min": rnd(0.5 * ch["connective_density"]),
                                            "note": "connective density floor"}

    # stance
    st = m["stance"]
    if st.get("passive_nominalization_rate", 0) >= 0.25:
        b["stance.passive_nominalization_rate"] = {"min": rnd(0.6 * st["passive_nominalization_rate"]),
                                                   "note": "phenomenon-first floor"}
    if st.get("self_reference_count", 0) >= 2:
        b["stance.self_reference_count"] = {"min": 1, "note": "formal self-reference present"}

    # formatting — presence-aware layout guards
    fm = m["formatting"]
    if fm.get("emoji_count", 0) == 0:
        b["formatting.emoji_count"] = {"max": 0, "note": "no emoji"}
    if fm.get("bullet_ratio", 0) < 0.05:
        b["formatting.bullet_ratio"] = {"max": 0.1, "note": "prose-first, minimal bulleting"}

    return {k: b[k] for k in sorted(b)}


# ---------------------------------------------------------------- dimension merge
def load_dims(paths):
    dims = {}
    for p in paths:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        ax = d.get("axis_group")
        if ax:
            dims[ax] = d  # last write wins per axis
    return dims


def confidence_rollup(dims, thin):
    levels = {ax: d.get("confidence", "low") for ax, d in dims.items()}
    lows = [ax for ax, c in levels.items() if c == "low"]
    highs = [ax for ax, c in levels.items() if c == "high"]
    if thin or len(lows) >= 3:
        overall = "low"
    elif not lows and len(highs) >= 4:
        overall = "high"
    else:
        overall = "medium"
    return overall, sorted(lows)


def pick_examples(dims, limit=5):
    out = []
    for ax in AXIS_ORDER:
        d = dims.get(ax)
        if not d:
            continue
        if d.get("confidence") == "low":
            continue
        for ex in d.get("exemplars", [])[:1]:
            if ex.get("before") and ex.get("after"):
                out.append({"axis": ax, "before": ex["before"], "after": ex["after"]})
                break
        if len(out) >= limit:
            break
    return out


def build_dimensions(dims):
    out = []
    for ax in AXIS_ORDER:
        d = dims.get(ax)
        if not d:
            continue
        rules = []
        for r in d.get("rules", []):
            rules.append({
                "id": r.get("id", ""),
                "statement": r.get("statement", ""),
                "strictness": r.get("strictness", "strict"),
            })
        if not rules:
            continue
        strictness = "advisory" if d.get("confidence") == "low" else "strict"
        out.append({
            "axis_group": ax,
            "summary": (d.get("observations") or [""])[0],
            "strictness": strictness,
            "rules": rules,
        })
    return out


def main():
    ap = argparse.ArgumentParser(description="Assemble style_profile.json from quant_profile + dimension_profiles.")
    ap.add_argument("--quant", required=True, help="quant_profile.json")
    ap.add_argument("--dims", required=True, help="dir of dimension_*.json (or a glob)")
    ap.add_argument("--name", required=True, help="profile_name slug (skill dir = humanize-<name>)")
    ap.add_argument("--display", help="display name")
    ap.add_argument("--note", help="source note (e.g. 'built from a single 36k-char doc')")
    ap.add_argument("-o", "--out", help="write style_profile.json here (default stdout)")
    args = ap.parse_args()

    q = json.load(open(args.quant, encoding="utf-8"))
    lang = q["language"]
    thin = q["corpus"].get("thin", False)

    if os.path.isdir(args.dims):
        dim_paths = sorted(glob.glob(os.path.join(args.dims, "*.json")))
    else:
        dim_paths = sorted(glob.glob(args.dims))
    if not dim_paths:
        sys.exit(f"error: no dimension_profile JSONs found at {args.dims}")
    dims = load_dims(dim_paths)

    overall, weak = confidence_rollup(dims, thin)
    profile = {
        "profile_name": args.name,
        "display_name": args.display or args.name,
        "language": lang,
        "source": {
            "build_files": q["corpus"].get("files", []),
            "total_chars": q["corpus"].get("total_chars", 0),
            "note": args.note or ("built from a thin corpus; several axes advisory" if thin else ""),
        },
        "baseline": derive_baseline(q),
        "dimensions": build_dimensions(dims),
        "ironclad": True,
        "confidence": {"overall": overall, "weak_axes": weak},
        "examples": pick_examples(dims),
        "meta": {"schema_version": "1.0", "maker_version": MAKER_VERSION},
    }

    blob = json.dumps(profile, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(blob + "\n")
        sys.stderr.write(f"wrote {args.out}  (confidence={overall}, weak={weak or 'none'}, "
                         f"axes={len(profile['dimensions'])}, bands={len(profile['baseline'])})\n")
    else:
        print(blob)


if __name__ == "__main__":
    main()
