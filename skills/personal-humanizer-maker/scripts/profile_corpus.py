#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""profile_corpus.py — deterministic quantitative style profiler.

Reads one or more sample documents and emits a `quant_profile.json` conforming to
schemas/quant_profile.schema.json. Language-parametrized (ko/en). Standard library
only — no third-party packages, no network.

    python3 profile_corpus.py --lang ko sample1.md sample2.md -o quant_profile.json
    cat sample.md | python3 profile_corpus.py --lang en -

This is the CODE layer of personal-humanizer-maker: it measures the *shape* of a
voice as distributions (mean / median / p90 / max / stdev), never its content. The
emitter turns these numbers into the target skill's PASS/WARN bands; the multi-agent
layer reads them alongside the raw text to write the qualitative rules.

Morphology note: Korean Sino-Korean ("한자어") density and passive/nominalization are
approximated with curated suffix/lexicon regexes rather than a morphological analyzer,
by design — the whole pipeline stays stdlib-only and dependency-free. These are honest
*signals*, not linguistic ground truth.
"""
import sys
import re
import json
import argparse
import statistics
from collections import Counter

PROFILER_VERSION = "1.0-m1"
SCHEMA_VERSION = "1.0"

# thin-corpus thresholds (chars). Below this, downstream confidence must degrade.
THIN_CHARS = {"ko": 1500, "en": 1200}


# ------------------------------------------------------------------ text prep
def strip_noise(raw):
    """Drop a trailing bibliography/references block so citation lists don't skew stats."""
    parts = re.split(r"^#{0,6}\s*(참고문헌|참고\s*자료|References|Bibliography|Works Cited)\b",
                     raw, maxsplit=1, flags=re.M)
    return parts[0]


def strip_citations(text):
    """Remove [[wikilinks]] and [N] bracket cites; their inner '.' would fake sentence ends."""
    text = re.sub(r"\[\[[^\]]*\]\]", " ", text)          # [[1. Title]]
    text = re.sub(r"\[\^[^\]]*\]", " ", text)             # [^fn]
    text = re.sub(r"\[[0-9][0-9,\s–\-]*\]", " ", text)  # [12], [3, 4]
    return text


def strip_markdown(text):
    """Reduce Markdown to a clean PROSE stream: drop non-prose lines (headings, list
    items, table rows, images) and non-prose blocks (fenced code, math), so tables and
    equations aren't miscounted as gigantic sentences. Paragraph breaks are preserved."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)     # fenced code
    text = re.sub(r"~~~.*?~~~", " ", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)    # html comments
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.S)   # block math
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.S)   # \[ ... \]
    text = re.sub(r"\$[^$\n]{1,200}\$", " ", text)         # inline math
    text = re.sub(r"\\\([^)\n]{1,200}\\\)", " ", text)     # \( ... \)

    kept = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            kept.append("")                                 # keep paragraph breaks
            continue
        if re.match(r"#{1,6}\s", s):                        # heading
            continue
        if re.match(r"([-*+•]|\d+[.)])\s", s):              # list item
            continue
        if s.startswith("|") or re.match(r"\|?\s*:?-{3,}", s):  # table row / separator
            continue
        if re.match(r"!\[", s) or s.startswith("<img"):     # image
            continue
        s = re.sub(r"^>\s?", "", s)                          # blockquote marker
        kept.append(s)
    text = "\n".join(kept)

    text = re.sub(r"`[^`]*`", " ", text)                    # inline code
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)  # links/images -> text
    text = re.sub(r"[*_]{1,3}", "", text)                   # emphasis marks
    return text


def stats(values):
    """Return {mean,median,p90,max,stdev} for a list of numbers (safe on 0/1 items)."""
    if not values:
        return {"mean": 0.0, "median": 0.0, "p90": 0.0, "max": 0.0, "stdev": 0.0}
    s = sorted(values)
    p90 = s[min(len(s) - 1, int(round(0.9 * (len(s) - 1))))]
    return {
        "mean": round(statistics.fmean(s), 2),
        "median": round(statistics.median(s), 2),
        "p90": round(float(p90), 2),
        "max": round(float(max(s)), 2),
        "stdev": round(statistics.pstdev(s), 2) if len(s) > 1 else 0.0,
    }


def per_k(count, chars):
    return round(1000.0 * count / chars, 3) if chars else 0.0


def count_any(text, terms):
    return sum(len(re.findall(re.escape(t), text)) for t in terms)


# ------------------------------------------------------------------ language configs
# Each config supplies: sentence splitter, length unit, long-threshold, and the
# lexicon buckets each axis needs. Adding a 3rd language = add one config here.

KO = {
    "long_threshold": 80,          # chars
    "clause_conn": ["으므로", "므로", "기에", "는바", "만큼", "에 따라", "와 직결", "및",
                    "지만", "는데", "면서", "아서", "어서", "으며", "며", "고자", "도록"],
    "hedge": ["수 있다", "수 있을", "수 있으", "로 보인다", "리라", "ㄹ 것이", "을 것이",
              "기대할 수", "가능성", "전망이다", "여지", "으로 판단된다"],
    # regex-safe: escape the terminal '.' so it isn't a wildcard. 요/죠 only count
    # sentence-finally (요[.!?]); 습니다/입니다 are honorific-style substrings.
    "spoken": [r"요[.!?]", r"죠[.!?]", "습니다", "됩니다", "입니다", "해요", "이에요", "네요", "거든요"],
    "register": ["적", "성", "화", "학", "론", "력", "량", "율", "률", "주의", "규명", "도출",
                 "입증", "구현", "관측", "고찰", "정립", "지대한", "비단", "지극히", "의거"],
    "intensifier": ["지극히", "결코", "비단", "마침내", "비로소", "지대한", "무려", "대단히",
                    "훨씬", "매우", "가장", "과언이 아니"],
    "transition": ["그러나", "그런데", "하지만", "반면", "그럼에도"],
    "juxtaposition": ["한편", "동시에", "예컨대", "또한", "아울러", "나아가", "특히"],
    "convergence": ["결국", "궁극적으로", "요컨대", "따라서", "그리하여", "마침내", "종합하면"],
    "passive": ["된다", "되었", "되며", "되어", "받는다", "받았", "진다", "여진", "해진", "된 ", "됨"],
    "nominalization": ["의 입증", "의 도출", "의 구현", "의 규명", "의 이해", "의 분석", "음을",
                       "것을", "기 위", "함으로", "함에"],
    "self_ref": ["본 연구", "본 글", "본 문서", "본 연구실", "본 학부생", "본고", "본 논문", "본 절"],
    "first_person": ["나는", "내가", "저는", "제가", "우리는", "우리가", "우리의"],
    "evaluation": ["핵심이다", "핵심으로", "중요한", "의의", "단초", "원점", "결정적", "필수적",
                   "주목받", "성과", "관건", "본질적"],
    "metaphor": ["지평", "원점", "초석", "발판", "문을 연", "열었", "지평을", "토대"],
}

EN = {
    "long_threshold": 25,          # words
    "clause_conn": [r"\bbecause\b", r"\balthough\b", r"\bthough\b", r"\bsince\b", r"\bwhile\b",
                    r"\bwhereas\b", r"\bwhich\b", r"\bthat\b", r"\bwho\b", r"\bwhen\b", r"\bif\b",
                    r"\bas\b", r"\bso that\b", r"\bin order to\b"],
    "hedge": [r"\bmay\b", r"\bmight\b", r"\bcould\b", r"\bappears?\b", r"\bseems?\b",
              r"\bsuggests?\b", r"\blikely\b", r"\bis expected\b", r"\bwould\b", r"\bpotentially\b"],
    "spoken": [r"n't\b", r"'re\b", r"'ve\b", r"'ll\b", r"'d\b", r"\bgonna\b", r"\bwanna\b", r"\bok\b"],
    "register": [r"\w{8,}",  # long words as a Latinate proxy
                 r"tion\b", r"sion\b", r"ment\b", r"ity\b", r"ous\b", r"ize\b", r"ical\b", r"ance\b"],
    "intensifier": [r"\bvery\b", r"\bgreatly\b", r"\bprofoundly\b", r"\bremarkably\b",
                    r"\bdecisively\b", r"\bconsiderably\b", r"\bfar\b", r"\bmost\b"],
    "transition": [r"\bhowever\b", r"\byet\b", r"\bbut\b", r"\bnevertheless\b", r"\bnonetheless\b"],
    "juxtaposition": [r"\bmeanwhile\b", r"\blikewise\b", r"\bfor instance\b", r"\bmoreover\b",
                      r"\bfurthermore\b", r"\bin particular\b"],
    "convergence": [r"\bultimately\b", r"\bthus\b", r"\btherefore\b", r"\bin the end\b",
                    r"\bconsequently\b", r"\bhence\b", r"\bin sum\b"],
    "passive": [r"\b(?:is|are|was|were|be|been|being)\s+\w+ed\b",
                r"\b(?:is|are|was|were)\s+\w+en\b"],
    "nominalization": [r"\w+tion\b", r"\w+ment\b", r"\w+ance\b", r"\w+ence\b"],
    "self_ref": [r"\bthis work\b", r"\bthis study\b", r"\bthis paper\b", r"\bthe present\b",
                 r"\bthis research\b"],
    "first_person": [r"\bI\b", r"\bwe\b", r"\bour\b", r"\bmy\b", r"\bus\b"],
    "evaluation": [r"\bcrucial\b", r"\bcentral\b", r"\bkey\b", r"\bessential\b", r"\bsignificant\b",
                   r"\bfundamental\b", r"\bpivotal\b", r"\bcritical\b"],
    "metaphor": [r"\bhorizon\b", r"\bcornerstone\b", r"\bfoundation\b", r"\bopens the door\b",
                 r"\bpaves the way\b", r"\blandscape\b"],
}

CONFIG = {"ko": KO, "en": EN}


def split_sentences(text, lang):
    """Split into sentences WITHIN paragraphs (so a paragraph-less run of list rows or a
    table can't merge into one mega-sentence). KO length is in characters, EN in words.
    Segments must carry script-appropriate content (Hangul for ko, Latin for en)."""
    out = []
    for para in re.split(r"\n\s*\n", text):
        para = " ".join(para.split())          # collapse internal newlines/spaces
        if not para:
            continue
        for c in re.split(r"(?<=[.!?…])\s+", para):
            c = c.strip()
            if not c:
                continue
            if lang == "ko":
                if len(c) > 4 and re.search(r"[가-힣]", c):
                    out.append(c)
            else:
                if len(c.split()) >= 2 and re.search(r"[A-Za-z]", c):
                    out.append(c)
    return out


def ko_is_declarative(s):
    """True if a sentence ends on the plain declarative ―다 (ignoring trailing marks/quotes)."""
    core = s.rstrip(".!?…\"'”’)） ")
    return core.endswith("다")


def sent_len(s, lang):
    return len(s) if lang == "ko" else len(s.split())


# ------------------------------------------------------------------ core measurement
def measure(text_raw, lang):
    cfg = CONFIG[lang]
    body = strip_noise(text_raw)
    wikilink_errors = len(re.findall(r"\]\]\]", body))
    cited = strip_citations(body)
    clean = strip_markdown(cited)
    nchars = len(re.sub(r"\s", "", clean))  # non-space chars for density denominators

    sents = split_sentences(clean, lang)
    n = len(sents)
    lengths = [sent_len(s, lang) for s in sents]
    long_ratio = round(100.0 * sum(x >= cfg["long_threshold"] for x in lengths) / n, 1) if n else 0.0
    clause_chain = round(count_any_re(clean, cfg["clause_conn"]) / n, 3) if n else 0.0

    # ending / register — computed over PROSE sentences, not the raw body
    if lang == "ko":
        decl = sum(1 for s in sents if ko_is_declarative(s))
        ending_dist = Counter(m for s in sents
                              for m in re.findall(r"([가-힣]{1,3})다[.!?…\"'”’)） ]*$", s))
        declarative_ratio = round(decl / n, 3) if n else 0.0
    else:
        decl = sum(1 for s in sents if s.rstrip().endswith("."))
        ending_dist = Counter()
        declarative_ratio = round(decl / n, 3) if n else 0.0
    hedge = count_any_re(clean, cfg["hedge"])
    spoken = count_any_re(clean, cfg["spoken"])

    # lexical
    gloss = len(re.findall(r"\([A-Za-z][^)]{0,40}\)", body))
    tokens = re.findall(r"[0-9A-Za-z가-힣]+", clean)
    ttr = round(len(set(tokens)) / len(tokens), 3) if tokens else 0.0
    register = per_k(count_any_re(clean, cfg["register"]), nchars)
    intens = per_k(count_any_re(clean, cfg["intensifier"]), nchars)

    # cohesion
    tr = count_any_re(clean, cfg["transition"])
    ju = count_any_re(clean, cfg["juxtaposition"])
    cv = count_any_re(clean, cfg["convergence"])
    conn_density = round((tr + ju + cv) / n, 3) if n else 0.0

    # stance
    passive = count_any_re(clean, cfg["passive"]) + count_any_re(clean, cfg["nominalization"])
    passive_rate = round(passive / n, 3) if n else 0.0
    self_ref = count_any_re(body, cfg["self_ref"])
    first_person = count_any_re(clean, cfg["first_person"])
    evaluation = per_k(count_any_re(clean, cfg["evaluation"]), nchars)

    # figuration
    metaphor = count_any_re(clean, cfg["metaphor"])
    rhetorical = round(intens + evaluation, 3)

    # formatting (measured on the ORIGINAL raw text — layout matters here)
    paras = [p for p in re.split(r"\n\s*\n", text_raw) if p.strip()]
    para_lens = [len(re.sub(r"\s", "", p)) for p in paras]
    lines = text_raw.splitlines()
    bullet_lines = sum(1 for ln in lines if re.match(r"\s*([-*+•]|\d+[.)])\s", ln))
    bullet_ratio = round(bullet_lines / len(lines), 3) if lines else 0.0
    heading_density = per_k(len(re.findall(r"^\s{0,3}#{1,6}\s", text_raw, flags=re.M)), max(nchars, 1))
    emoji = count_emoji(text_raw)
    punct_sig = {
        "em_dash": per_k(text_raw.count("—") + text_raw.count("―"), nchars),
        "colon": per_k(text_raw.count(":"), nchars),
        "semicolon": per_k(text_raw.count(";"), nchars),
        "paren": per_k(text_raw.count("("), nchars),
        "ellipsis": per_k(text_raw.count("…") + len(re.findall(r"\.\.\.", text_raw)), nchars),
    }
    citation_style = detect_citation_style(body)

    return {
        "language": lang,
        "corpus": {
            "files": [],  # filled by caller
            "total_chars": len(text_raw),
            "n_sentences": n,
            "n_paragraphs": len(paras),
            "thin": len(text_raw) < THIN_CHARS[lang],
        },
        "metrics": {
            "sentence": {
                **{f"len_{k}": v for k, v in stats(lengths).items()},
                "long_ratio_80": long_ratio,
                "clause_chain_density": clause_chain,
            },
            "ending": {
                "declarative_ratio": declarative_ratio,
                "hedge_projection_ratio": round(hedge / n, 3) if n else 0.0,
                "spoken_count": spoken,
                "distribution": dict(ending_dist.most_common(8)),
            },
            "lexical": {
                "register_density": register,
                "gloss_count": gloss,
                "type_token_ratio": ttr,
                "intensifier_density": intens,
            },
            "cohesion": {
                "connective_density": conn_density,
                "transition_markers": tr,
                "juxtaposition_markers": ju,
                "convergence_markers": cv,
            },
            "stance": {
                "passive_nominalization_rate": passive_rate,
                "self_reference_count": self_ref,
                "first_person_count": first_person,
                "evaluation_density": evaluation,
            },
            "figuration": {
                "metaphor_markers": metaphor,
                "rhetorical_intensity": rhetorical,
            },
            "formatting": {
                "para_len_mean": stats(para_lens)["mean"],
                "bullet_ratio": bullet_ratio,
                "heading_density": heading_density,
                "emoji_count": emoji,
                "punct_signature": punct_sig,
                "citation_style": citation_style,
                "wikilink_error_count": wikilink_errors,
            },
        },
        "meta": {"schema_version": SCHEMA_VERSION, "profiler_version": PROFILER_VERSION},
    }


def count_any_re(text, patterns):
    """Count matches for a list of regex patterns (used for EN word-boundary terms
    and KO literal fragments alike — KO terms are literal so they match as-is).

    IGNORECASE is a no-op for Hangul (no case), so it is safe to apply globally; for
    EN it makes sentence-initial forms ('However', 'This work') match their lexicon
    entries without duplicating every capitalized variant.
    """
    total = 0
    for p in patterns:
        try:
            total += len(re.findall(p, text, flags=re.IGNORECASE))
        except re.error:
            total += len(re.findall(re.escape(p), text, flags=re.IGNORECASE))
    return total


def count_emoji(text):
    n = 0
    for ch in text:
        o = ord(ch)
        if (0x1F300 <= o <= 0x1FAFF) or (0x2600 <= o <= 0x27BF) or o in (0x2705, 0x274C, 0x2B50):
            n += 1
    return n


def detect_citation_style(body):
    if re.search(r"\[\[[^\]]+\]\]", body):
        return "wikilink"
    if re.search(r"\[\^[^\]]+\]", body):
        return "footnote"
    if re.search(r"\[[0-9]+(?:[,\s\-][0-9]+)*\]", body):
        return "bracket"
    return "none"


# ------------------------------------------------------------------ CLI
def load_inputs(paths):
    texts, names = [], []
    if not paths or paths == ["-"]:
        return [sys.stdin.read()], ["<stdin>"]
    for p in paths:
        with open(p, encoding="utf-8") as f:
            texts.append(f.read())
        names.append(p)
    return texts, names


def merge_measure(texts, names, lang):
    """Profile the concatenation so distributions span the whole corpus, then record files."""
    joined = "\n\n".join(texts)
    prof = measure(joined, lang)
    prof["corpus"]["files"] = names
    return prof


def human_summary(prof):
    m = prof["metrics"]
    c = prof["corpus"]
    L = m["sentence"]
    out = []
    out.append(f"lang={prof['language']}  files={len(c['files'])}  chars={c['total_chars']}  "
               f"sents={c['n_sentences']}{'  [THIN]' if c['thin'] else ''}")
    out.append(f"  sentence: mean={L['len_mean']} median={L['len_median']} p90={L['len_p90']} "
               f"max={L['len_max']} stdev={L['len_stdev']} long%={L['long_ratio_80']} "
               f"clause_chain={L['clause_chain_density']}")
    out.append(f"  ending:   declarative={m['ending']['declarative_ratio']} "
               f"hedge={m['ending']['hedge_projection_ratio']} spoken={m['ending']['spoken_count']}")
    out.append(f"  lexical:  register/k={m['lexical']['register_density']} "
               f"gloss={m['lexical']['gloss_count']} ttr={m['lexical']['type_token_ratio']} "
               f"intens/k={m['lexical']['intensifier_density']}")
    out.append(f"  cohesion: conn/sent={m['cohesion']['connective_density']} "
               f"(T{m['cohesion']['transition_markers']}/J{m['cohesion']['juxtaposition_markers']}/"
               f"C{m['cohesion']['convergence_markers']})")
    out.append(f"  stance:   passive/sent={m['stance']['passive_nominalization_rate']} "
               f"self_ref={m['stance']['self_reference_count']} "
               f"1st_person={m['stance']['first_person_count']} eval/k={m['stance']['evaluation_density']}")
    out.append(f"  format:   para_mean={m['formatting']['para_len_mean']} "
               f"bullet%={m['formatting']['bullet_ratio']} emoji={m['formatting']['emoji_count']} "
               f"cite={m['formatting']['citation_style']} ]]]={m['formatting']['wikilink_error_count']}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Quantitative style profiler (ko/en, stdlib-only).")
    ap.add_argument("files", nargs="*", help="sample file paths, or - for stdin")
    ap.add_argument("--lang", required=True, choices=["ko", "en"])
    ap.add_argument("-o", "--out", help="write quant_profile.json here (default: stdout)")
    ap.add_argument("--summary", action="store_true", help="also print a human summary to stderr")
    args = ap.parse_args()

    texts, names = load_inputs(args.files)
    prof = merge_measure(texts, names, args.lang)
    blob = json.dumps(prof, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(blob + "\n")
        sys.stderr.write(f"wrote {args.out}\n")
    else:
        print(blob)
    if args.summary:
        sys.stderr.write(human_summary(prof) + "\n")


if __name__ == "__main__":
    main()
