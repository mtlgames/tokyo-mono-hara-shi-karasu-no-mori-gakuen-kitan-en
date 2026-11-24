"""Translation batches (docs/translator-brief.md): split untranslated text, check translator output, merge it back.

    python -X utf8 tools/batches.py split [--size 3500]   work/tl/bNNN.tsv and work/tl/terms_bNNN.txt for untranslated JP
    python -X utf8 tools/batches.py check [bNNN ...]      a batch's .out.tsv; with no batch, all shipped English (check.py)
    python -X utf8 tools/batches.py merge bNNN ... [--overwrite] [--partial]   check, then write the English into
        script/; --partial merges a failing batch's clean rows and queues the failing ones in docs/fit-queue.tsv
    python -X utf8 tools/batches.py fit "text" [--form dlg]        dry-run: wrapped lines and px widths

Copied from the skill's assets/batches.py; the ADAPTER section fits this game (script/ JSON, docs/re/text.md).
Batch TSV: id, speaker, form, limit, JP (JP line breaks shown as " / "). Output: work/tl/bNNN.out.tsv,
id<TAB>English, every id once, same order. English is one line: the merge wraps dialogue/captions/tables by width;
" / " forces a break. Limits: docs/re/engine.md §Width gate.
"""
import json
import re
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

# ---- ADAPTER: this game's text format ----
TOKEN = re.compile(r"\{p[xmn]\}|%[-+0#]*\d*(?:\.\d+)?l?[sdiuxXcf]")  # no space flag: "40% of" is prose  # player-name codes, printf formats
FREE = set()
VARIABLE = r"(?:\{p[xmn]\}|%[-+ 0#]*\d*l?[du])"
RUBY = re.compile(r"\{ruby:([^|}]*)\|([^}]*)\}")
# honorific after a name (kanji/katakana run or a player-name code) -> required English form
HONORIFICS = {"さん": "-san", "くん": "-kun", "君": "-kun", "ちゃん": "-chan", "先輩": "-senpai", "センパイ": "-senpai",
              "先生": "-sensei", "様": "-sama", "さま": "-sama"}
LINE_PX, LINES, CAPTION_PX, CHOICE_B, NAME_CHARS = 464, 3, 336, 29, 17  # insert.LINE_PX etc.
CHAPTER_ORDER = {"ms": 0, "dg": 1, "fd": 2, "fn": 3, "qs": 4, "in": 5}
NO_BREAK = set("@_\\{}")  # in .pwx text (insert.SCRIPT_BAD + braces = markup)


def docs():
    """(path, doc, entries) per script file, story order: speakers, tables, EBOOT, then scripts by chapter."""
    def order(p):
        r = p.relative_to(SCRIPT).as_posix()
        if r.startswith("pw/"):
            stem = p.stem
            return (2, int(stem[2:4]), CHAPTER_ORDER.get(stem[:2], 9), stem)
        return (0 if r == "speakers.json" else 1, 0, 0, r)
    for path in sorted(SCRIPT.rglob("*.json"), key=order):
        doc = json.loads(path.read_text(encoding="utf-8"))
        yield path, doc, doc


def needs_english(entry):
    """Empty JP isn't "untranslated"; EBOOT data the build never replaces (insert.NON_TEXT) isn't either."""
    return is_text(entry) and not entry.get("en")


def is_text(entry):
    """Not blank (a lone full-width space), not EBOOT data (insert.NON_TEXT), not a NON_TEXT_TABLES byte."""
    import insert
    return (bool(entry.get("jp", "").strip(" 　")) and not insert.non_text(entry)
            and entry["id"].split(":")[0] not in NON_TEXT_TABLES)


NON_TEXT_TABLES = {"objhaichi"}  # object placement bytes the extractor read as 1-char strings (b058/b059): never text


def group_of(entry):
    return entry["id"]


def entry_key(entry):
    return entry["id"]


def form_of(entry):
    i = entry["id"]
    if "slot" in entry and i.startswith("eboot:"):
        return "eboot"
    if "lines" in entry:
        return "name"
    if ":ksf:" in i:
        return "choice"
    if entry.get("kind") == "caption":
        return "caption"
    if "speaker" in entry or i.count(":") == 2 and re.match(r"[a-z]{2}\d\d_\d+:\d{3}:", i):
        return "dlg" if entry.get("speaker") else "narr"
    return "table:" + i.split(":")[0]


@lru_cache(None)
def widths():
    import insert
    return insert.font_widths("sysfont18")


@lru_cache(None)
def menu_widths():
    import insert
    return insert.font_widths("advfont14")


NAME_VAR = re.compile(r"\{(p[xmn])\}")
NAME_ENTRY = "W" * 5  # the name entry takes 5 characters per name (work/qa/warp/en/name_entry); W is the widest


@lru_cache(None)
def var_values():
    """{code: longest English value}: pm/pn = the default name or a 5-W player entry, px = the widest nickname
    format (eboot 0x2D3A10-0x2D445C, insert.NAME_EBOOT) with those names (pnyh/pn1 = one W)."""
    eb = {e["id"]: e for e in json.loads((SCRIPT / "eboot.json").read_text(encoding="utf-8"))}
    name = {"pm": max(eb["eboot:2b7830"]["en"], NAME_ENTRY, key=raw_px),
            "pn": max(eb["eboot:2b7838"]["en"], NAME_ENTRY, key=raw_px)}
    forms = ["pn", "pm"] + [e.get("en") or "" for e in eb.values() if 0x2D3A10 <= int(e["id"][6:], 16) <= 0x2D445C]
    # SPLICE_MAX assumes the pmyh buffer, which a long message overwrites, is never read (engine.md §Name codes)
    assert not any("pmyh" in f for f in forms), "a nickname uses pmyh: lower SPLICE_MAX to 160"
    forms = [re.sub(r"p[nm]", lambda m: name[m[0]], re.sub(r"p[nm](?:yh|1)", "W", f)) for f in forms]
    return dict(name, px=max(forms, key=raw_px))


@lru_cache(None)
def var_px():
    return {k: raw_px(v) for k, v in var_values().items()}


def raw_px(s):
    return sum(widths().get(ord(c), 18) for c in s.replace("--", "―"))  # fontpatch.DASH, 18 px


def px(s):
    """Drawn width with each name code at its longest value (§Checks: variables at their longest English value)."""
    v = var_px()
    return raw_px(NAME_VAR.sub("", s)) + sum(v[c] for c in NAME_VAR.findall(s))


def spliced_bytes(s):
    """.pwx message bytes after the name splice: English as full-width stand-ins (insert.to_sjis_text, 2 bytes a
    char, a line break 2), each name code at its longest value."""
    v = var_values()
    return 2 * len(NAME_VAR.sub("", s)) + sum(2 * len(v[c]) for c in NAME_VAR.findall(s))


# name splice (docs/re/engine.md §Name codes): the dialogue pass output goes through a .bss buffer with 308 bytes to
# the next one, and past 322 bytes the pass's stack scratch reaches the pnyh name buffer
SPLICE_MAX = 300


@lru_cache(None)
def table_cols():
    """{stem:col: (max line bytes, max string bytes, max lines)} over the original strings."""
    out = {}
    for path, _, es in docs():
        if path.parent.name == "tables":
            for x in es:
                b = x["jp"].encode("cp932")
                k = col_key(x)
                a, t, n = out.get(k, (0, 0, 0))
                out[k] = (max(a, *map(len, b.split(b"\n"))), max(t, len(b)), max(n, b.count(b"\n") + 1))
    return out


def col_key(x):
    stem, _, col = x["id"].split(":")
    return f"{stem}:{col}"


def table_limit(entry):
    """(line bytes, total bytes, lines): insert.LONG_ROW/LONG_MIN rule, the one the long-build tour passed."""
    line, total, lines = table_cols()[col_key(entry)]
    total = min(total, max(16, 3 * len(entry["jp"].encode("cp932"))))
    if col_key(entry) in TABLE_WRAP:
        line, lines = TABLE_WRAP[col_key(entry)][1], wrapped_lines(col_key(entry))
    return min(line, total), total, lines


@lru_cache(None)
def wrapped_lines(key):
    """Most lines a JP string of a TABLE_WRAP column takes once the box has wrapped it (the box scrolls)."""
    n = TABLE_WRAP[key][0]
    return max(sum(max(1, -(-len(s.encode("cp932")) // n)) for s in x["jp"].split("\n"))
               for path, _, es in docs() if path.parent.name == "tables" for x in es if col_key(x) == key)


# columns whose box wraps by itself every N bytes, mid-word in English: (box wrap, stored line max)
# dungeon Q&A panel body: the box breaks at 38 bytes, a 37-char line touches its right edge (work/qa/warp/w6/dun_tut_qa)
TABLE_WRAP = {"help:08": (38, 35)}


def eboot_limit(entry):
    """Slot bytes; moved to the freed pool when longer (insert.eboot_patch), capped here at 3x the JP."""
    import insert
    if insert.fixed_slot(entry):  # array fields never move
        return insert.eboot_room(entry) - 1
    return max(insert.eboot_room(entry) - 1, 3 * len(entry["jp"].encode(entry["enc"])))


def limit_label(entry):
    f = form_of(entry)
    if f in ("dlg", "narr"):
        return f"{LINES}x{LINE_PX}px"
    if f == "caption":
        return f"{CAPTION_PX}px"
    if f == "choice":
        return f"{CHOICE_B}b"
    if f == "name":
        return f"{NAME_CHARS}ch"
    if f == "eboot":
        return f"{eboot_limit(entry)}b"
    line, total, lines = table_limit(entry)
    return f"{total}b" + (f" {lines}x{line}b" if lines > 1 or line < total else "")


def greedy(words, width, limit):
    out, line = [], ""
    for w in words:
        cand = f"{line} {w}" if line else w
        if line and width(cand) > limit:
            out.append(line)
            line = w
        else:
            line = cand
    return out + [line]


def wrap(text, width, limit, balance=False):
    """Word wrap; " / " and real newlines force a break. balance: the narrowest limit that keeps greedy's line
    count, so a wrapped paragraph never ends in a stub line (§Checks)."""
    out = []
    for para in re.split(r" / |\n", text):
        words = para.split(" ")
        lines = greedy(words, width, limit)
        if balance and len(lines) > 1:
            lo, hi = max(map(width, words)), limit
            while lo < hi:
                mid = (lo + hi) // 2
                lo, hi = (lo, mid) if len(greedy(words, width, mid)) <= len(lines) else (mid + 1, hi)
            lines = greedy(words, width, hi)
        out += lines
    return out


def shape(entry, en):
    """English as stored in script/: wrapped with \\n for this entry's box."""
    f = form_of(entry)
    if f in ("dlg", "narr"):
        return "\n".join(wrap(en, px, LINE_PX, balance=True))
    if f.startswith("table:"):
        jp = entry["jp"].split("\n")
        own = max(len(s.encode("cp932")) for s in jp)
        if len(jp) > 1 and "\n" not in en and " / " not in en and len(en) > own:
            # a multi-line JP box (bubble, dialog) wider-than-JP English on one line can run past the box: the
            # column max is no box width when a column feeds several boxes. Keep the JP line count, balanced.
            words = en.split(" ")
            lim = next(n for n in range(max(map(len, words)), len(en) + 1) if len(greedy(words, len, n)) <= len(jp))
            return "\n".join(greedy(words, len, lim))
        return "\n".join(wrap(en, len, table_limit(entry)[0]))
    return en.replace(" / ", "\n")


def stub(lines):
    """A wrapped (not forced) last line under 6 characters."""
    return len(lines) > 1 and len(lines[-1]) < 6 and px(f"{lines[-2]} {lines[-1]}") > LINE_PX


def width_problems(entry, en):
    f = form_of(entry)
    lines = shape(entry, en).split("\n")
    if f in ("dlg", "narr"):
        out = []
        if len(lines) > LINES or any(px(s) > LINE_PX for s in lines):
            out.append(f"over {LINES} lines of {LINE_PX}px: {[px(s) for s in lines]}")
        if stub(lines):
            out.append(f"stub last line {lines[-1]!r} (reword)")
        if spliced_bytes("\n".join(lines)) > SPLICE_MAX:
            out.append(f"over {SPLICE_MAX} bytes after the name splice ({spliced_bytes(chr(10).join(lines))})")
        return out
    elif f == "caption":
        if len(lines) > 1 or px(lines[0]) > CAPTION_PX:
            return [f"caption over 1 line of {CAPTION_PX}px ({px(lines[0])})"]
    elif f == "choice":
        if len(en) > CHOICE_B or "\n" in en:
            return [f"choice over {CHOICE_B} bytes ({len(en)})"]
    elif f == "name":
        if len(en) > NAME_CHARS:
            return [f"name over {NAME_CHARS} chars ({len(en)})"]
    elif f == "eboot":
        if len(en) > eboot_limit(entry):
            return [f"over {eboot_limit(entry)} bytes ({len(en)})"]
        if 0x2B1E40 <= int(entry["id"][6:], 16) <= 0x2B2038:  # city map / school room list in the red panel
            import engine
            w = sum(menu_widths().get(ord(c), 14) for c in en)
            if w > engine.FLOOR_MAX:
                return [f"list name over {engine.FLOOR_MAX}px in advfont14 ({w})"]
    else:
        line, total, n = table_limit(entry)
        s = "\n".join(lines)
        if len(s) > total or len(lines) > n or any(len(x) > line for x in lines):
            return [f"over {total}b / {n} lines of {line}b: {[len(x) for x in lines]}"]
        lim = TABLE_PX.get(col_key(entry))
        if lim and any(px(x) > lim for x in lines):
            return [f"line over {lim}px: {[px(x) for x in lines]}"]
    return []


# px limits per table column, in sysfont18 px (the box draws smaller, but in proportion): buddy bubble lines of
# 222 px touch the chevron's right border (battle final frame, worker 16)
TABLE_PX = {"buddymes:08": 215}


def encodable(char, entry=None):
    if entry is not None and form_of(entry) in ("dlg", "narr", "caption", "name") and char in NO_BREAK:
        return False
    import insert
    return " " <= char <= "~" or (char in insert.BUTTONS and entry is not None
                                  and form_of(entry) not in ("dlg", "narr", "caption", "name", "choice"))
# ---- end of ADAPTER ----


def kind(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ":
        return "katakana"
    if "一" <= char <= "鿿" or char == "々":
        return "kanji"
    return "other"


def has_term(jp, term):
    """term occurs as a whole kana or kanji run: ミン isn't in タイミング, くも isn't in ぼくも."""
    jp = jp.replace(" / ", "")
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary():
    """[(JP forms, EN forms, avoid forms)] from glossary.md's | JP | EN | max | notes | Avoid | tables."""
    rows = []
    if not GLOSSARY.exists():
        return rows
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [x.strip() for x in cells[4].split("/") if x.strip()] if len(cells) > 4 else []
            jps = [x.strip() for x in cells[0].split("/")]
            if len(cells) > 3 and "(not enforced)" in cells[3]:  # ambiguous kanji (白 = Mao or "white"): list only
                jps = [j + "\0" for j in jps]
            rows.append((jps, [x.strip() for x in cells[1].split("/")], avoid))
    return rows


_CHARS = None


def character_names():
    """JP forms from glossary.md's "## Characters" table (as glossary() spells them)."""
    global _CHARS
    if _CHARS is None:
        _CHARS, section = set(), ""
        for line in (GLOSSARY.read_text(encoding="utf-8").splitlines() if GLOSSARY.exists() else []):
            section = line if line.startswith("## ") else section
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if section == "## Characters" and line.startswith("|") and len(cells) >= 2:
                nf = len(cells) > 3 and "(not enforced)" in cells[3]
                _CHARS |= {x.strip() + ("\0" if nf else "") for x in cells[0].split("/")}
    return _CHARS


def plain_jp(jp):
    return RUBY.sub(r"\1", jp)


def problems(entry, en, terms):
    """Every rule, on one line of English."""
    jp = plain_jp(entry["jp"])
    if not en.strip():
        return ["empty English"]
    out = []
    plain = TOKEN.sub("", en)
    if bad := sorted({c for c in plain if not encodable(c, entry) and c != "\n"}):
        out.append(f"unencodable characters {bad}")
    lit_n = "\\n" in entry["jp"]  # inputproftext keeps literal backslash-n breaks the game expands
    if re.search(r"\\u[0-9a-fA-F]{4}" + ("" if lit_n else r"|\\n"), en) or "\t" in en:
        out.append("escape sequence or tab in the English (use ' / ' for a forced break)")
    want, have = Counter(TOKEN.findall(jp)), Counter(TOKEN.findall(en))
    if form_of(entry) in ("dlg", "narr", "caption", "choice", "name"):  # name codes: same set, order free
        ok = want == have
    else:  # printf: same codes in the same order
        ok = TOKEN.findall(jp) == TOKEN.findall(en)
    if not ok:
        out.append(f"codes differ: JP {dict(want)} EN {dict(have)}")
    if re.search(VARIABLE + r"(st|nd|rd|th)\b", en):
        out.append('ordinal suffix after a variable (write "No. N")')
    en_terms = " ".join(en.replace(" / ", " ").replace("\n", " ").split()).lower()
    for jps, ens, avoid in terms:
        present = any(has_term(jp, j.rstrip("\0")) for j in jps)
        if any(has_term(jp, j) for j in jps) and not any(" ".join(e.split()).lower() in en_terms for e in ens):
            out.append(f"glossary: {jps[0]} -> {ens[0]}")
        # only where the JP term is in the line: "spirit" in dialogue is fine, Spirit for 精神力 is not
        out += [f"glossary Avoid: {a}" for a in avoid if present and re.search(rf"\b{re.escape(a)}\b", en)]
    # honorifics only after a character name or a player-name code: 同様, オレ様, 敵さん, 封札師さま are not names
    chars = character_names()
    names = "|".join(sorted({re.escape(j.rstrip("\0")) for jps, _, _ in terms for j in jps if j in chars},
                            key=len, reverse=True))
    before = rf"(?:\{{p[xmn]\}}{'|' + names if names else ''})"
    for jp_form, en_form in HONORIFICS.items():
        if re.search(before + re.escape(jp_form), jp) and en_form.lower() not in en.lower():
            out.append(f"honorific {jp_form} needs {en_form}")
    return out + width_problems(entry, en)


def index():
    result = {}
    for _, _, entries in docs():
        for e in entries:
            key = entry_key(e)
            if key in result:
                raise ValueError(f"duplicate batch key {key!r}")
            result[key] = e
    return result


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def split(size, only=None):
    """Numbers on from the last batch and leaves out ids already batched, so a repeat run can't duplicate work.
    only: a regex the script path (relative to script/) must match."""
    index()
    TL.mkdir(parents=True, exist_ok=True)
    taken = {r[0] for p in existing() for r in read_tsv(p)}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    batches, cur, chars, cur_file = [], [], 0, None
    for path, _, entries in docs():
        rel = path.relative_to(SCRIPT).as_posix()
        if only and not re.search(only, rel):
            continue
        for e in entries:
            if not needs_english(e) or entry_key(e) in taken:
                continue
            c = len(plain_jp(e["jp"]))
            # a new batch at the size limit, or at a file start once the batch is past half full
            if cur and (chars + c > size or len(cur) >= MAX_ENTRIES or (rel != cur_file and chars > size // 2)):
                batches.append(cur)
                cur, chars = [], 0
            cur.append(e)
            chars += c
            cur_file = rel
    if cur:
        batches.append(cur)
    terms = glossary()
    for batch in batches:
        n += 1
        name = f"b{n:03d}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} already exists")
        rows = [f"{entry_key(e)}\t{e.get('speaker', '')}\t{form_of(e)}\t{limit_label(e)}\t"
                + e["jp"].replace("\n", " / ") for e in batch]
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        jps = " ".join(plain_jp(e["jp"]) + " " + e.get("speaker", "") for e in batch)
        used = sorted({(j.rstrip("\0"), ens[0]) for jpl, ens, _ in terms for j in jpl if has_term(jps, j.rstrip("\0"))})
        (TL / f"terms_{name}.txt").write_text("".join(f"{j}\t{e}\n" for j, e in used)
                                              or "(no glossary terms in this batch)\n", encoding="utf-8", newline="\n")
    print(f"{len(batches)} new batches in {TL}, {len(taken)} ids already batched")


def check_batch(batch, entries, terms):
    skip = lambda i: i in entries and not is_text(entries[i])
    want = [r[0] for r in read_tsv(TL / f"{batch}.tsv") if not skip(r[0])]
    out = TL / f"{batch}.out.tsv"
    if not out.exists():
        return [f"{out.name} missing"], {}
    # spaces kept: runtime-joined EBOOT fragments need their leading space (" info registered.")
    rows = [(r[0], "\t".join(r[1:])) for r in read_tsv(out) if not skip(r[0])]
    bad = []
    if [r[0] for r in rows] != want:
        got = [r[0] for r in rows]
        dup = sorted(i for i, c in Counter(got).items() if c > 1)
        bad.append(f"ids differ: missing {sorted(set(want) - set(got))[:8]} extra {sorted(set(got) - set(want))[:8]} "
                   f"duplicate {dup[:8]} (order must match too)")
    for eid, en in rows:
        if eid in entries:
            bad += [f"{eid}: {p}: {en!r}" for p in problems(entries[eid], en, terms)]
    return bad, {eid: shape(entries[eid], en) for eid, en in rows if eid in entries}


def merge(new, overwrite):
    """Refuses to replace different English unless told to, before anything is written."""
    if not overwrite:
        for _, _, entries in docs():
            for e in entries:
                if entry_key(e) in new and e.get("en") and e["en"] != new[entry_key(e)]:
                    sys.exit(f"{e['id']} would lose {e['en']!r}: pass --overwrite if that is meant")
    changed = 0
    for path, doc, entries in docs():
        touched = False
        for e in entries:
            if entry_key(e) in new and e.get("en") != new[entry_key(e)]:
                e["en"] = new[entry_key(e)]
                touched = True
                changed += 1
        if touched:
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"merged: {changed} entries changed")


def main(argv):
    if not argv or {"-h", "--help"} & set(argv):
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        return split(int(args[args.index("--size") + 1]) if "--size" in args else 3500,
                     args[args.index("--only") + 1] if "--only" in args else None)
    if cmd == "fit":
        form = args[args.index("--form") + 1] if "--form" in args else "dlg"
        e = {"id": "x:000:00", "jp": "", "speaker": "x"} if form == "dlg" else {"id": "x", "jp": "", "kind": form}
        for s in shape(e, args[0]).split("\n"):
            print(f"{px(s):4d}px {len(s):3d}b  {s}")
        return 0
    overwrite, partial = "--overwrite" in args, "--partial" in args
    names = [a for a in args if a not in ("--overwrite", "--partial")]
    entries, terms = index(), glossary()
    if cmd == "check" and not names:
        bad = [f"{i}: {p}: {e['en']!r}" for i, e in entries.items() if e.get("en") for p in problems(e, e["en"], terms)]
        bad += [f"{i}: no English (the build ships the Japanese): {e['jp']!r}"
                for i, e in entries.items() if needs_english(e)]
        # the build inserts the stored lines as they are: a line shape() would re-wrap is over its box
        bad += [f"{i}: stored wrap is not shape()'s (a line over the limit, or unbalanced): {e['en']!r}"
                for i, e in entries.items() if e.get("en") and shape(e, e["en"]) != e["en"]]
        print(f"{len(entries)} entries, {sum(bool(e.get('en')) for e in entries.values())} translated, "
              f"{len(bad)} problems")
        print("\n".join(bad[:200]))
        return 1 if bad else 0
    if cmd not in ("check", "merge") or not names:
        sys.exit(__doc__)
    failed = 0
    for batch in names:
        bad, rows = check_batch(batch, entries, terms)
        failed += bool(bad)
        print(f"{batch}: " + ("OK" if not bad else f"{len(bad)} problems"))
        for line in bad:
            print("  " + line)
        if cmd == "merge" and not bad:
            merge(rows, overwrite)
        elif cmd == "merge" and partial and rows:
            # merge the clean rows; over-limit lines wait in docs/fit-queue.tsv for engine work / a fit pass
            failed_ids = {line.split(": ", 1)[0] for line in bad}
            if any(i not in rows for i in failed_ids):
                print(f"{batch}: not merged: id set problems")
                continue
            queue = ROOT / "docs/fit-queue.tsv"
            old = queue.read_text(encoding="utf-8") if queue.exists() else "id\tEnglish\tproblem\n"
            keep = [ln for ln in old.splitlines()[1:] if ln.split("\t")[0] not in failed_ids]
            new = [f"{i}\t{rows[i].replace(chr(10), ' / ')}\t{p.split(': ', 1)[1].rsplit(': ', 1)[0]}" for i, p in
                   ((line.split(": ", 1)[0], line) for line in bad)]
            queue.write_text("\n".join([old.splitlines()[0], *keep, *dict.fromkeys(new)]) + "\n",
                             encoding="utf-8", newline="\n")
            merge({i: e for i, e in rows.items() if i not in failed_ids}, overwrite)
    return 1 if failed else 0


def _selftest():
    e = {"id": "ms00_01:000:01", "speaker": "白", "jp": "{pm}くん、そう……。\nあなた", "en": ""}
    assert form_of(e) == "dlg" and limit_label(e) == "3x464px"
    assert problems(e, "{pm}, I see...", []) == ["honorific くん needs -kun"]
    assert problems(e, "{pm}-kun, I see...", []) == []
    assert any("codes differ" in p for p in problems(e, "Kazuki-kun, I see...", []))
    long = "word " * 200
    assert any("over 3 lines" in p for p in problems(e, long, []))
    assert shape(e, "a / b") == "a\nb" and "\n" not in shape(e, "short line")
    t = next(x for _, _, es in docs() for x in es if x["id"] == "buddymes:0072:08")   # 2-line JP bubble
    assert shape(t, "Oh, a yakisoba bun...") == "Oh, a yakisoba\nbun..." and shape(t, "Oh!") == "Oh!"
    assert any("unencodable" in p for p in problems(e, "{pm}-kun, under_score", []))
    t = {"id": "item:0001:04", "jp": "パチンコ", "refs": 1, "en": ""}
    assert form_of(t) == "table:item" and not problems(t, "Slingshot", [])
    assert any("over" in p for p in problems(t, "A very long slingshot name here", []))
    f = {"id": "systemtext:0001:00", "jp": "%d個", "en": ""}
    assert not problems(f, "x%d", []) and problems(f, "x%s", [])
    assert has_term("ミンが来た", "ミン") and not has_term("タイミング", "ミン")
    assert px("{pn}") == raw_px(var_values()["pn"]) >= raw_px("WWWWW") and px("{px}") >= px("{pn}-senpai")
    w = "aaaa " * 30 + "end."  # greedy leaves "end." alone; balanced spreads the words
    assert not stub(shape(e, w).split("\n")) and stub(greedy(w.split(" "), px, LINE_PX))
    assert shape(e, "a / Huh?") == "a\nHuh?" and not stub(["a", "Huh?"])  # a forced break is no stub
    print("selftest ok")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(ROOT / "tools"))
    if sys.argv[1:] == ["--selftest"]:
        _selftest()
    else:
        sys.exit(main(sys.argv[1:]))
