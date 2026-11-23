"""Like bplog.py, but print the last hits only, with the C string each named register points at (SJIS decoded):
find the last breakpoint reached before a crash and the text it was handling.

    python -X utf8 tools/debug/bpstr.py ISO --out DIR --warp MS01_00 --mash SPEC [--regs a0,a1,s2] [--keep 30] ADDR..

Prints the last --keep hits when the run ends (end of mash, or PPSSPP closing on a crash).
"""
import argparse, collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg, warp
from pspdbg import psp


def cstr(s, addr, n=200):
    if not 0x08800000 <= addr < 0x0A000000:
        return '-'
    b = s.read(addr, n)
    return b[:b.index(0)].decode('cp932', 'replace') if 0 in b else b.decode('cp932', 'replace') + '...'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('--out', required=True); ap.add_argument('addrs', nargs='+')
    ap.add_argument('--warp'); ap.add_argument('--state'); ap.add_argument('--mash', default='3000:circle')
    ap.add_argument('--regs', default='a0,a1,s2'); ap.add_argument('--keep', type=int, default=30)
    a = ap.parse_args()
    last = collections.deque(maxlen=a.keep)
    s = pspdbg.Session(a.iso, a.out, a.state)
    try:
        f = 0
        if a.warp:
            w = warp.Warp(a.warp); s.bp(warp.ADV_LOAD)
            f = s.play(psp.parse_route(open(os.path.join(warp.ROOT, 'tools', 'routes', 'boot.txt')).read()), w.on_bp)
            while not w.done and f < 6000: f = s.play([(30, set())], w.on_bp, f)
            s.bp_clear(warp.ADV_LOAD)
        for b in a.addrs: s.bp(int(b, 16))

        def hit(s, r):
            last.append(f'f{s.frame():06d} pc={r["pc"]:08x} ra={r["ra"]:08x} ' +
                        ' '.join(f'{k}={r[k]:08x}:{cstr(s, r[k])!r}' for k in a.regs.split(',')))
        s.play(warp.mash_steps(a.mash), hit, f)
    except EOFError as e:
        last.append(f'END: {e}')
    finally:
        print('\n'.join(last))
        s.close()


if __name__ == '__main__':
    main()
