"""source.py: read files straight from the original ISO's CROW.PAK, by the paths unpack_all.py writes
(nested members as <outer.pak>/<inner path>, x.zdv inflated as x). The extractors and tests read here, never work/.

    from source import members
    for path, data in members("pw/", "app_init.pak/table/"): ...
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import zdv  # noqa: E402
from pak import is_pak, parse, unpacked  # noqa: E402


def members(*prefixes, iso=None):
    """Yield (path, bytes) for every unpacked file whose path starts with one of prefixes, in archive order."""
    from build import ISO, crow_pak
    hit = lambda p: p.startswith(prefixes)
    near = lambda d: any(x.startswith(d) or d.startswith(x) for x in prefixes)  # d ends with '/'

    def member(raw, name):
        path = unpacked(name)
        if not (hit(path) or near(path + "/")):
            return
        body = zdv.inflate(raw) if name.endswith(".zdv") else raw
        if is_pak(body):
            ds, _, files = parse(body)
            for p, off, size, _ in files:
                yield from member(body[ds + off:ds + off + size], f"{path}/{p}")
        elif hit(path):
            yield path, body

    pak = crow_pak(iso or ISO)
    for name, _, _, k in pak.files:
        if hit(unpacked(name)) or near(unpacked(name) + "/"):
            yield from member(pak.read(k), name)
