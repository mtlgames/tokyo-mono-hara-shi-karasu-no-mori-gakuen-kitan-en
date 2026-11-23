"""findtext.py: which game files (CROW.PAK members, unpacked) and EBOOT hold a Japanese string, as cp932 bytes.

    python -X utf8 tools/findtext.py TEXT [TEXT..]       # prints path and offsets per hit

For leftovers seen in a shot: an extracted file means a missed string form; none means graphics (GIM) or code-built.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eboot_text  # noqa: E402
from source import members  # noqa: E402

if __name__ == "__main__":
    pats = [(t, t.encode("cp932")) for t in sys.argv[1:]]
    blobs = list(members(""))
    if eboot_text.ELF.exists():
        blobs.append(("EBOOT", eboot_text.ELF.read_bytes()))
    for t, p in pats:
        hits = []
        for path, d in blobs:
            o = d.find(p)
            offs = []
            while o >= 0 and len(offs) < 5:
                offs.append(hex(o))
                o = d.find(p, o + 1)
            if offs:
                hits.append(f"{path} {' '.join(offs)}")
        print(t, "->", "; ".join(hits) or "nowhere (graphics or code-built)")
