import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def test_rom_sha1_listed():
    lines = [l for l in (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    assert lines and all(len(l.split()[0]) == 40 for l in lines)


def test_tbl_importable():
    import tbl  # noqa: F401


def test_credits():
    """Run finder / fill self-check, and gfx/credits/credits.tsv: 3 columns, unique keys, English for every roll run."""
    import credits
    credits.selftest()
    rows = [l.split("\t") for l in credits.TSV.read_text(encoding="utf-8").splitlines()]
    assert all(len(r) == 3 for r in rows), [r for r in rows if len(r) != 3]
    keys = [r[0] for r in rows[1:]]
    assert len(keys) == len(set(keys))
    en = credits.table()
    assert all(en.get(f"roll:{i:03d}") for i in range(240)), [i for i in range(240) if not en.get(f"roll:{i:03d}")]
