#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_roundtrip.py — the convergence gate's self-consistency + divergence behavior.

Builds a profile from the ko fixture, then checks:
  * the source doc converges on its own bands (exit 0),
  * a stylistically different doc diverges (exit 1) and --relax writes a widened profile.
Standard library only.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCR = ROOT / "skills" / "personal-humanizer-maker" / "scripts"
KOFIX = ROOT / "tests" / "fixtures" / "ko_sample.md"

failures = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        failures.append(msg)


CASUAL = ("오늘은 그냥 이런저런 얘기를 해보려고 해요. 사실 별거 없어요! "
          "그냥 요즘 느낀 걸 적는 거죠 뭐. 재밌지 않나요? ㅎㅎ 다들 그렇게 살잖아요.\n\n"
          "아무튼 오늘도 화이팅이에요~ 내일 봐요!")


def run(args):
    return subprocess.run([sys.executable, str(SCR / "roundtrip_check.py")] + args,
                          capture_output=True, text=True)


def main():
    tmp = Path(tempfile.mkdtemp(prefix="phm_rt_"))
    quant = tmp / "quant.json"
    dims = tmp / "dims"
    dims.mkdir()
    style = tmp / "style.json"

    subprocess.run([sys.executable, str(SCR / "profile_corpus.py"), "--lang", "ko",
                    str(KOFIX), "-o", str(quant)], capture_output=True, text=True, check=True)
    for ax in ["sentence_architecture", "register_modality", "lexical_register",
               "cohesion_argument", "stance_voice", "figuration", "formatting"]:
        (dims / f"{ax}.json").write_text(json.dumps({
            "axis_group": ax, "language": "ko", "confidence": "high", "sample_support": 8,
            "observations": ["x"], "rules": [{"id": "X1", "statement": "x", "strictness": "strict"}],
            "exemplars": [],
        }, ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(SCR / "build_profile.py"), "--quant", str(quant),
                    "--dims", str(dims), "--name", "fx", "-o", str(style)],
                   capture_output=True, text=True, check=True)

    print("[self-consistency] source doc vs its own bands")
    r = run(["--profile", str(style), str(KOFIX)])
    check(r.returncode == 0, "source document CONVERGES on its own profile (exit 0)")
    check("CONVERGED" in r.stdout, "verdict prints CONVERGED")

    print("[divergence] casual ~요체 text vs formal bands")
    casual = tmp / "casual.md"
    casual.write_text(CASUAL, encoding="utf-8")
    relaxed = tmp / "relaxed.json"
    r = run(["--profile", str(style), str(casual), "--relax", str(relaxed)])
    check(r.returncode == 1, "stylistically different doc DIVERGES (exit 1)")
    check(relaxed.exists(), "--relax wrote a widened profile")

    print()
    if failures:
        print(f"FAILED: {len(failures)} check(s)")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
