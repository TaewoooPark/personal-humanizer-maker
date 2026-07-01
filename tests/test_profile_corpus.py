#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_profile_corpus.py — smoke + signal tests for the quantitative profiler.

Runs the real CLI on the committed ko/en fixtures, checks the output against the
required keys of schemas/quant_profile.schema.json, and asserts that the headline
signals for each language actually fire. Standard library only; exits non-zero on
failure so it doubles as a CI gate.

    python3 tests/test_profile_corpus.py
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILER = ROOT / "skills" / "personal-humanizer-maker" / "scripts" / "profile_corpus.py"
SCHEMA = ROOT / "schemas" / "quant_profile.schema.json"
FIX = ROOT / "tests" / "fixtures"

failures = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        failures.append(msg)


def run(lang, path):
    out = subprocess.run(
        [sys.executable, str(PROFILER), "--lang", lang, str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(out)


def required_keys(schema):
    top = schema["required"]
    metric_axes = schema["properties"]["metrics"]["required"]
    return top, metric_axes


def main():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    top_req, axes_req = required_keys(schema)

    print("[ko] fixtures/ko_sample.md")
    ko = run("ko", FIX / "ko_sample.md")
    check(all(k in ko for k in top_req), f"top-level keys present {top_req}")
    check(all(a in ko["metrics"] for a in axes_req), f"7 axis groups present {axes_req}")
    check(ko["language"] == "ko", "language == ko")
    check(ko["meta"]["schema_version"] == "1.0", "schema_version == 1.0")
    check(ko["corpus"]["n_sentences"] >= 6, f"n_sentences >= 6 (got {ko['corpus']['n_sentences']})")
    e = ko["metrics"]
    check(e["ending"]["declarative_ratio"] >= 0.8,
          f"KO declarative ―다체 >= 0.8 (got {e['ending']['declarative_ratio']})")
    check(e["ending"]["spoken_count"] == 0,
          f"KO spoken/honorific == 0 (got {e['ending']['spoken_count']})")
    check(e["lexical"]["gloss_count"] >= 2,
          f"KO English glosses >= 2 (got {e['lexical']['gloss_count']})")
    check(e["cohesion"]["convergence_markers"] >= 1,
          f"KO convergence marker (결국/수렴) >= 1 (got {e['cohesion']['convergence_markers']})")
    check(e["stance"]["self_reference_count"] >= 1,
          f"KO formal self-reference (본 글) >= 1 (got {e['stance']['self_reference_count']})")
    check(e["sentence"]["len_mean"] >= 60,
          f"KO manyeonche mean length >= 60 chars (got {e['sentence']['len_mean']})")

    print("[en] fixtures/en_sample.md")
    en = run("en", FIX / "en_sample.md")
    check(all(k in en for k in top_req), "top-level keys present")
    check(en["language"] == "en", "language == en")
    e = en["metrics"]
    check(15 <= e["sentence"]["len_mean"] <= 60,
          f"EN mean length in words in [15,60] (got {e['sentence']['len_mean']})")
    check(e["lexical"]["register_density"] > 0,
          f"EN Latinate register density > 0 (got {e['lexical']['register_density']})")
    check(e["cohesion"]["transition_markers"] >= 1,
          f"EN transition (however) >= 1 (got {e['cohesion']['transition_markers']})")
    check(e["cohesion"]["convergence_markers"] >= 1,
          f"EN convergence (ultimately) >= 1 (got {e['cohesion']['convergence_markers']})")
    check(e["stance"]["self_reference_count"] >= 1,
          f"EN self-reference (this work) >= 1 (got {e['stance']['self_reference_count']})")

    print()
    if failures:
        print(f"FAILED: {len(failures)} check(s)")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
