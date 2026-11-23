"""unpack_all.py: unpack CROW.PAK fully for recon: nested .pak archives become folders, .zdv files are inflated.

    python -X utf8 tools/unpack_all.py work/iso/PSP_GAME/USRDIR/CROW.PAK work/unpacked
Output path for a nested file: <outer>.pak/<inner path>; an inflated x.zdv is written as x.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pak import Pak, is_pak  # noqa: E402
from zdv import inflate  # noqa: E402


def walk(pak, out):
    for path, off, size, k in pak.files:
        data = pak.read(k)
        if path.endswith(".zdv"):
            try:
                data, path = inflate(data), path[:-4]
            except Exception as e:
                print("zdv?", out / path, len(data), data[:32].hex(" "), e)
        dst = out / path
        if is_pak(data):
            with tempfile.NamedTemporaryFile(delete=False) as t:
                t.write(data)
            try:
                walk(Pak(t.name), dst)
            finally:
                Path(t.name).unlink()
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)


if __name__ == "__main__":
    walk(Pak(sys.argv[1]), Path(sys.argv[2]))
