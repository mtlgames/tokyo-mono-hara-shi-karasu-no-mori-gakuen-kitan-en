"""Hex-dump RAM at a savestate; ADDR may be `*PTR+OFF` (read the u32 at PTR, add OFF).

    python -X utf8 tools/debug/peek.py ISO STATE ADDR [SIZE] [--sjis]
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('state'); ap.add_argument('addr'); ap.add_argument('size', nargs='?', default='0x40')
    ap.add_argument('--sjis', action='store_true')
    a = ap.parse_args()
    s = pspdbg.Session(a.iso, os.path.join(os.path.dirname(a.state) or '.', '_peek'), a.state)
    try:
        if a.addr.startswith('*'):
            ptr, _, off = a.addr[1:].partition('+')
            addr = s.u32(int(ptr, 16)) + int(off or '0', 16)
        else:
            addr = int(a.addr, 16)
        d = s.read(addr, int(a.size, 0))
        for k in range(0, len(d), 16):
            row = d[k:k + 16]
            txt = row.decode('cp932', 'replace') if a.sjis else ''.join(chr(c) if 32 <= c < 127 else '.' for c in row)
            print(f'{addr + k:08x} {row.hex(" ")}  {txt}')
    finally:
        s.close()


if __name__ == '__main__':
    main()
