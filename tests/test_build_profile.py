#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_build_profile.py — the CODE analysis chain on committed fixtures.

profile_corpus -> build_profile (auto-derived baseline + merged dims) -> emit_skill,
entirely on the ko fixture so it needs no private data. Exits non-zero on failure.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCR = ROOT / "skills" / "personal-humanizer-maker" / "scripts"
KOFIX = ROOT / "tests" / "fixtures" / "ko_sample.md"
SCHEMA = ROOT / "schemas" / "style_profile.schema.json"

failures = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        failures.append(msg)


# minimal per-axis dimension_profiles (what the agents would emit), enough to assemble.
DIMS = {
    "sentence_architecture": ["짧은 단문을 종속절로 엮는 만연체."],
    "register_modality": ["평서 ―다체로 통일."],
    "lexical_register": ["전문용어 영문 병기."],
    "cohesion_argument": ["전환→병치→수렴으로 단락 착지."],
    "stance_voice": ["피동·명사화와 격식 자기지칭."],
    "figuration": ["절제된 은유 허용."],
    "formatting": ["산문 문단 위주."],
}


def main():
    tmp = Path(tempfile.mkdtemp(prefix="phm_build_"))
    quant = tmp / "quant.json"
    dims = tmp / "dims"
    dims.mkdir()
    style = tmp / "style_profile.json"

    # 1. profile the fixture
    subprocess.run([sys.executable, str(SCR / "profile_corpus.py"), "--lang", "ko",
                    str(KOFIX), "-o", str(quant)], capture_output=True, text=True, check=True)
    check(quant.exists(), "profile_corpus produced quant_profile.json")

    # 2. synthesize dimension_profiles
    for ax, obs in DIMS.items():
        (dims / f"{ax}.json").write_text(json.dumps({
            "axis_group": ax, "language": "ko", "confidence": "high", "sample_support": 8,
            "observations": obs,
            "rules": [{"id": ax[:2].upper() + "1", "statement": obs[0], "strictness": "strict"}],
            "exemplars": [],
        }, ensure_ascii=False), encoding="utf-8")

    # 3. assemble
    subprocess.run([sys.executable, str(SCR / "build_profile.py"),
                    "--quant", str(quant), "--dims", str(dims),
                    "--name", "fixture-ko", "--display", "Fixture KO",
                    "-o", str(style)], capture_output=True, text=True, check=True)
    prof = json.loads(style.read_text(encoding="utf-8"))

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    print("[style_profile] contract + content")
    check(all(k in prof for k in schema["required"]), "all required keys present")
    check(prof["ironclad"] is True, "ironclad covenant flag set true")
    check(len(prof["baseline"]) >= 6, f"baseline auto-derived >= 6 bands (got {len(prof['baseline'])})")
    check(len(prof["dimensions"]) == 7, f"7 dimensions merged (got {len(prof['dimensions'])})")
    check(prof["confidence"]["overall"] in ("high", "medium", "low"), "confidence rolled up")
    check("sentence.len_mean" in prof["baseline"], "sentence length band derived")

    # 4. the assembled profile must emit a working skill
    out = tmp / "humanize-fixture-ko"
    subprocess.run([sys.executable, str(SCR / "emit_skill.py"), str(style), "-o", str(out)],
                   capture_output=True, text=True, check=True)
    check((out / "SKILL.md").exists(), "emit_skill produced a package from the assembled profile")
    r = subprocess.run([sys.executable, str(out / "scripts" / "style_metrics.py"), str(KOFIX)],
                       capture_output=True, text=True)
    check(r.returncode in (0, 1) and "summary:" in r.stdout, "emitted checker runs on the fixture")

    print()
    if failures:
        print(f"FAILED: {len(failures)} check(s)")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
