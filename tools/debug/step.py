"""Play a route from a savestate, shoot the last frame, print the dungeon section/floor, save the new state.

    python -X utf8 tools/debug/step.py ISO STATE OUTSTATE "6 up;30 -;6 right;30 -" [--out DIR] [--every N]

Dungeon walking by hand, one leg per call (docs/re/debug.md "Dungeons"). The dungeon object's section and floor
strings (0x09DF1118 / 0x09DF1158) are printed so each door transition is checked.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg, trace_pw, warp
from pspdbg import psp

SECTION, FLOOR = 0x09DF1118, 0x09DF1158


def cstr(b): return b.split(b'\0')[0].decode('cp932', 'replace')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('state'); ap.add_argument('outstate'); ap.add_argument('route')
    ap.add_argument('--out', default='work/qa/step'); ap.add_argument('--every', type=int, default=0)
    ap.add_argument('--mash', help="warp.py mash spec played before the route, e.g. 9000:circle,cross")
    a = ap.parse_args()
    s = pspdbg.Session(a.iso, a.out, a.state)
    try:
        for b in trace_pw.BPS: s.bp(b)
        f = 0
        for st in (warp.mash_steps(a.mash) if a.mash else []) + psp.parse_route(a.route):
            f = s.play([st], trace_pw.log_load, f)
            if a.every and f % a.every < st[0]: s.shot(f'f{f:06d}.png')
        s.shot('final.png')
        print('section', cstr(s.read(SECTION, 32)), 'floor', cstr(s.read(FLOOR, 32)), flush=True)
        s.save_state(os.path.abspath(a.outstate)); print('state', a.outstate, 'shot', a.out + '/final.png')
    finally:
        s.close()


if __name__ == '__main__':
    main()
