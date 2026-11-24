"""Print GPRs and FPU registers at code breakpoints (first N hits) from a savestate.

    python -X utf8 tools/debug/fpregs.py ISO STATE ADDR [ADDR..] [--frames 60] [--max 6] [--fpr f20,f23,f25]
"""
import argparse, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg
from bpstr import cstr


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('state'); ap.add_argument('addrs', nargs='+')
    ap.add_argument('--frames', type=int, default=60); ap.add_argument('--max', type=int, default=6)
    ap.add_argument('--fpr', default='f12,f13,f20,f23,f25,f28,f29'); ap.add_argument('--out', default='work/qa/fpregs')
    a = ap.parse_args()
    s = pspdbg.Session(a.iso, a.out, a.state)
    want = a.fpr.split(',')
    try:
        bps = [int(x, 16) for x in a.addrs]
        for b in bps: s.bp(b)
        n = 0
        while n < a.max:
            r = s.run_until_bp(a.frames)
            if not r: break
            n += 1
            cats = s.ws.call('cpu.getAllRegs')['categories']
            fpu = next(c for c in cats if c['name'] == 'FPU')
            fv = {k: struct.unpack('<f', struct.pack('<I', v))[0] for k, v in zip(fpu['registerNames'], fpu['uintValues'])}
            print(f"f{s.frame():06d} pc={r['pc']:08x} ra={r['ra']:08x} a0={r['a0']:08x} a1={r['a1']:08x} a2={r['a2']:08x} s1={r['s1']:08x} " + ' '.join(f'{k}={fv[k]:.2f}' for k in want) + f" {cstr(s, r['a1'], 60)!r}", flush=True)
    finally:
        s.close()


if __name__ == '__main__':
    main()
