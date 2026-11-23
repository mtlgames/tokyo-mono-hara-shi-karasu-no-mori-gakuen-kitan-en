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
        o = at[0] + eboot.FILE0
        assert d[o:d.index(b"\0", o)] == en[x["id"]].encode()
    orig = eboot_text.ELF.read_bytes()  # no room for this much: the string keeps its Japanese
    assert insert.eboot_patch(bytearray(orig), Fixed({data_x["id"]: "D" * 5000}), {"eboot.json": [data_x]}) == orig


def test_non_text_never_marked(sc):
    t = insert.Text("marker")
    cells = [x for x in sc["eboot.json"] if insert.non_text(x)]
    assert len(cells) == 335 and all(  # 241 name-entry/ASCII + 94 glyph/kinsoku/markup tables (phase 6)
t.get(x, "eboot", 3) is None for x in cells)
