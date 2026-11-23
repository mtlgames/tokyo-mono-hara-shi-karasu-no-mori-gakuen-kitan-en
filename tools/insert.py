"""insert.py: script/ text -> game files. Formats: docs/re/text.md; English encoding: docs/re/engine.md.

Two modes:
  en      every entry with a non-empty `en` replaces its original (phase 7); the rest stays Japanese
  marker  every entry becomes `#n` + filler text (phase 5 marker build); n -> id in work/marker_ids.tsv

Encodings: .pwx spans are full-width stand-ins (fontpatch.to_sjis_text, ASCII bytes are commands there); .ksf
choices, CSVB tables and EBOOT strings are C strings and get plain ASCII. Tables grow (new strings appended to the
TblB pool, pointers repointed); .ksf choices and EBOOT strings are slot-bound (SLOT_KSF - 1 bytes, eboot_room()).

    python -X utf8 tools/insert.py          # self-test + counts per kind for both modes
"""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import csvb  # noqa: E402
import ksf  # noqa: E402
import pwx  # noqa: E402
import tables  # noqa: E402
from fontpatch import to_sjis_text  # noqa: E402

SCRIPT = ROOT / "script"
IDS = ROOT / "work" / "marker_ids.tsv"
FILLER = "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs. "
LINE_PX = 464          # ADV dialogue line budget (sysfont18), docs/re/engine.md; the width gate re-measures it
NAME_CHARS = 16        # marker speaker name length
CAPTION_RIGHT = 336    # location captions end here, left of the red-diamond strip (engine.CAP_TEXT x = 0)
SPACE_PX = 9           # sysfont18 space (full-width stand-in) width
SCRIPT_BAD = "@_\\"    # in .pwx text: ＠ hangs the ADV, sysfont18 has no _ glyph, \ draws as ¥ (width gate)
NAME_MAX = 17          # speaker name chars: 18 crashes the game when the name shows (width gate)
# extracted strings that are data, not text (marker build): never replaced. EBOOT file offset ranges, inclusive.
NON_TEXT = [
    (0x2B1154, 0x2B1514, "name-entry grid cells, one char per 4-byte slot (its 英数 page already has A-Z a-z)"),
    (0x2B7F04, 0x2B7F04, "full-width ASCII table (space..【), index = ASCII code - 0x20"),
]


def non_text(x):
    if x["id"].startswith("eboot:"):
        off = int(x["id"].split(":")[1], 16)
        return any(a <= off <= b for a, b, _ in NON_TEXT)
    return False


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def scripts():
    """{json path relative to script/: entries}, sorted, so marker numbers are stable."""
    return {p.relative_to(SCRIPT).as_posix(): load(p) for p in sorted(SCRIPT.rglob("*.json"))}


def font_widths(name):
    """{ASCII code: advance in px} of the English stand-ins in the patched font `name` (e.g. sysfont18)."""
    import fontpatch
    from ipk import Font
    from source import members
    f = Font(fontpatch.patch(next(d for _, d in members(f"app_init.pak/system/font/{name}.ipk"))))
    return {c: f.metrics(f.codes[fontpatch.code(fontpatch.fw(chr(c)))])[0] for c in range(0x20, 0x7F)}


class Text:
    """Replacement text per id for one mode: .get(entry) -> English str or None (keep the original)."""

    def __init__(self, mode, qa=None):
        """qa: {id: text} overrides on top of the mode (width tests: build.py --qa FILE)."""
        self.mode, self.qa = mode, qa or {}
        self.ids = {x["id"]: n for n, x in enumerate(x for es in scripts().values() for x in es)}
        self.widths = font_widths("sysfont18")
        assert self.widths[0x20] == SPACE_PX

    def px(self, s):
        """sysfont18 width of English text (ASCII; anything else counted as a full 18 px cell)."""
        return sum(self.widths.get(ord(c), 18) for c in s)

    def caption(self, x):
        """Caption text right-aligned to CAPTION_RIGHT with leading spaces (None stays None)."""
        t = self._get(x, "caption")
        if t is None:
            return None
        if self.px(t) > CAPTION_RIGHT:
            raise ValueError(f"{x['id']}: caption {self.px(t)} px, max {CAPTION_RIGHT}: {t!r}")
        return " " * ((CAPTION_RIGHT - self.px(t)) // SPACE_PX) + t

    def fill(self, head, nbytes=None, px=None):
        """head + filler, up to nbytes ASCII bytes or px pixels (sysfont18)."""
        out = head
        for c in FILLER * 8:
            if (nbytes is not None and len(out) + 1 > nbytes) or (px is not None and self.px(out + c) > px):
                break
            out += c
        return out.rstrip()

    def get(self, x, kind, room=None):
        """English for entry x. kind: span | caption | speaker | choice | table | eboot. room: byte limit."""
        return self.caption(x) if kind == "caption" else self._get(x, kind, room)

    def _get(self, x, kind, room=None):
        if non_text(x):
            return None
        if x["id"] in self.qa:
            return self.qa[x["id"]]
        if self.mode == "en":
            return x.get("en") or None
        tag = f"#{self.ids[x['id']]}"
        lines = x["jp"].split("\n")
        if kind == "span":  # as wide as the JP line (18 px a char, ~ English length); full-width lines blow the
            # 256 KB .pwx limit, so the width gate tests full lines through overrides instead
            return "\n".join(self.fill(f"{tag} " if i == 0 else "", px=min(LINE_PX, max(160, 18 * len(ln))))
                             for i, ln in enumerate(lines))
        if kind == "speaker":
            return self.fill(f"{tag} ", nbytes=NAME_CHARS)
        if kind == "caption":
            return self.fill(f"{tag} ", nbytes=max(len(tag), len(x["jp"].encode("cp932"))))
        out = [self.fill(f"{tag} " if i == 0 else "", nbytes=max(len(tag) + 1, len(ln.encode("cp932"))))
               for i, ln in enumerate(lines)]
        s = "\n".join(out)
        return s[:room] if room is not None else s

    def save_ids(self):
        if self.mode == "marker":
            IDS.parent.mkdir(parents=True, exist_ok=True)
            IDS.write_text("".join(f"{n}\t{i}\n" for i, n in self.ids.items()), encoding="utf-8")


def ascii_bytes(s, what):
    try:
        return s.encode("ascii")
    except UnicodeEncodeError:
        raise ValueError(f"{what}: C-string text must be ASCII here: {s!r}") from None


# --- .pwx / .ksf -------------------------------------------------------------------------------------------------

def speaker_names(text, sc):
    out = {x["id"]: text.get(x, "speaker") for x in sc.get("speakers.json", [])}
    long = {k: v for k, v in out.items() if v and len(v) > NAME_MAX}
    if long:
        raise ValueError(f"speaker names over {NAME_MAX} chars (crash in game): {long}")
    return out


def pwx_file(d, stem, by, spk, text):
    """Original .pwx bytes -> bytes with the replaced spans (or None if nothing changed)."""
    bl, changed = pwx.blocks(d), False
    for bi, b in enumerate(bl):
        b = bytearray(b)
        for si, (s, e) in reversed(list(enumerate(pwx.spans(b)))):
            x = by.get(f"{stem}:{bi:03d}:{si:02d}")
            if x is None:
                continue
            en = text.get(x, x.get("kind", "span")) if x["jp"] else None
            speaker = x.get("speaker")
            sp_en = spk.get(speaker) if speaker is not None else None
            if en is None and sp_en is None:
                continue
            bad = set((en or "") + (sp_en or "")) & set(SCRIPT_BAD)
            if bad:
                raise ValueError(f"{x['id']}: {''.join(sorted(bad))} not allowed in script text (SCRIPT_BAD)")
            new = pwx.join_speaker(to_sjis_text(sp_en) if sp_en else speaker,
                                   to_sjis_text(en) if en is not None else x["jp"])
            enc = pwx.encode(new)
            try:  # stray ASCII (an unknown {..} tag, a raw brace) would land in the script as a command
                pwx.decode(enc)
            except ValueError as err:
                raise ValueError(f"{x['id']}: {err}: {new!r}") from None
            b[s:e] = enc
            changed = True
        bl[bi] = bytes(b)
    return pwx.pack(bl, pwx.head_size(d)) if changed else None


def ksf_file(d, stem, by, text):
    d, changed = bytearray(d), False
    for a, _ in ksf.choices(bytes(d)):
        x = by.get(f"{stem}:ksf:{a:05x}")
        en = text.get(x, "choice", ksf.SLOT - 1) if x else None
        if en is None:
            continue
        raw = ascii_bytes(en, x["id"])
        if len(raw) >= ksf.SLOT:
            raise ValueError(f"{x['id']}: {len(raw)} bytes, choice slot holds {ksf.SLOT - 1}")
        d[a:a + ksf.SLOT] = raw.ljust(ksf.SLOT, b"\0")
        changed = True
    return bytes(d) if changed else None


# --- CSVB tables -------------------------------------------------------------------------------------------------

def table_file(b, stem, by, text):
    """Append each replaced string to the TblB pool and repoint every pointer to its old offset."""
    c = csvb.chunks(b)
    size, count = struct.unpack_from("<HH", c["Info"], 0)
    t = bytearray(c["TblB"])
    new = {}
    for p, (r, col) in tables.offsets(b).items():
        x = by.get(f"{stem}:{r:04d}:{col:02x}")
        en = text.get(x, "table") if x else None
        if en is not None:
            new[p] = len(t)
            t += ascii_bytes(en, x["id"]).replace(b"\r", b"") + b"\0"
    if not new:
        return None
    t += b"\0" * (-len(t) % 4)
    for r in range(count):
        for col in csvb.str_cols(b):
            o = r * size + col
            p = struct.unpack_from("<I", t, o)[0]
            if p in new:
                struct.pack_into("<I", t, o, new[p])
    return replace_chunk(b, "TblB", bytes(t))


def replace_chunk(b, tag, body):
    """CSVB bytes with chunk `tag` replaced; chunk sizes and the total size follow."""
    out, o = bytearray(b[:8]), 8
    while o + 8 <= len(b):
        tg, n = b[o:o + 4], struct.unpack_from("<I", b, o + 4)[0]
        if tg.decode("latin1") == tag:
            out += tg + struct.pack("<I", len(body) + 8) + body
        else:
            out += b[o:o + n]
        if tg in (b"Term", b"TERM") or n < 8:
            out += b[o + n:]
            break
        o += n
    struct.pack_into("<I", out, 4, struct.unpack_from("<I", b, 4)[0] + len(out) - len(b))
    return bytes(out)


TABLE_DIRS = ("app_init.pak/table/", "table/", "dungeon/")


# --- EBOOT ---------------------------------------------------------------------------------------------------------

def eboot_room(x):
    """Bytes an in-place EBOOT string may use, NUL included: up to the slot's next 4-byte boundary after the original
    NUL (zeros beyond that may be data)."""
    off, n = int(x["id"].split(":")[1], 16), len(x["jp"].encode(x["enc"])) + 1
    return min(x["slot"], (off + n + 3) // 4 * 4 - off)


def eboot_patch(d, text, sc):
    """Write replaced EBOOT strings in place into the ELF bytearray d."""
    for x in sc.get("eboot.json", []):
        room = eboot_room(x)
        en = text.get(x, "eboot", room - 1)
        if en is None:
            continue
        raw = ascii_bytes(en, x["id"])
        if len(raw) >= room:
            raise ValueError(f"{x['id']}: {len(raw)} bytes, slot holds {room - 1}")
        off = int(x["id"].split(":")[1], 16)
        d[off:off + room] = raw.ljust(room, b"\0")
    return d


# --- all -----------------------------------------------------------------------------------------------------------

def file_edits(text, sc=None):
    """{unpacked CROW.PAK path: new bytes} for the script, choices and tables."""
    from source import members
    sc = sc or scripts()
    spk = speaker_names(text, sc)
    out = {}
    stem = lambda p: p.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    for path, d in members("pw/"):
        key = f"pw/{path.split('/')[1]}/{stem(path)}.json"
        by = {x["id"]: x for x in sc.get(key, [])}
        new = (pwx_file(d, stem(path), by, spk, text) if path.endswith(".pwx")
               else ksf_file(d, stem(path), by, text) if path.endswith(".ksf") else None)
        if new is not None:
            out[path] = new
    for path, d in members(*TABLE_DIRS):
        key = f"tables/{stem(path)}.json"
        if d[:4] == b"CSVB" and key in sc:
            new = table_file(d, stem(path), {x["id"]: x for x in sc[key]}, text)
            if new is not None:
                out[path] = new
    return out


if __name__ == "__main__":
    # self-test: a replaced table string is reachable through every pointer that shared it
    from source import members
    path, b = next((p, d) for p, d in members("app_init.pak/table/item.bin"))
    sc = scripts()
    first = sc["tables/item.json"][0]

    class One:
        def get(self, x, kind, room=None):
            return "Hello" if x["id"] == first["id"] else None
    nb = table_file(b, "item", {x["id"]: x for x in sc["tables/item.json"]}, One())
    got = [raw for _, _, _, raw in csvb.strings(nb) if raw == b"Hello"]
    assert len(got) == first["refs"], (len(got), first["refs"])
    keep = lambda bb, s: [(r, c, raw) for r, c, _, raw in csvb.strings(bb) if raw != s]
    assert keep(nb, b"Hello") == keep(b, first["jp"].encode("cp932"))
    print("ok", path, first["id"], "refs", first["refs"])
