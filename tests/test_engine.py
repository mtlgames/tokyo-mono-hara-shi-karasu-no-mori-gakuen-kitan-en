"""Phase 5: font codec, English font patch, EBOOT engine patch guards."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import eboot  # noqa: E402
import fontpatch  # noqa: E402
from ipk import Font  # noqa: E402
from source import members  # noqa: E402


@pytest.fixture(scope="module")
def fonts():
    return dict(members(*fontpatch.FONTS))


def test_ipk_glyph_roundtrip(fonts):
    for d in fonts.values():
        f = Font(d)
        for k in (0, 100, len(f.codes) - 1):
            f.set_glyph(k, f.glyph(k))
        assert bytes(f.data) == d


def test_fontpatch_fullwidth_is_ascii(fonts):
    for d in fonts.values():
        f, o = Font(fontpatch.patch(d)), Font(d)
        for c in "Ab'z ":
            k = f.codes[fontpatch.code(fontpatch.fw(c))]
            assert f.glyph(k) == o.glyph(o.codes[ord(c)]) and f.metrics(k) == o.metrics(o.codes[ord(c)])


@pytest.mark.skipif(not eboot.ELF.exists(), reason="needs the decrypted EBOOT dump")
def test_engine_patch_guards():
    import engine
    p = eboot.Patcher()
    engine.patch(p)
    with pytest.raises(ValueError):          # a jal has a relocation: refuse to overwrite it
        p.asm(0x08817314, "nop")
