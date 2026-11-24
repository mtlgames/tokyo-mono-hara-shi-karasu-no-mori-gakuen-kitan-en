"""Warp to a scenes.txt scene (script/block/set/mash, as warp.py) with code breakpoints set from the start, and print
each hit's registers and the C strings they point at: find which call draws a label and with what x/y.

    python -X utf8 tools/debug/bpscene.py ISO SCENE ADDR.. [--regs a1,a2,a3,t0] [--max 200] [--out DIR]
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg, warp, save
from pspdbg import psp
from bpstr import cstr


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('scene'); ap.add_argument('addrs', nargs='+')
    ap.add_argument('--regs', default='a1,a2,a3,t0'); ap.add_argument('--max', type=int, default=200)
    ap.add_argument('--out', default=os.path.join(warp.ROOT, 'work', 'qa', 'bpscene'))
    a = ap.parse_args()
    sp = warp.parse_spec(warp.load_scenes()[a.scene])
    s = pspdbg.Session(a.iso, a.out)
    n = [0]

    def hit(s, r):
        if r['pc'] not in bps:
            w.on_bp(s, r)
        elif w.done and n[0] < a.max:   # labels may be set in the first frames of the block: bps armed from boot
            n[0] += 1
            print(f'f{s.frame():06d} pc={r["pc"]:08x} ra={r["ra"]:08x} ' +
                  ' '.join(f'{k}={r[k]:08x}:{cstr(s, r[k], 40)!r}' for k in a.regs.split(',')), flush=True)

    bps = [int(x, 16) for x in a.addrs]
    try:
        w = warp.Warp(sp['script'], int(sp.get('block', 0))); s.bp(warp.ADV_LOAD)
        if w.block: s.bp(warp.BLOCK_START)
        for b in bps: s.bp(b)
        f = s.play(psp.parse_route(open(os.path.join(warp.ROOT, 'tools', 'routes', 'boot.txt')).read()), hit)
        while not (w.done and w.block_done) and f < 6000:
            f = s.play([(30, set())], hit, f)
        s.bp_clear(warp.ADV_LOAD)
        if w.block: s.bp_clear(warp.BLOCK_START)
        if 'set' in sp:
            s.run_to(f + 1); save.poke_state(s, sp['set'].split(','))
        steps = (warp.mash_steps(sp['mash']) if 'mash' in sp else []) + psp.parse_route(sp.get('route', ''))
        for st in steps:
            f = s.play([st], hit, f)
        s.shot('final.png')
    finally:
        s.close()


if __name__ == '__main__':
    main()
