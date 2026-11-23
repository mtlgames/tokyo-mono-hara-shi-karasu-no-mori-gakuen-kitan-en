"""Log registers at code breakpoints: frame, pc, ra, a0-a3, t0-t3, s0-s4, and the u32 words at sp..sp+0x40.

    python -X utf8 tools/debug/bplog.py ISO --out DIR ADDR [ADDR..] [--state S | --warp MS01_00] [--mash 3000:circle]

--warp boots to New Game and rewrites the ADV params like warp.py; --mash is warp.py's mash spec.
"""
import argparse, os, sys, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg, warp
from pspdbg import psp

REGS = ['pc', 'ra', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 't2', 't3', 's0', 's1', 's2', 's3', 's4', 'v0']


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('--out', required=True); ap.add_argument('addrs', nargs='+')
    ap.add_argument('--state'); ap.add_argument('--warp'); ap.add_argument('--mash', default='3000:circle')
    ap.add_argument('--max', type=int, default=40, help='stop logging after this many hits')
    a = ap.parse_args()
    s = pspdbg.Session(a.iso, a.out, a.state)
    try:
        f = 0
        if a.warp:
            w = warp.Warp(a.warp); s.bp(warp.ADV_LOAD)
            f = s.play(psp.parse_route(open(os.path.join(warp.ROOT, 'tools', 'routes', 'boot.txt')).read()), w.on_bp)
            while not w.done and f < 6000: f = s.play([(30, set())], w.on_bp, f)
            s.bp_clear(warp.ADV_LOAD)
        bps = [int(x, 16) for x in a.addrs]
        for b in bps: s.bp(b)
        n = [0]

        def hit(s, r):
            n[0] += 1
            if n[0] > a.max:
                for b in bps: s.bp_clear(b)
                return
            stack = struct.unpack('<16I', s.read(r['sp'], 64))
            print(f'f{s.frame():06d} ' + ' '.join(f'{k}={r[k]:08x}' for k in REGS), flush=True)
            print('   sp: ' + ' '.join(f'{x:08x}' for x in stack), flush=True)
        s.play(warp.mash_steps(a.mash), hit, f)
    finally:
        s.close()


if __name__ == '__main__':
    main()
