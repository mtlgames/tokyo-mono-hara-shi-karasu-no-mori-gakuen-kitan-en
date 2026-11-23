"""Find byte patterns in PSP RAM (0x08800000-0x0A000000) at a savestate: every hit address.

    python -X utf8 tools/debug/ramfind.py ISO STATE HEX|"text" [HEX..] [--sjis]

A pattern is hex bytes (`49504b20`) or, with --sjis, text encoded as cp932.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('state'); ap.add_argument('pats', nargs='+')
    ap.add_argument('--sjis', action='store_true'); ap.add_argument('--out', default='work/qa/ramfind')
    a = ap.parse_args()
    pats = [p.encode('cp932') if a.sjis else bytes.fromhex(p) for p in a.pats]
    s = pspdbg.Session(a.iso, a.out, a.state)
    try:
        ram = b''.join(s.read(0x08800000 + o, 0x100000) for o in range(0, 0x1800000, 0x100000))
    finally:
        s.close()
    for p in pats:
        i = ram.find(p)
        hits = []
        while i >= 0 and len(hits) < 50:
            hits.append(i)
            i = ram.find(p, i + 1)
        print(p.hex(), ' '.join(f'{0x08800000 + h:08x}' for h in hits) or 'none')


if __name__ == '__main__':
    main()
