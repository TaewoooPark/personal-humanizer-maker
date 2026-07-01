#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_all.py — run every test in this directory. Exit non-zero if any fails."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESTS = ["test_profile_corpus", "test_emit_skill", "test_build_profile", "test_roundtrip"]


def main():
    failed = []
    for t in TESTS:
        print(f"\n{'=' * 60}\n{t}\n{'=' * 60}")
        r = subprocess.run([sys.executable, str(HERE / f"{t}.py")])
        if r.returncode != 0:
            failed.append(t)
    print(f"\n{'#' * 60}")
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1
    print(f"ALL {len(TESTS)} TEST FILES PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
