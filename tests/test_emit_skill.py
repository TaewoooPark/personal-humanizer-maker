#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_emit_skill.py — the emitter's self-reproduction + well-formedness gate.

Emits a skill from the reconstructed seed profile and checks that the package is
well-formed, the covenant is injected, the baked metrics script is valid Python, and
the emitted checker actually runs. Standard library only; exits non-zero on failure.

    python3 tests/test_emit_skill.py
"""
import json
import py_compile
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EMIT = ROOT / "skills" / "personal-humanizer-maker" / "scripts" / "emit_skill.py"
SEED = ROOT / "tests" / "fixtures" / "seed_profile.taewoo-urp.json"
KOFIX = ROOT / "tests" / "fixtures" / "ko_sample.md"

failures = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        failures.append(msg)


def main():
    tmp = Path(tempfile.mkdtemp(prefix="phm_emit_"))
    out = tmp / "humanize-taewoo-urp"
    subprocess.run([sys.executable, str(EMIT), str(SEED), "-o", str(out)],
                   capture_output=True, text=True, check=True)

    print("[files] emitted package")
    for rel in ["SKILL.md", "scripts/style_metrics.py", "scripts/_profile_core.py",
                "references/style_profile.md", "references/examples.md"]:
        check((out / rel).exists(), f"{rel} exists")

    print("[SKILL.md] structure")
    skill = (out / "SKILL.md").read_text(encoding="utf-8")
    check("name: humanize-taewoo-urp" in skill, "frontmatter name set")
    check("## 0. 철칙 — 의미 불변" in skill, "§0 ironclad covenant injected")
    check("**SA1.**" in skill and "**CA1.**" in skill, "per-axis rules rendered (SA1, CA1)")
    check("*(권고)*" in skill, "advisory rules tagged")
    check("문체의 문체" not in skill, "no doubled '문체의 문체' phrasing")

    print("[style_metrics.py] validity + bands")
    sm = out / "scripts" / "style_metrics.py"
    try:
        py_compile.compile(str(sm), doraise=True)
        check(True, "compiles as valid Python (no bare JSON true/false)")
    except py_compile.PyCompileError as e:
        check(False, f"compiles as valid Python — {e}")
    body = sm.read_text(encoding="utf-8")
    check("sentence.len_mean" in body, "baseline band baked (sentence.len_mean)")
    check('LANG = "ko"' in body, "language flag baked")

    print("[run] emitted checker on ko fixture")
    r = subprocess.run([sys.executable, str(sm), str(KOFIX)], capture_output=True, text=True)
    check(r.returncode in (0, 1), f"checker runs (exit {r.returncode})")
    check("PASS" in r.stdout or "WARN" in r.stdout or "FAIL" in r.stdout,
          "checker prints PASS/WARN/FAIL lines")
    check("의미 불변" in r.stdout, "checker prints the covenant caveat")

    print()
    if failures:
        print(f"FAILED: {len(failures)} check(s)")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
