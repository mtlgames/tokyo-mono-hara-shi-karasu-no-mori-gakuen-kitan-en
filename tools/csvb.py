"""CSVB table reader (app_init.pak/table/*.bin, table/*.bin, dungeon dNNscr.bin). Layout: docs/re/text.md.

`CSVB` u32 total size, then chunks tag + u32 size (size includes the 8-byte header): Info (u16 row size, u16 row count,
u16 0, u16 ?), OfsB (u16 byte offsets of the string-pointer fields in a row, 0xFFFF-terminated), KITB (index, not
string-dependent: see text.md), TblB (count fixed-size rows, then a pool of NUL-terminated strings; a pointer field is
a u32 offset from the TblB start, 0 = no string), Term.

    python -X utf8 tools/csvb.py FILE [--rows N] [--find HEX]   # print rows as u16 words
"""
import argparse
import struct


def chunks(b):
    out, o = {}, 8
    while o + 8 <= len(b):
        tag, n = b[o:o + 4], struct.unpack_from('<I', b, o + 4)[0]
        out.setdefault(tag.decode('latin1'), b[o + 8:o + n])
        if tag in (b'Term', b'TERM') or n < 8: break
        o += n
    return out


def rows(b):
    c = chunks(b)
    size, count = struct.unpack_from('<HH', c['Info'], 0)
    t = c['TblB']
    return [t[i * size:(i + 1) * size] for i in range(count)]


def str_cols(b):
    """Row offsets of the string-pointer fields (OfsB)."""
    o = chunks(b)['OfsB']
    cols = [struct.unpack_from('<H', o, i)[0] for i in range(0, len(o) - 1, 2)]
    return cols[:cols.index(0xFFFF)] if 0xFFFF in cols else cols


def strings(b):
    """[(row, col offset, pool offset, raw bytes)] for every non-null string pointer, in row order."""
    c = chunks(b)
    size, count = struct.unpack_from('<HH', c['Info'], 0)
    t = c['TblB']
    out = []
    for r in range(count):
        for col in str_cols(b):
            p = struct.unpack_from('<I', t, r * size + col)[0]
            if p:
                out.append((r, col, p, t[p:t.index(b'\0', p)]))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('file'); ap.add_argument('--rows', type=int, default=20); ap.add_argument('--find')
    a = ap.parse_args()
    b = open(a.file, 'rb').read()
    c = chunks(b)
    print({k: len(v) for k, v in c.items()}, 'Info', c['Info'].hex(' '))
    for i, r in enumerate(rows(b)):
        if a.find and bytes.fromhex(a.find) not in r: continue
        if i >= a.rows and not a.find: break
        w = struct.unpack(f'<{len(r) // 2}H', r[:len(r) // 2 * 2])
        print(i, ' '.join(f'{x:4x}' for x in w), r.decode('cp932', 'replace').replace('\0', '.')[:40] if b'\x82' in r or b'\x83' in r else '')


if __name__ == '__main__':
    main()
