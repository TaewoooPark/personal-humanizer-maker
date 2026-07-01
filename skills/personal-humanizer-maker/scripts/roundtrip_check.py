#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""roundtrip_check.py — the fully-automatic safety gate.

Given a style_profile.json and one or more *evaluation* documents, this measures each
doc with the same profiler and reports whether it lands inside the profile's baseline
bands. Two uses:

  * generalization test — feed a *held-out doc by the same author*: do the bands built
    from doc A also fit doc B? (the headline benchmark)
  * convergence gate — feed a *humanized output*: did the rewrite reach the author's
    numbers without a strict-band failure?

    python3 roundtrip_check.py --profile style_profile.json held_out.md
    python3 roundtrip_check.py --profile style_profile.json rewrite.md --relax widened.json

Exit code: 0 if converged (or within threshold), 1 if diverged. Standard library only.
The content-fidelity half of the gate (did meaning survive?) is an LLM audit, specified
in SKILL.md and run alongside this — numbers alone never certify a rewrite.
"""
import sys
import os
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from profile_corpus import measure


def dig(d, path):
    cur = d
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def band_ok(value, band):
    if value is None:
        return None
    lo, hi = band.get("min"), band.get("max")
    if lo is not None and value < lo:
        return False
    if hi is not None and value > hi:
        return False
    return True


def fmt_band(band):
    lo, hi = band.get("min"), band.get("max")
    if lo is not None and hi is not None:
        return f"[{lo}, {hi}]"
    return f">= {lo}" if lo is not None else f"<= {hi}"


AXIS_OF_PREFIX = {
    "sentence": "sentence_architecture", "ending": "register_modality",
    "lexical": "lexical_register", "cohesion": "cohesion_argument",
    "stance": "stance_voice", "figuration": "figuration", "formatting": "formatting",
}


def strictness_of(profile, path):
    weak = set(profile.get("confidence", {}).get("weak_axes", []))
    axis = AXIS_OF_PREFIX.get(path.split(".")[0])
    spec = profile["baseline"].get(path, {})
    if "strict" in spec:
        return spec["strict"]
    return axis not in weak


def evaluate(profile, docs):
    lang = profile["language"]
    baseline = profile["baseline"]
    per_doc = []
    for path in docs:
        with open(path, encoding="utf-8") as f:
            prof = measure(f.read(), lang)
        m = prof["metrics"]
        rows = []
        for bpath, band in sorted(baseline.items()):
            v = dig(m, bpath)
            ok = band_ok(v, band)
            rows.append({
                "signal": bpath, "value": v, "band": fmt_band(band),
                "ok": ok, "strict": strictness_of(profile, bpath),
            })
        per_doc.append({"doc": os.path.basename(path), "rows": rows,
                        "thin": prof["corpus"]["thin"], "sents": prof["corpus"]["n_sentences"]})
    return per_doc


def summarize(per_doc):
    strict_total = strict_pass = adv_total = adv_pass = 0
    for d in per_doc:
        for r in d["rows"]:
            if r["ok"] is None:
                continue
            if r["strict"]:
                strict_total += 1
                strict_pass += 1 if r["ok"] else 0
            else:
                adv_total += 1
                adv_pass += 1 if r["ok"] else 0
    strict_rate = (strict_pass / strict_total) if strict_total else 1.0
    return strict_pass, strict_total, strict_rate, adv_pass, adv_total


def relax_profile(profile, per_doc, out_path):
    """Widen or demote the strict bands that failed on the eval docs, write a new profile."""
    failing = set()
    for d in per_doc:
        for r in d["rows"]:
            if r["strict"] and r["ok"] is False:
                failing.add(r["signal"])
    newp = json.loads(json.dumps(profile))
    for sig in failing:
        band = newp["baseline"][sig]
        if "min" in band:
            band["min"] = round(band["min"] * 0.8, 2)
        if "max" in band:
            band["max"] = round(band["max"] * 1.2, 2)
        band["strict"] = False
        band["note"] = (band.get("note", "") + " [relaxed by roundtrip gate]").strip()
    newp.setdefault("confidence", {}).setdefault("weak_axes", [])
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(newp, f, ensure_ascii=False, indent=2)
    return sorted(failing)


def main():
    ap = argparse.ArgumentParser(description="Round-trip convergence gate for an emitted personal humanizer.")
    ap.add_argument("docs", nargs="+", help="evaluation document(s): held-out author text or a humanized output")
    ap.add_argument("--profile", required=True, help="style_profile.json to test against")
    ap.add_argument("--threshold", type=float, default=1.0,
                    help="minimum strict-band pass rate to count as converged (default 1.0 = all)")
    ap.add_argument("--relax", metavar="OUT", help="on divergence, write a widened profile here")
    args = ap.parse_args()

    profile = json.load(open(args.profile, encoding="utf-8"))
    per_doc = evaluate(profile, args.docs)

    for d in per_doc:
        print(f"\n# {d['doc']}  (sents={d['sents']}{', THIN' if d['thin'] else ''})")
        for r in d["rows"]:
            tag = "n/a " if r["ok"] is None else ("PASS" if r["ok"] else ("FAIL" if r["strict"] else "WARN"))
            vs = "—" if r["value"] is None else (round(r["value"], 2) if isinstance(r["value"], float) else r["value"])
            note = "" if r["strict"] else "  (advisory)"
            print(f"  [{tag}] {r['signal']}: {vs}  target {r['band']}{note}")

    sp, st, rate, ap_, at = summarize(per_doc)
    print(f"\n=== convergence: strict {sp}/{st} ({rate:.0%}), advisory {ap_}/{at} ===")
    converged = rate >= args.threshold
    verdict = "CONVERGED" if converged else "DIVERGED"
    print(f"=== verdict: {verdict} (threshold {args.threshold:.0%}) ===")

    if not converged and args.relax:
        failing = relax_profile(profile, per_doc, args.relax)
        print(f"  wrote relaxed profile -> {args.relax}  (widened+demoted: {', '.join(failing)})")

    return 0 if converged else 1


if __name__ == "__main__":
    sys.exit(main())
