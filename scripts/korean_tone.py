#!/usr/bin/env python3
"""Deterministic Korean voice check (Toss-style 해요체) for the DoseWeek website.

Loads the `ko` locale from the website SOURCE files the generators render (docs/*.json,
import/content.json), the Korean entries of the generators' own label tables
(scripts/render_*.py) and the Korean text of templates/*.html. Generated HTML and the
generated import/*.ko.md downloads are not sources. The shared rules live in
scripts/korean_tone_rules.json. The rule engine below is identical in the iOS, Android and
website repositories; only the loader differs. Exits 1 on any violation or stale allow-list
entry. Not wired into check_site.py until the Korean copy pass lands.

    python3 scripts/korean_tone.py [--report docs/audits/korean-tone-report-YYYYMMDD.json]
"""

import argparse
import ast
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
REPOSITORY = "wonyoungb/doseweek-legal"
LOCALE = "ko"


# ---- LOADER: website sources ----
def json_strings(node, path):
    """Yield (JSON path, string) for every string below node."""
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from json_strings(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from json_strings(value, f"{path}[{index}]")


def json_locale(document):
    """Return (JSON path prefix, Korean subtree) for a locale-keyed source document."""
    if isinstance(document.get("locales"), dict):
        return "locales.ko", document["locales"].get(LOCALE)
    return "ko", document.get(LOCALE)


def json_entries(path, relative):
    prefix, subtree = json_locale(json.loads(path.read_text(encoding="utf-8")))
    if subtree is not None:
        yield from ((relative, key, text) for key, text in json_strings(subtree, prefix))


def generator_entries(path, relative):
    """Korean values of `"ko": ...` entries in the renderers' own label tables."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and key.value == LOCALE:
                strings = [item for item in ast.walk(value) if isinstance(item, ast.Constant)
                           and isinstance(item.value, str)]
                for index, item in enumerate(strings):
                    yield relative, f"line {key.lineno}: ko[{index}]", item.value


class TemplateText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found = []

    def handle_data(self, data):
        if HANGUL_WORD.search(data):
            self.found.append((self.getpos()[0], data.strip()))

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value and HANGUL_WORD.search(value):
                self.found.append((self.getpos()[0], value.strip()))


def template_entries(path, relative):
    parser = TemplateText()
    parser.feed(path.read_text(encoding="utf-8"))
    for line, text in parser.found:
        yield relative, f"line {line}", text


def source_files(root=None):
    root = Path(root or ROOT)
    files = sorted(root.glob("docs/*.json")) + [root / "import/content.json"]
    files += sorted(root.glob("scripts/render_*.py")) + sorted(root.glob("templates/*.html"))
    return [path for path in files if path.exists()]


def load_entries(root=None):
    root = Path(root or ROOT).resolve()
    entries = []
    files = source_files(root)
    for path in files:
        relative = path.resolve().relative_to(root).as_posix()
        if path.suffix == ".json":
            entries += list(json_entries(path, relative))
        elif path.suffix == ".py":
            entries += list(generator_entries(path, relative))
        else:
            entries += list(template_entries(path, relative))
    return entries, [path.resolve().relative_to(root).as_posix() for path in files]


# ---- ENGINE: identical in DoseWeek iOS, Android and website; keep in sync ----
RULES_PATH = SCRIPTS / "korean_tone_rules.json"
ALLOWLIST_PATH = SCRIPTS / "korean_tone_allowlist.json"
RULE_IDS = ("ending", "honorific", "jargon", "glossary", "noun-status")

HANGUL_WORD = re.compile(r"[가-힣]+")
PLACEHOLDER = re.compile(
    r"%(?:\d+\$)?[-#+ 0,(]*\d*(?:\.\d+)?(?:ll|hh|l|h|z|j|t|L|q)?[@dDiuUxXoOfFeEgGcCsSpaA%]"
    r"|\{\{[^{}]*\}\}|\$\{[^{}]*\}|\{[A-Za-z_][A-Za-z0-9_.]*\}"
)
# Quoted terms, code and markup are masked: they are named, not spoken in this voice.
MASKED = re.compile(
    r"‘[^’\n]*’|“[^”\n]*”|\"[^\"\n]*\"|'[^'\n]{1,80}'|「[^」\n]*」|『[^』\n]*』|《[^》\n]*》"
    r"|〈[^〉\n]*〉|`[^`\n]*`|<!\[CDATA\[|\]\]>|<[^<>\n]+>|https?://[^\s)<>]+|\[[^\]\n]*\]\([^)\n]*\)"
)
TOKEN = re.compile("(\\d+)")
SENTENCE_BREAK = re.compile(r"\n+|(?<=[.!?。…])\s+")
TRAILING = " \t.!?。…:;,)]}」』’”\"'*~-–—"
HANGUL_BASE, JONG_COUNT, JUNG_COUNT = 0xAC00, 28, 21
JONG_B, JONG_N = 17, 4


def hangul_parts(syllable):
    """Return (initial, medial, final) indexes, or None for a non-Hangul character."""
    code = ord(syllable) - HANGUL_BASE
    if not 0 <= code < 11172:
        return None
    return code // (JUNG_COUNT * JONG_COUNT), code // JONG_COUNT % JUNG_COUNT, code % JONG_COUNT


def compose(initial, medial, final=0):
    return chr(HANGUL_BASE + (initial * JUNG_COUNT + medial) * JONG_COUNT + final)


def has_final(syllable):
    parts = hangul_parts(syllable)
    return None if parts is None else parts[2] != 0


# medial -> medial after the 해요체 vowel ending contracts into an open syllable
CONTRACT = {8: 9, 13: 14, 11: 10, 20: 6, 18: 4}
OPEN_KEEPS = {0, 1, 4, 5, 6, 9, 10, 14}


def open_syllable_yo(syllable):
    """가 -> 가요, 보 -> 봐요, 되 -> 돼요, 리 -> 려요, 쓰 -> 써요 (stem without a final)."""
    if syllable == "하":
        return "해요"
    initial, medial, _ = hangul_parts(syllable)
    if medial in CONTRACT:
        return compose(initial, CONTRACT[medial]) + "요"
    if medial in OPEN_KEEPS:
        return syllable + "요"
    return syllable + "어요"


def closed_stem_yo(stem):
    """먹 -> 먹어요, 좁 -> 좁아요: vowel harmony on the last stem syllable."""
    parts = hangul_parts(stem[-1]) if stem else None
    if parts and parts[1] in (0, 8):
        return stem + "아요"
    return stem + "어요"


def reu_yo(stem):
    """르 irregular: 다르 -> 달라요, 머무르 -> 머물러요 (stem is the text before 르)."""
    initial, medial, _ = hangul_parts(stem[-1])
    return stem[:-1] + compose(initial, medial, 8) + ("라요" if medial in (0, 8) else "러요")


def copula_yo(before):
    """Noun + 입니다/이다 -> 예요 after a vowel, 이에요 after a final consonant."""
    final = has_final(before[-1]) if before else None
    if final is None:
        return "(이)에요"
    return "이에요" if final else "예요"


class Rules:
    def __init__(self, data):
        self.data = data
        ending = data["ending"]
        self.formal = sorted(ending["formal_rewrites"], key=lambda pair: -len(pair[0]))
        self.plain = sorted(ending["plain_rewrites"], key=lambda pair: -len(pair[0]))
        self.plain_exempt = tuple(ending["plain_exempt_words"])
        self.honorific = [dict(item, regex=re.compile(item["pattern"])) for item in data["honorific"]]
        self.jargon = [dict(item, regex=re.compile(item["pattern"])) for item in data["jargon"]]
        self.glossary = data["glossary"]["terms"]
        self.noun_status = data["noun_status"]


def load_rules(path=RULES_PATH):
    return Rules(json.loads(Path(path).read_text(encoding="utf-8")))


def mask(text):
    """Replace quoted terms, markup and placeholders with private-use tokens."""
    kept = []

    def keep(match):
        kept.append(match.group(0))
        return f"{len(kept) - 1}"

    return PLACEHOLDER.sub(keep, MASKED.sub(keep, text)), kept


def unmask(text, kept):
    while TOKEN.search(text):
        text = TOKEN.sub(lambda match: kept[int(match.group(1))], text)
    return text


def split_sentences(masked):
    return [part.strip() for part in SENTENCE_BREAK.split(masked) if part.strip()]


def sentence_core(sentence):
    """The sentence without trailing punctuation, and that trailing punctuation."""
    core = sentence.rstrip(TRAILING)
    return core, sentence[len(core):]


def last_word(core):
    match = re.search(r"[가-힣]+$", core)
    return match.group(0) if match else ""


def is_formal(word):
    if word.endswith(("십시오", "십시요")):
        return True
    if len(word) < 3 or not word.endswith(("니다", "니까")):
        return False
    before = word[-3]
    parts = hangul_parts(before)
    return before == "습" or (parts is not None and parts[2] == JONG_B)


def is_plain(word, rules):
    if len(word) < 2 or not word.endswith("다") or is_formal(word):
        return False
    return word not in rules.plain_exempt and not word.endswith("보다")


def rewrite_formal(core, rules):
    for old, new in rules.formal:
        if core.endswith(old):
            return core[: -len(old)] + new
    word = last_word(core)
    stem = core[:-3]
    ending = word[-2:]
    before = word[-3]
    if before == "습":
        return closed_stem_yo(stem) if ending == "니다" else stem + "나요"
    if before == "입" and ending == "니다":
        return stem + copula_yo(stem)
    initial, medial, _ = hangul_parts(before)
    opened = compose(initial, medial)
    if ending == "니까":
        return stem + opened + "나요"
    if opened == "르" and stem and hangul_parts(stem[-1]):
        return reu_yo(stem)
    return stem + open_syllable_yo(opened)


def rewrite_plain(core, rules):
    for old, new in rules.plain:
        if core.endswith(old):
            return core[: -len(old)] + new
    word = last_word(core)
    stem = core[:-1]
    if word.endswith("는다") and len(word) > 2:
        return closed_stem_yo(core[:-2])
    if word.endswith("이다"):
        noun = core[:-2]
        return noun + copula_yo(noun)
    parts = hangul_parts(stem[-1]) if stem else None
    if parts is None:
        return core
    if parts[2] == JONG_N:
        opened = compose(parts[0], parts[1])
        if opened == "르" and len(stem) > 1 and hangul_parts(stem[-2]):
            return reu_yo(stem[:-1])
        return stem[:-1] + open_syllable_yo(opened)
    if parts[2] == 0:
        return stem[:-1] + open_syllable_yo(stem[-1])
    return closed_stem_yo(stem)


def rewrite_stacked(match):
    before, eu = match.group(1), match.group(2)
    if eu:
        return before + "을 수 있어요"
    parts = hangul_parts(before)
    if parts and parts[2] == 0:
        return compose(parts[0], parts[1], 8) + " 수 있어요"
    return before + "을 수 있어요"


def rewrite_noun_status(core, noun, replacement):
    """백업 완료 -> 백업했어요, 연결 실패 -> 연결하지 못했어요, 저장 불가 -> 저장할 수 없어요."""
    head = core[: -len(noun)].rstrip()
    if head.endswith("기") and noun in ("완료", "실패"):
        return head[:-1] + ("기를 마쳤어요" if noun == "완료" else "지 못했어요")
    if re.search(r"[가-힣]$", head):
        return head + replacement
    return (head + " " if head else "") + noun + {"완료": "했어요", "실패": "했어요"}.get(noun, "해요" if noun == "불가능" else "예요")


def check_sentence(masked_sentence, rules, whole_message):
    """Return (rule, detail) findings and the suggested 해요체 rewrite of one masked sentence."""
    findings = []
    text = masked_sentence
    suggestion = masked_sentence
    for item in rules.honorific:
        if item["regex"].search(text):
            findings.append(("honorific", item["label"]))
            if item.get("rewrite") == "stacked":
                suggestion = item["regex"].sub(rewrite_stacked, suggestion)
            else:
                suggestion = item["regex"].sub(item["replacement"], suggestion)
            break
    for item in rules.jargon:
        if item["regex"].search(text):
            findings.append(("jargon", f"{item['term']} -> {item['replacement']}"))
            if item["term"] == "해당":
                suggestion = re.sub(r"(?<![가-힣])해당\s", "이 ", suggestion)
            elif not item["replacement"].startswith("("):
                suggestion = item["regex"].sub(item["replacement"], suggestion)
    for item in rules.glossary:
        if item["term"] in text:
            findings.append(("glossary", f"{item['term']} -> {item['replacement']}"))
            suggestion = suggestion.replace(item["term"], item["replacement"])
    core, tail = sentence_core(text)
    word = last_word(core)
    new_core, new_tail = sentence_core(suggestion)
    if is_formal(word):
        findings.append(("ending", word))
        if is_formal(last_word(new_core)):
            new_core = rewrite_formal(new_core, rules)
    elif is_plain(word, rules):
        findings.append(("ending", word))
        if is_plain(last_word(new_core), rules):
            new_core = rewrite_plain(new_core, rules)
    else:
        words = core.split()
        for item in rules.noun_status["endings"]:
            noun = item["noun"]
            if not word.endswith(noun):
                continue
            if len(words) >= rules.noun_status["min_words"] or len(word) > len(noun):
                if whole_message or tail.strip() in (".", "!"):
                    findings.append(("noun-status", noun))
                    if last_word(new_core).endswith(noun):
                        new_core = rewrite_noun_status(new_core, noun, item["replacement"])
            break
    if findings and new_core != sentence_core(suggestion)[0]:
        new_tail = new_tail if new_tail.strip() else "."
        suggestion = new_core + new_tail
    return findings, suggestion


def check_text(text, rules):
    """All findings for one string: dicts with rule, detail, sentence and suggestion."""
    if not HANGUL_WORD.search(text):
        return []
    masked, kept = mask(text)
    sentences = split_sentences(masked)
    results = []
    for sentence in sentences:
        findings, suggestion = check_sentence(sentence, rules, whole_message=len(sentences) == 1)
        for rule, detail in findings:
            results.append({
                "rule": rule,
                "detail": detail,
                "sentence": unmask(sentence, kept),
                "suggestion": unmask(suggestion, kept),
            })
    return results


def load_allowlist(path=ALLOWLIST_PATH):
    path = Path(path)
    if not path.exists():
        return []
    entries = json.loads(path.read_text(encoding="utf-8"))["entries"]
    for entry in entries:
        missing = {"key", "rule", "reason"} - {name for name, value in entry.items() if value}
        if missing or entry["rule"] not in RULE_IDS:
            raise ValueError(f"allow-list entry needs key, a known rule and a reason: {entry}")
    return entries


def allowed(violation, entry):
    return (
        entry["key"] == violation["key"]
        and entry["rule"] == violation["rule"]
        and entry.get("file", violation["file"]) == violation["file"]
        and entry.get("match", "") in violation["sentence"]
    )


def audit(entries, rules, allowlist):
    """Check (file, key, text) entries; return violations, allow-listed hits and stale entries."""
    violations, suppressed, used = [], [], set()
    sentences = 0
    for file, key, text in entries:
        if HANGUL_WORD.search(text):
            sentences += len(split_sentences(mask(text)[0]))
        for finding in check_text(text, rules):
            violation = {"file": file, "key": key, **finding}
            matches = [index for index, entry in enumerate(allowlist) if allowed(violation, entry)]
            if matches:
                used.update(matches)
                suppressed.append(violation)
            else:
                violations.append(violation)
    stale = [entry for index, entry in enumerate(allowlist) if index not in used]
    return violations, suppressed, stale, sentences


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def engine_source():
    """This engine block, whose hash is pinned in the shared rule data."""
    source = Path(__file__).read_text(encoding="utf-8")
    start = source.index("# ---- ENGINE:")
    end = source.index("# ---- END ENGINE ----")
    return source[start:end]


def build_report(entries, files, rules_path=RULES_PATH, allowlist_path=ALLOWLIST_PATH):
    rules = load_rules(rules_path)
    allowlist = load_allowlist(allowlist_path)
    violations, suppressed, stale, sentences = audit(entries, rules, allowlist)
    counts = {rule: sum(item["rule"] == rule for item in violations) for rule in RULE_IDS}
    counts["total"] = len(violations)
    return {
        "schemaVersion": 1,
        "repository": REPOSITORY,
        "generator": "scripts/korean_tone.py",
        "rules": {"path": "scripts/korean_tone_rules.json", "sha256": sha256(rules_path)},
        "allowlist": {
            "path": "scripts/korean_tone_allowlist.json",
            "sha256": sha256(allowlist_path) if Path(allowlist_path).exists() else None,
            "suppressed": len(suppressed),
            "stale": stale,
        },
        "inputs": [{"file": file, "sha256": sha256(ROOT / file)} for file in files],
        "scanned": {"strings": sum(bool(HANGUL_WORD.search(text)) for _, _, text in entries),
                    "sentences": sentences},
        "counts": counts,
        "violations": violations,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check Korean copy against the DoseWeek 해요체 voice.")
    parser.add_argument("--report", type=Path, help="write the JSON report to this path")
    parser.add_argument("--limit", type=int, default=20, help="violations to print (default 20)")
    arguments = parser.parse_args(argv)
    entries, files = load_entries()
    report = build_report(entries, files)
    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for item in report["violations"][: arguments.limit]:
        print(f"{item['file']} {item['key']} [{item['rule']}] {item['sentence']}\n  -> {item['suggestion']}")
    counts = " ".join(f"{rule}={count}" for rule, count in report["counts"].items())
    print(f"korean_tone: {report['scanned']['strings']} strings, {report['scanned']['sentences']} "
          f"sentences; violations {counts}; allow-listed {report['allowlist']['suppressed']}; "
          f"stale allow-list entries {len(report['allowlist']['stale'])}")
    return 1 if report["violations"] or report["allowlist"]["stale"] else 0
# ---- END ENGINE ----


if __name__ == "__main__":
    sys.exit(main())
