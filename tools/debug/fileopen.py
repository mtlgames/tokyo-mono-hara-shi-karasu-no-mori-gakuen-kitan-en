"""Log every file the game opens (sceIoOpen / sceIoOpenAsync import stubs): frame, path, caller.

    python -X utf8 tools/debug/fileopen.py ISO --out DIR --state S [--mash 3000:circle,up] [--max 200]

Stubs found from the IoFileMgrForUser import table in work/exe/main_ram.bin (NIDs 0x109F50BC, 0x89AA9906).
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg, warp

STUBS = {0x08AA7FB0: 'open', 0x08AA7F90: 'open_async'}


def cstr(s, addr):
    b = s.read(addr, 128)
    return b.split(b'\0')[0].decode('cp932', 'replace')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('--out', required=True); ap.add_argument('--state', help='omit for a cold boot (stubs hit once the module is loaded)')
    ap.add_argument('--mash', default='3000:-'); ap.add_argument('--max', type=int, default=200)
    a = ap.parse_args()
    s = pspdbg.Session(a.iso, a.out, a.state)
    try:
        for b in STUBS: s.bp(b)
        n = [0]

        def hit(s, r):
            if r['pc'] not in STUBS: return print(f'f{s.frame():06d} other break pc={r["pc"]:08x}', flush=True)
            n[0] += 1
            if n[0] > a.max:
                for b in STUBS: s.bp_clear(b)
                return
            print(f'f{s.frame():06d} {STUBS[r["pc"]]:10s} {cstr(s, r["a0"])}  ra={r["ra"]:08x}', flush=True)
        s.play(warp.mash_steps(a.mash), hit)
    finally:
        s.close()


if __name__ == '__main__':
    main()
