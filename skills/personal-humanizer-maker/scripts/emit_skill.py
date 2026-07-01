#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""emit_skill.py — turn a style_profile.json into a standalone personal-humanizer skill.

    python3 emit_skill.py profile.json -o ~/.claude/skills/humanize-taewoo
    python3 emit_skill.py profile.json --print        # preview SKILL.md only

Given the synthesizer's `style_profile.json` (schemas/style_profile.schema.json), this
writes a self-contained skill package that mirrors the hand-made seed:

    humanize-<name>/
    ├── SKILL.md                 # §0 covenant + per-axis rules + workflow + self-check
    ├── scripts/
    │   ├── style_metrics.py     # author baseline bands baked in
    │   └── _profile_core.py     # vendored measurement core (copy of profile_corpus.py)
    └── references/
        ├── style_profile.md     # human-readable profile
        └── examples.md          # before/after mined from the author's writing

Standard library only. The emitter is deterministic: same profile in -> same skill out.
"""
import sys
import os
import re
import json
import shutil
import pprint
import argparse

MAKER_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(MAKER_ROOT, "templates")
REFERENCES = os.path.join(MAKER_ROOT, "references")
PROFILER = os.path.join(MAKER_ROOT, "scripts", "profile_corpus.py")

MAKER_VERSION = "1.0-m3"

AXIS_OF_PREFIX = {
    "sentence": "sentence_architecture",
    "ending": "register_modality",
    "lexical": "lexical_register",
    "cohesion": "cohesion_argument",
    "stance": "stance_voice",
    "figuration": "figuration",
    "formatting": "formatting",
}

AXIS_LABEL = {
    "ko": {
        "sentence_architecture": "문장 건축",
        "register_modality": "종결·화법",
        "lexical_register": "어휘 층위",
        "cohesion_argument": "결속·논증",
        "stance_voice": "태도·시점",
        "figuration": "수사",
        "formatting": "포맷",
    },
    "en": {
        "sentence_architecture": "Sentence architecture",
        "register_modality": "Register & modality",
        "lexical_register": "Lexical register",
        "cohesion_argument": "Cohesion & argument",
        "stance_voice": "Stance & voice",
        "figuration": "Figuration",
        "formatting": "Formatting",
    },
}


# ----------------------------------------------------------------- helpers
def voice_of(disp):
    """Trim a trailing '문체' so phrasings like '{voice}의 문체로' don't double up."""
    d = disp.strip()
    if d.endswith("문체"):
        return d[:-2].rstrip(" ·의")
    return d


def load_profile(path):
    with open(path, encoding="utf-8") as f:
        prof = json.load(f)
    for k in ("profile_name", "language", "baseline", "dimensions", "meta"):
        if k not in prof:
            sys.exit(f"error: style_profile missing required key '{k}'")
    if prof["language"] not in ("ko", "en"):
        sys.exit("error: language must be ko or en")
    return prof


def ironclad_block(lang):
    txt = open(os.path.join(REFERENCES, "ironclad.md"), encoding="utf-8").read()
    m = re.search(rf"<!-- BEGIN {lang} -->(.*?)<!-- END {lang} -->", txt, re.S)
    return m.group(1).strip() if m else ""


def build_baseline_literal(prof):
    """Convert profile.baseline -> the BASELINE dict baked into style_metrics.py."""
    weak = set(prof.get("confidence", {}).get("weak_axes", []))
    out = {}
    for path, spec in prof["baseline"].items():
        entry = {}
        if spec.get("min") is not None:
            entry["min"] = spec["min"]
        if spec.get("max") is not None:
            entry["max"] = spec["max"]
        axis = AXIS_OF_PREFIX.get(path.split(".")[0])
        strict = spec.get("strict", axis not in weak)
        entry["strict"] = bool(strict)
        out[path] = entry
    # deterministic ordering
    return {k: out[k] for k in sorted(out)}


def render_rules(prof):
    lang = prof["language"]
    labels = AXIS_LABEL[lang]
    head = "## 문체·논증 규칙" if lang == "ko" else "## Style & argument rules"
    lines = [head, ""]
    for dim in prof["dimensions"]:
        axis = dim.get("axis_group", "")
        label = labels.get(axis, axis)
        lines.append(f"### {label}")
        if dim.get("summary"):
            lines.append(dim["summary"])
        for r in dim.get("rules", []):
            stmt = r.get("statement", "").strip()
            adv = "" if r.get("strictness", "strict") == "strict" else (
                "  *(권고)*" if lang == "ko" else "  *(advisory)*")
            rid = r.get("id", "")
            prefix = f"**{rid}.** " if rid else ""
            lines.append(f"- {prefix}{stmt}{adv}")
        lines.append("")
    return "\n".join(lines).strip()


def render_intro(prof):
    lang = prof["language"]
    disp = prof.get("display_name", prof["profile_name"])
    voice = voice_of(disp)
    if lang == "ko":
        return (f"이미 있는 한국어 글의 **문장·문단 흐름만** {voice}의 문체로 다듬는다. "
                f"내용·사실·수치·인용은 건드리지 않고 문체·리듬·논증 전개만 입힌다. "
                f"이 스킬은 personal-humanizer-maker가 저자의 샘플에서 자동 생성했다.")
    return (f"Rewrite the **flow of sentences and paragraphs only** of existing English "
            f"text into {disp}'s voice — touching no facts, numbers, or citations, only "
            f"style, rhythm, and argument shape. Auto-generated by personal-humanizer-maker.")


def render_confidence(prof):
    weak = prof.get("confidence", {}).get("weak_axes", [])
    overall = prof.get("confidence", {}).get("overall", "high")
    lang = prof["language"]
    if not weak and overall == "high":
        return ""
    labels = AXIS_LABEL[lang]
    names = ", ".join(labels.get(a, a) for a in weak) if weak else "—"
    note = prof.get("source", {}).get("note", "")
    if lang == "ko":
        body = [f"> **신뢰도: {overall}.** 다음 축은 샘플 근거가 얕아 *권고(advisory)*로만 적용한다 — {names}.",
                "> 해당 축의 규칙은 강제하지 말고, 어색하면 원문 표현을 우선한다."]
        if note:
            body.append(f"> ({note})")
        return "\n".join(body)
    body = [f"> **Confidence: {overall}.** These axes had thin support and apply as *advisory* only — {names}.",
            "> Do not force those axes; prefer the source phrasing when a rule reads awkwardly."]
    if note:
        body.append(f"> ({note})")
    return "\n".join(body)


def render_workflow(prof):
    lang = prof["language"]
    if lang == "ko":
        return ("## 워크플로\n\n"
                "1. **불변 목록 고정.** 원문의 사실·수치·인용·고유명사를 먼저 추려 '건드리지 않을 것'으로 잠근다.\n"
                "2. **논증 먼저, 문장 다음.** 문단별로 결속·논증 규칙으로 흐름을 점검·재배열한 뒤, 문장별로 나머지 규칙을 적용한다.\n"
                "3. **자가검증.** 결과를 `scripts/style_metrics.py`로 측정해 밴드와 대조하고 WARN을 검토한다.\n"
                "4. **의미 대조.** 1의 불변 목록과 결과를 최종 대조해 사실·수치·인용이 보존됐는지 확인한다.\n"
                "5. **출력.** 다듬은 본문만 제시한다. 변경 요약·발견된 사실 오류는 요청 시 별도 보고한다.")
    return ("## Workflow\n\n"
            "1. **Lock the invariants.** List the source's facts, numbers, citations, and proper nouns as 'do not touch'.\n"
            "2. **Argument first, sentences second.** Reorder paragraph flow with the cohesion/argument rules, then apply the rest per sentence.\n"
            "3. **Self-check.** Measure the result with `scripts/style_metrics.py` against the bands and review any WARN.\n"
            "4. **Meaning diff.** Compare the result to the invariant list from step 1 to confirm facts/numbers/citations survived.\n"
            "5. **Output.** Present only the rewritten text. Report change summaries or spotted factual errors separately, on request.")


def render_selfcheck(prof, name):
    lang = prof["language"]
    if lang == "ko":
        return ("## 자가검증 스크립트\n\n"
                "```bash\n"
                f"python3 ~/.claude/skills/{name}/scripts/style_metrics.py <파일.md>\n"
                f"cat 다듬은본문 | python3 ~/.claude/skills/{name}/scripts/style_metrics.py -\n"
                "```\n\n"
                "저자 기준선 밴드가 baked-in 되어 있다. 문체의 '형태'만 측정하며 내용은 평가하지 않는다. "
                "**WARN이 곧 실패는 아니다** — 의미 불변(§0)을 어기면서까지 수치를 맞추지 말 것.")
    return ("## Self-check script\n\n"
            "```bash\n"
            f"python3 ~/.claude/skills/{name}/scripts/style_metrics.py <file.md>\n"
            f"cat rewritten | python3 ~/.claude/skills/{name}/scripts/style_metrics.py -\n"
            "```\n\n"
            "The author's baseline bands are baked in. It measures the *shape* of style only, not content. "
            "**A WARN is not a failure** — never chase a number at the cost of the covenant (§0).")


def build_skill_md(prof, name):
    tmpl = open(os.path.join(TEMPLATES, "SKILL.md.tmpl"), encoding="utf-8").read()
    lang = prof["language"]
    disp = prof.get("display_name", prof["profile_name"])
    voice = voice_of(disp)
    if lang == "ko":
        desc = (f"{voice}의 문체로 한국어 글을 '문장만' 윤문한다. 내용·사실·수치·인용·고유명사는 "
                f"바꾸지 않고 문체·리듬·논증 전개만 입힌다. 트리거 — \"{voice} 문체로\", \"내 문체로 다듬어줘\", "
                f"\"이 글 윤문\". personal-humanizer-maker가 자동 생성한 개인 스킬.")
    else:
        desc = (f"Rewrite English prose into {disp}'s voice — sentences only. Never changes "
                f"content, facts, numbers, citations, or proper nouns; only style, rhythm, and "
                f"argument shape. Triggers — \"in {disp}'s voice\", \"humanize this in my style\". "
                f"A personal skill auto-generated by personal-humanizer-maker.")
    repl = {
        "{{NAME}}": name,
        "{{DISPLAY_NAME}}": disp,
        "{{DESCRIPTION}}": desc,
        "{{INTRO}}": render_intro(prof),
        "{{IRONCLAD}}": ironclad_block(lang),
        "{{CONFIDENCE}}": render_confidence(prof),
        "{{RULES}}": render_rules(prof),
        "{{WORKFLOW}}": render_workflow(prof),
        "{{SELFCHECK}}": render_selfcheck(prof, name),
    }
    out = tmpl
    for k, v in repl.items():
        out = out.replace(k, v)
    # collapse the blank line left by an empty confidence block
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out


def build_style_metrics(prof):
    tmpl = open(os.path.join(TEMPLATES, "style_metrics.py.tmpl"), encoding="utf-8").read()
    baseline = build_baseline_literal(prof)
    # Python literal (True/False/None), not JSON — this is baked into a .py file.
    literal = pprint.pformat(baseline, indent=1, width=92, sort_dicts=False)
    disp = prof.get("display_name", prof["profile_name"])
    out = tmpl.replace("__LANG__", prof["language"])
    out = out.replace("__BASELINE__", literal)
    out = out.replace("{{DISPLAY}}", disp)
    return out


def build_profile_md(prof):
    lang = prof["language"]
    labels = AXIS_LABEL[lang]
    L = []
    L.append(f"# style_profile — {prof.get('display_name', prof['profile_name'])}")
    L.append("")
    src = prof.get("source", {})
    L.append(f"- language: `{lang}`")
    L.append(f"- built from: {', '.join(src.get('build_files', [])) or '—'} "
             f"({src.get('total_chars', 0)} chars)")
    L.append(f"- confidence: {prof.get('confidence', {}).get('overall', '?')}"
             f"  weak axes: {', '.join(prof.get('confidence', {}).get('weak_axes', [])) or 'none'}")
    if src.get("note"):
        L.append(f"- note: {src['note']}")
    L.append("")
    L.append("## Baseline bands")
    L.append("")
    L.append("| signal | band | strict |")
    L.append("|---|---|---|")
    bl = build_baseline_literal(prof)
    for path, band in bl.items():
        lo, hi = band.get("min"), band.get("max")
        rng = (f"[{lo}, {hi}]" if lo is not None and hi is not None
               else f">= {lo}" if lo is not None else f"<= {hi}")
        L.append(f"| `{path}` | {rng} | {band.get('strict', True)} |")
    L.append("")
    L.append("## Dimensions")
    for dim in prof["dimensions"]:
        axis = dim.get("axis_group", "")
        L.append("")
        L.append(f"### {labels.get(axis, axis)}")
        if dim.get("summary"):
            L.append(dim["summary"])
        for r in dim.get("rules", []):
            L.append(f"- **{r.get('id','')}** ({r.get('strictness','strict')}): {r.get('statement','')}")
    return "\n".join(L) + "\n"


def build_examples_md(prof):
    lang = prof["language"]
    head = "# 예문 (before → after)\n" if lang == "ko" else "# Examples (before → after)\n"
    exs = prof.get("examples", [])
    if not exs:
        note = ("> 저자 코퍼스에서 추출된 대표 예문이 아직 없다.\n" if lang == "ko"
                else "> No canonical examples were mined yet.\n")
        return head + "\n" + note
    blocks = [head]
    for i, e in enumerate(exs, 1):
        axis = e.get("axis", "")
        blocks.append(f"\n## {i}. {axis}".rstrip())
        blocks.append(f"\n**before**\n\n> {e.get('before','').strip()}\n")
        blocks.append(f"**after**\n\n> {e.get('after','').strip()}\n")
    return "\n".join(blocks)


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Emit a standalone personal-humanizer skill from a style_profile.json.")
    ap.add_argument("profile", help="path to style_profile.json")
    ap.add_argument("-o", "--out", help="output skill dir (default: ~/.claude/skills/humanize-<name>)")
    ap.add_argument("--print", dest="preview", action="store_true", help="preview SKILL.md to stdout, write nothing")
    args = ap.parse_args()

    prof = load_profile(args.profile)
    name = f"humanize-{prof['profile_name']}"
    skill_md = build_skill_md(prof, name)

    if args.preview:
        print(skill_md)
        return

    out = args.out or os.path.expanduser(f"~/.claude/skills/{name}")
    os.makedirs(os.path.join(out, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(out, "references"), exist_ok=True)

    with open(os.path.join(out, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(skill_md + "\n")
    with open(os.path.join(out, "scripts", "style_metrics.py"), "w", encoding="utf-8") as f:
        f.write(build_style_metrics(prof))
    shutil.copyfile(PROFILER, os.path.join(out, "scripts", "_profile_core.py"))
    with open(os.path.join(out, "references", "style_profile.md"), "w", encoding="utf-8") as f:
        f.write(build_profile_md(prof))
    with open(os.path.join(out, "references", "examples.md"), "w", encoding="utf-8") as f:
        f.write(build_examples_md(prof))

    # confidence sidecar when the build is shaky
    weak = prof.get("confidence", {}).get("weak_axes", [])
    if weak or prof.get("confidence", {}).get("overall") == "low":
        with open(os.path.join(out, "CONFIDENCE.md"), "w", encoding="utf-8") as f:
            f.write(render_confidence(prof).replace("> ", "") + "\n")

    sys.stderr.write(f"emitted skill -> {out}\n")


if __name__ == "__main__":
    main()
