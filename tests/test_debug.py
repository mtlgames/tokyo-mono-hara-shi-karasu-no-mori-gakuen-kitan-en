import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "debug"))
import save, warp  # noqa: E402


def test_save_fields_roundtrip(tmp_path):
    src = tmp_path / "src" / save.DIRNAME
    src.mkdir(parents=True)
    b = bytearray(save.SIZE + 1)
    save.put(b, 'size', save.SIZE)
    (src / "DATA.BIN").write_bytes(b)
    save.edit(str(src), str(tmp_path / "out"), ['money=98765', 'chapter=3', 'name_family=七代'])
    out = (tmp_path / "out" / save.DIRNAME / "DATA.BIN").read_bytes()
    assert save.get(out, 'money') == 98765 and save.get(out, 'chapter') == 3
    assert save.get(out, 'name_family') == '七代' and len(out) == len(b)


def test_scene_specs_parse():
    scenes = warp.load_scenes()
    for name, spec in scenes.items():
        sp = warp.parse_spec(spec)
        assert 'script' in sp or 'from' in sp, name
        if 'from' in sp: assert sp['from'] in scenes, name
        if 'set' in sp:
            for a in sp['set'].split(','): assert a.partition('=')[0] in save.FIELDS, name
    assert warp.parse_spec('from=a set=chapter=1 route=6 start;90 -') == {'from': 'a', 'set': 'chapter=1', 'route': '6 start;90 -'}
