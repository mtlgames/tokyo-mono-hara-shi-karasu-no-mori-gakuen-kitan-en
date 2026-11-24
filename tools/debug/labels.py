"""labels.py: list the status-page labels (calls to the label maker 0x0892B6B0): call site, x-immediate site and x,
y, systemtext id, refs, JP, EN. Output feeds engine.STATUS_CELLS.

    python -X utf8 tools/debug/labels.py > work/qa/status_labels.txt
"""
import json, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
d = (ROOT / 'work' / 'exe' / 'NPJH50215_EBOOT.BIN').read_bytes()
L, F = 0x08804000, 0xC0
w = lambda va: struct.unpack_from('<I', d, va - L + F)[0]
st = {x['id'][11:15]: x for x in json.loads((ROOT / 'script' / 'tables' / 'systemtext.json').read_text(encoding='utf8'))}
for va in range(0x0892B700, 0x0892C400, 4):
    if w(va) == 0x0C000000 | ((0x0892B6B0 - L) >> 2):
        a1 = a2 = tid = None
        for k in range(va - 4, va - 40, -4):
            i = w(k)
            if i >> 16 == 0x2405 and a1 is None: a1 = (k, i & 0xFFFF)
            if i >> 16 == 0x2406 and a2 is None: a2 = i & 0xFFFF
            if i >> 16 == 0x2404 and tid is None: tid = i & 0xFFFF
        e = st.get(f'{tid:04d}', {}) if tid is not None else {}  # ids 0392-0398 are deduped to 0067-0073
        print(hex(va), a1 and (hex(a1[0]), a1[1]), a2, tid, e.get('refs'), e.get('jp'), e.get('en'))
