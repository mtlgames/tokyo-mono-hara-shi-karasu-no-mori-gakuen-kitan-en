"""Log every .PWX script the game loads (breakpoint on the loader's sprintf), with the caller and frame.

    python -X utf8 tools/debug/trace_pw.py ISO --out DIR [--route R] [--state S] [--frames N] [--mash circle]

Loader: 0x089F22E4(a0, type, chapter, sub); type indexes the prefix table at 0x08ADC490 (MS FD FN ID IN DG KWLNSCR
FS QS QUEST). The breakpoints sit at 0x089F2448 / 0x089F24F0 (state 0, before the path is built).
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg
from pspdbg import psp

PREFIX = ['MS', 'FD', 'FN', 'ID', 'IN', 'DG', 'KWLNSCR', 'FS', 'QS', 'QUEST']
BPS = (0x089F2448, 0x089F24F0)


def log_load(s, r):
    t = r['a1']
    name = (PREFIX[t] if t < len(PREFIX) else str(t)) + ('' if t in (6, 9) else f'{r["s3"]:02d}_{r["s4"]:02d}')
    print(f'f{s.frame():06d} load {name} caller={s.u32(r["sp"] + 0x28):08x}', flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('--out', required=True)
    ap.add_argument('--route'); ap.add_argument('--state'); ap.add_argument('--frames', type=int, default=3000)
    ap.add_argument('--mash', help='buttons pressed 6 of every 30 frames after the route, cycled (circle,right)')
    ap.add_argument('--shot-every', type=int, default=0)
    ap.add_argument('--state-out')
    a = ap.parse_args()
    s = pspdbg.Session(a.iso, a.out, a.state)
    try:
        for b in BPS: s.bp(b)
        steps = psp.parse_route(open(a.route).read()) if a.route else []
        f = s.play(steps, log_load)
        tail, mash = [], a.mash.split(',') if a.mash else []
        for i in range(0, a.frames, 30):   # cycle the mash list, one press per 30 frames
            key = mash[(i // 30) % len(mash)] if mash else None
            tail += [(6, set(key.split('+')) if key else set()), (24, set())]
        for i, st in enumerate(tail):
            f = s.play([st], log_load, f)
            if a.shot_every and i % 2 and (f // a.shot_every) != ((f - 30) // a.shot_every): s.shot(f'f{f:06d}.png')
        s.shot('final.png')
        if a.state_out: s.save_state(a.state_out)
    finally:
        s.close()


if __name__ == '__main__':
    main()
