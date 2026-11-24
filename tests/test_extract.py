"""Phase 4: every extracted string re-encodes to the original bytes, every text range is covered, and the committed
script/*.json matches a fresh extraction of the original ISO (and EBOOT, when work/exe has it)."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import csvb  # noqa: E402
import eboot_text  # noqa: E402
import extract  # noqa: E402
import ksf  # noqa: E402
import pwx  # noqa: E402
import tables  # noqa: E402
from source import members  # noqa: E402

# Japanese in table pools that no text pointer reaches: SSCR AI / skill / dungeon-trigger script node labels (dev
# names, guess: never drawn; the marker build shows any that are), binary noise, one orphan duplicate in obj.
UNCOVERED = {"dungeonuimoya": 1, "enemy": 6, "enemyai": 1391, "obj": 1, "questvoice": 6, "skill": 247,
             "d00scr": 162, "d01scr": 180, "d02scr": 116, "d03scr": 184, "d04scr": 135, "d05scr": 124,
             "d06scr": 142, "d07scr": 176, "d08scr": 116, "d09scr": 120, "d100scr": 133, "d101scr": 118,
             "d102scr": 101, "d103scr": 101, "d10scr": 105, "d11scr": 109, "d12scr": 219, "d13scr": 142,
             "d14scr": 108, "d15scr": 157, "d16scr": 108}


@pytest.fixture(scope="module")
def pw():
    return list(members("pw/"))


def test_pwx_roundtrip_and_coverage(pw):
    n = 0
    for path, d in pw:
        if not path.endswith(".pwx"):
            continue
        assert pwx.pack(pwx.blocks(d), pwx.head_size(d)) == d, path
        for b in pwx.blocks(d):
            sp = pwx.spans(b)
            inside = set()
            for s, e in sp:
                t = pwx.decode(b[s:e])
                assert pwx.encode(t) == b[s:e], (path, b[s:e])
                assert pwx.join_speaker(*pwx.split_speaker(t)) == t
                inside.update(range(s, e))
                n += 1
            i = 0
            while i < len(b):  # every SJIS char sits in a span
                if pwx.lead(b[i]):
                    assert i in inside, (path, b[i:i + 16])
                    i += 2
                else:
                    i += 1
    assert n == 29758


def test_ksf_choices(pw):
    n = 0
    for path, d in pw:
        if path.endswith(".ksf"):
            for a, s in ksf.choices(d):
                raw = s.encode("cp932")
                assert d[a - 1] == 1 and d[a:a + len(raw)] == raw and not any(d[a + len(raw):a + ksf.SLOT])
                n += 1
    assert n == 1225


def test_tables_roundtrip_and_coverage():
    seen = set()
    for path, b in members(*extract.TABLE_DIRS):
        if b[:4] != b"CSVB":
            continue
        t = csvb.chunks(b)["TblB"]
        for x in tables.entries(b, "t"):
            r, col = int(x["id"].split(":")[1]), int(x["id"].split(":")[2], 16)
            size = int.from_bytes(csvb.chunks(b)["Info"][:2], "little")
            p = int.from_bytes(t[r * size + col:r * size + col + 4], "little")
            assert t[p:p + len(x["jp"].encode("cp932")) + 1] == x["jp"].encode("cp932") + b"\0", (path, x)
        st = extract.stem(path)
        assert len(tables.uncovered(b)) == UNCOVERED.get(st, 0), path
        seen.add(st)
    assert set(UNCOVERED) <= seen


@pytest.mark.skipif(not eboot_text.ELF.exists(), reason="decrypted EBOOT not dumped (docs/re/pak.md)")
def test_eboot_strings():
    d = eboot_text.ELF.read_bytes()
    ss = eboot_text.strings(d)
    for x in ss:
        raw = x["jp"].encode(x["enc"])
        assert d[x["off"]:x["off"] + len(raw) + 1] == raw + b"\0" and d[x["off"] - 1] == 0
        assert x["slot"] > len(raw)
    assert len(ss) == 1258  # 1255 + eboot_text.LONE (瞬 円 装)


def test_merge_keeps_translations():
    old = [{"id": "a", "jp": "あ", "en": "A", "notes": "n"}, {"id": "b", "jp": "い", "en": "B"}]
    new, changed = extract.merge([{"id": "a", "jp": "あ"}, {"id": "b", "jp": "う"}, {"id": "c", "jp": "え"}], old)
    assert new == [{"id": "a", "jp": "あ", "en": "A", "notes": "n"}, {"id": "b", "jp": "う", "en": "B"},
                   {"id": "c", "jp": "え", "en": ""}]
    assert changed == ["b"]


def test_script_matches_extraction():
    """script/*.json holds exactly the extracted entries (ids, jp and context), so no string is missing or stale."""
    fresh = extract.extracted()
    files = {p.relative_to(extract.SCRIPT).as_posix() for p in extract.SCRIPT.rglob("*.json")}
    if not eboot_text.ELF.exists():
        files.discard("eboot.json")
    assert files == set(fresh)
    for rel, entries in fresh.items():
        have = json.loads((extract.SCRIPT / rel).read_text(encoding="utf-8"))
        strip = lambda xs: [{k: v for k, v in x.items() if k not in extract.KEEP} for x in xs]
        assert strip(have) == strip(entries), rel
        assert all("en" in x for x in have), rel
