"""Log every CPU write (or --read) to RAM ranges (PPSSPP memory breakpoints): frame, pc, ra, bytes there now.

    python -X utf8 tools/debug/watchw.py ISO --out DIR ADDR:SIZE [ADDR:SIZE..] [--read] [--state S | --warp MS01_00]
        [--sav SAVEDIR] [--route-str "300 -;6 circle"] [--mash 6000:circle,right] [--max 40]

--warp boots to New Game and rewrites the ADV params like warp.py; --mash is warp.py's mash spec.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg, warp
from pspdbg import psp


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('--out', required=True); ap.add_argument('ranges', nargs='+')
    ap.add_argument('--read', action='store_true'); ap.add_argument('--sav'); ap.add_argument('--route-str', default='')
    ap.add_argument('--state'); ap.add_argument('--warp'); ap.add_argument('--mash', default='')
    ap.add_argument('--max', type=int, default=40)
    a = ap.parse_args()
    rs = [(int(x.split(':')[0], 16), int(x.split(':')[1], 0)) for x in a.ranges]
    s = pspdbg.Session(a.iso, a.out, a.state, sav=a.sav)
    try:
        f = 0
        if a.warp:
            w = warp.Warp(a.warp); s.bp(warp.ADV_LOAD)
            f = s.play(psp.parse_route(open(os.path.join(warp.ROOT, 'tools', 'routes', 'boot.txt')).read()), w.on_bp)
            while not w.done and f < 6000: f = s.play([(30, set())], w.on_bp, f)
            s.bp_clear(warp.ADV_LOAD)
        for addr, size in rs:
            s.ws.call('memory.breakpoint.add', address=addr, size=size, enabled=True, log=False,
                      read=a.read, write=not a.read, change=False)
        n = [0]

        def hit(s, r):
            n[0] += 1
            if n[0] > a.max:
                for addr, size in rs: s.ws.call('memory.breakpoint.remove', address=addr, size=size)
                return
            now = ' '.join(s.read(addr, min(size, 16)).hex() for addr, size in rs)
            print(f'f{s.frame():06d} pc={r["pc"]:08x} ra={r["ra"]:08x} a0={r["a0"]:08x} now={now}', flush=True)
        steps = psp.parse_route(a.route_str) + (warp.mash_steps(a.mash) if a.mash else [])
        s.play(steps, hit, f)
    finally:
        s.close()


if __name__ == '__main__':
    main()
