"""CSVB table reader (app_init.pak/table/*.bin, dungeon dNNscr.bin): chunks tag + u32 size (size includes the 8-byte
header): Info (u16 row size, u16 row count, ...), OfsB, KITB, TblB (rows), Term. Layout notes: docs/re/text.md.

    python -X utf8 tools/csvb.py FILE [--rows N] [--find HEX]   # print rows as u16 words
"""
import argparse, struct


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
