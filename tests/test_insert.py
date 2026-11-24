"""Insertion (tools/insert.py): English lands where the ids say, everything else stays byte-identical."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import csvb  # noqa: E402
import insert  # noqa: E402
import ksf  # noqa: E402
import pwx  # noqa: E402
from fontpatch import to_sjis_text  # noqa: E402
from source import members  # noqa: E402


class Fixed:
    """Text stand-in: {id: English}, everything else kept."""

    def __init__(self, m):
        self.m = m

    def get(self, x, kind, room=None):
        return None if insert.non_text(x) else self.m.get(x["id"])


@pytest.fixture(scope="module")
def sc():
    return insert.scripts()


def member(path):
    return next(d for p, d in members(path))


def test_no_en_no_edits(sc):
    assert insert.file_edits(Fixed({}), sc) == {}


def test_names_full_width():
    """Names spliced into .pwx text ({px}, nickname formats) must hold no ASCII but the pwx name codes."""
    assert insert.ascii_bytes("Kazuki", "systemtext:0587:00") == to_sjis_text("Kazuki").encode("cp932")
    assert insert.ascii_bytes("Big Bro pnyh", "eboot:2d3b24") == to_sjis_text("Big Bro ").encode("cp932") + b"pnyh"
    assert insert.ascii_bytes("pn1-san", "eboot:2d406c") == b"pn1" + to_sjis_text("-san").encode("cp932")
    assert insert.ascii_bytes("Kazuki", "systemtext:0590:00") == b"Kazuki"


def test_pwx_span_and_speaker(sc):
    d = member("pw/ms/ms00_00.pwx")
    by = {x["id"]: x for x in sc["pw/ms/ms00_00.json"]}
    new = insert.pwx_file(d, "ms00_00", by, {"図書館員": "Librarian"},
                          Fixed({"ms00_00:000:01": "Line one,\nline two!"}))
    old_e, new_e = pwx.entries(d, "ms00_00"), pwx.entries(new, "ms00_00")
    assert [x["id"] for x in old_e] == [x["id"] for x in new_e]
    got = {x["id"]: x for x in new_e}["ms00_00:000:01"]
    assert got["jp"] == to_sjis_text("Line one,\nline two!") and got["speaker"] == to_sjis_text("Librarian")
    # untouched spans keep their text; speaker swapped everywhere it was 図書館員
    for o, n in zip(old_e, new_e):
        if o["id"] != "ms00_00:000:01":
            assert n["jp"] == o["jp"]
            assert n.get("speaker") == (to_sjis_text("Librarian") if o.get("speaker") == "図書館員" else o.get("speaker"))


def test_pwx_rejects_bad_chars(sc):
    d = member("pw/ms/ms00_00.pwx")
    by = {x["id"]: x for x in sc["pw/ms/ms00_00.json"]}
    for bad in ("mail@home", "{oops}", "a_b"):
        with pytest.raises(ValueError):
            insert.pwx_file(d, "ms00_00", by, {}, Fixed({"ms00_00:000:01": bad}))
    with pytest.raises(ValueError):
        insert.speaker_names(Fixed({"図書館員": "W" * (insert.NAME_MAX + 1)}), sc)


def test_ksf_choice_slot(sc):
    key = next(k for k, v in sc.items() if any(x.get("kind") == "choice" for x in v))
    stem = key.rsplit("/", 1)[1][:-5]
    path = next(p for p, _ in members(f"pw/{key.split('/')[1]}/{stem}.ksf"))
    d = member(path)
    first = next(x for x in sc[key] if x.get("kind") == "choice")
    new = insert.ksf_file(d, stem, {x["id"]: x for x in sc[key]}, Fixed({first["id"]: "Tell her"}))
    a = int(first["id"].rsplit(":", 1)[1], 16)
    assert new[a:a + ksf.SLOT] == b"Tell her".ljust(ksf.SLOT, b"\0")
    assert new[:a] == d[:a] and new[a + ksf.SLOT:] == d[a + ksf.SLOT:]
    with pytest.raises(ValueError):
        insert.ksf_file(d, stem, {x["id"]: x for x in sc[key]}, Fixed({first["id"]: "x" * ksf.SLOT}))


def test_table_repoint(sc):
    b = member("app_init.pak/table/item.bin")
    entries = sc["tables/item.json"]
    shared = max(entries, key=lambda x: x["refs"])
    nb = insert.table_file(b, "item", {x["id"]: x for x in entries}, Fixed({shared["id"]: "Hello"}))
    assert sum(raw == b"Hello" for *_, raw in csvb.strings(nb)) == shared["refs"]
    keep = lambda bb, s: [(r, c, raw) for r, c, _, raw in csvb.strings(bb) if raw != s]
    assert keep(nb, b"Hello") == keep(b, shared["jp"].encode("cp932"))
    assert set(csvb.chunks(nb)) == set(csvb.chunks(b))


def test_eboot_in_place(sc):
    import eboot_text
    if not eboot_text.ELF.exists():
        pytest.skip("no decrypted EBOOT")
    d = bytearray(eboot_text.ELF.read_bytes())
    x = next(x for x in sc["eboot.json"] if insert.eboot_room(x) >= 8 and not insert.non_text(x))
    room = insert.eboot_room(x)
    off = int(x["id"].split(":")[1], 16)
    orig = bytes(d)
    insert.eboot_patch(d, Fixed({x["id"]: "Hi"}), {"eboot.json": [x]})
    assert d[off:off + room] == b"Hi".ljust(room, b"\0")
    assert d[:off] == orig[:off] and d[off + room:] == orig[off + room:]
    # too long and nowhere to move: keeps its Japanese
    assert insert.eboot_patch(bytearray(orig), Fixed({x["id"]: "x" * room}), {"eboot.json": [x]}) == orig


def test_eboot_move(sc):
    """A string longer than its slot moves into freed room; every relocated pointer (data word or lui/addiu lo16)
    follows it and nothing else changes outside the string pool."""
    import eboot
    import eboot_text
    if not eboot_text.ELF.exists():
        pytest.skip("no decrypted EBOOT")
    d = bytearray(eboot_text.ELF.read_bytes())
    refs = eboot.pointers(d)
    va = lambda x: int(x["id"].split(":")[1], 16) - eboot.FILE0
    vis = [x for x in sc["eboot.json"] if not insert.non_text(x) and x["refs"] == len(refs.get(va(x), [1]))]
    kinds = lambda x: {p[0] for p in refs[va(x)]}
    data_x = next(x for x in vis if kinds(x) == {"word"})
    code_x = next(x for x in vis if kinds(x) == {"lo"})
    donors = [x for x in vis if x not in (data_x, code_x)][:40]  # shortened to free room
    en = {data_x["id"]: "D" * 40, code_x["id"]: "Quest Complete!", **{x["id"]: "x" for x in donors}}
    insert.eboot_patch(d, Fixed(en), {"eboot.json": [data_x, code_x] + donors})
    new = eboot.pointers(d)
    for x in (data_x, code_x):
        sites = sorted(p[1] for p in refs[va(x)])
        at = [a for a, ps in new.items() if sorted(p[1] for p in ps) == sites]
        assert len(at) == 1, x["id"]
        o = eboot.file_off(d, at[0])
        assert d[o:d.index(b"\0", o)] == en[x["id"]].encode()
    orig = eboot_text.ELF.read_bytes()  # no room this much in its lui window: a lo16 string keeps its Japanese
    assert insert.eboot_patch(bytearray(orig), Fixed({code_x["id"]: "C" * 5000}), {"eboot.json": [code_x]}) == orig
    # a data-word string of any length goes to the new segment past .bss
    d = insert.eboot_patch(bytearray(orig), Fixed({data_x["id"]: "D" * 5000}), {"eboot.json": [data_x]})
    at = [a for a, ps in eboot.pointers(d).items() if ps == refs[va(data_x)]]
    assert len(at) == 1 and at[0] > 0xAB3EC4 and d[eboot.file_off(d, at[0]):].startswith(b"D" * 5000 + b"\0")


def test_eboot_writes_in_range(sc):
    """romdiff gate on the shipped EBOOT: every changed byte is a logged engine write (expected original bytes
    checked), the slot of a string with English (whose original bytes must be its Japanese), a relocated pointer
    to one, the program header table, or the appended string segment. Non-text slots (name-entry grid, ASCII and
    kinsoku tables) are not allowed."""
    import batches
    import eboot
    import eboot_text
    import engine
    import romdiff
    if not eboot_text.ELF.exists():
        pytest.skip("no decrypted EBOOT")
    orig = eboot_text.ELF.read_bytes()
    p = eboot.Patcher(bytearray(orig))
    eng = bytes(engine.patch(p))
    new = bytes(insert.eboot_patch(bytearray(eng), insert.Text("en"), sc))
    text = [x for x in sc["eboot.json"] if batches.is_text(x) and x.get("en")]
    slots = {int(x["id"].split(":")[1], 16): x["slot"] for x in text}
    sites = [s + eboot.FILE0 for va, ps in eboot.pointers(bytearray(orig)).items() if va + eboot.FILE0 in slots
             for _, s, _, _ in ps]
    writes = p.log + [(o, x["jp"].encode(x["enc"]) + b"\0", new[o:o + len(x["jp"].encode(x["enc"])) + 1], x["id"])
                      for x in text for o in [int(x["id"].split(":")[1], 16)]]
    allowed = ([range(o, o + n) for o, n in slots.items()] + [range(s, s + 4) for s in sites]
               + [range(0x2C, 0x2E), range(0x34, 0xC0), range(len(orig), len(new))])
    errs, _ = romdiff.check(orig, new, allowed, writes)
    assert not errs, errs[:10]
    assert len(p.log) >= 38 and all(len(a) == len(b) for _, a, b, _ in p.log)


@pytest.mark.skipif(not (ROOT / "rom").is_dir() or not any((ROOT / "rom").glob("*.iso")), reason="no ROM")
def test_built_iso_changes(tmp_path, sc):
    """romdiff for the rebuilt CROW.PAK (recompressed, so compared leaf by leaf): same leaf set, only the leaves
    build.edits() names changed and exactly to its bytes, every table pointer of an entry with English reads that
    English and every other one its original string; every other ISO file is byte-identical."""
    import build
    import iso9660
    import tables
    out = tmp_path / "en.iso"
    build.build(out)
    want = build.edits(insert.Text("en"))
    en = {x["id"]: x["en"] for f, xs in sc.items() if f.startswith("tables/") for x in xs if x.get("en")}
    seen = set()
    for (p, a), (q, b) in zip(members("", iso=build.ISO), members("", iso=out), strict=True):
        assert p == q
        if a == b:
            assert p not in want or want[p] == a, p
            continue
        seen.add(p)
        assert want.get(p) == b, p
        if p.startswith(insert.TABLE_DIRS) and csvb.chunks(a).get("TblB") is not None:
            stem, first = Path(p).stem, tables.offsets(a)
            for (r, c, op, raw), (r2, c2, _, nraw) in zip(csvb.strings(a), csvb.strings(b), strict=True):
                i = f"{stem}:{first[op][0]:04d}:{first[op][1]:02x}" if op in first else None
                assert (r, c) == (r2, c2) and nraw == (insert.ascii_bytes(en[i], i).replace(b"\r", b"")
                                                       if i in en else raw), (p, r, c)
    assert seen == {p for p, d in want.items() if d is not None}
    import movie
    movies = movie.pmfs()
    with open(build.ISO, "rb") as f, open(out, "rb") as g:
        for (p, lba, n, _), (p2, lba2, n2, _) in zip(iso9660.listing(f), iso9660.listing(g), strict=True):
            assert p == p2
            if p not in (build.CROW, build.EBOOT):
                f.seek(lba * 2048)
                g.seek(lba2 * 2048)
                old, new = f.read(n), g.read(n2)
                assert n == n2 and new == movies.get(p, old), p   # chapter cards: tools/movie.py, same size


def test_non_text_never_marked(sc):
    t = insert.Text("marker")
    cells = [x for x in sc["eboot.json"] if insert.non_text(x)]
    assert len(cells) == 335 and all(  # 241 name-entry/ASCII + 94 glyph/kinsoku/markup tables (phase 6)
t.get(x, "eboot", 3) is None for x in cells)
