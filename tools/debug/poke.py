"""Write floats / words into RAM at a savestate, run a few frames, shoot: quick layout experiments.

    python -X utf8 tools/debug/poke.py ISO STATE OUT ADDR=VAL [ADDR=VAL..] [--frames 4]

VAL with a dot is a float (368.0), else a hex word (0x3f800000). OUT/final.png is the shot.
"""
import argparse, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('state'); ap.add_argument('out'); ap.add_argument('sets', nargs='*')
    ap.add_argument('--frames', type=int, default=4)
    a = ap.parse_args()
    s = pspdbg.Session(a.iso, a.out, a.state)
    try:
        for kv in a.sets:
            k, v = kv.split('=')
            s.write(int(k, 16), struct.pack('<f', float(v)) if '.' in v else int(v, 16).to_bytes(4, 'little'))
        s.play([(a.frames, set())])
        s.shot('final.png')
    finally:
        s.close()


if __name__ == '__main__':
    main()
