"""Find which script and block holds a script command, for warp.py `block=` (e.g. a block that only opens a shop).

    python -X utf8 tools/debug/find_cmd.py shop00 trade03 camp
Prints SCRIPT_ID block N, then the block's last 60 bytes as SJIS.
"""
import glob, os, struct, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def blocks(data):
    """Offset table of u16 4-byte units; the first entry is the table size (see docs/re/text.md)."""
    n = struct.unpack_from('<H', data, 0)[0] * 4
    offs = [struct.unpack_from('<H', data, i)[0] * 4 for i in range(0, n, 2)]
    offs = [o for o in offs if o] + [len(data)]
    return [data[a:b] for a, b in zip(offs, offs[1:])]


def main():
    words = [w.encode() for w in sys.argv[1:]]
    for p in sorted(glob.glob(os.path.join(ROOT, 'work', 'unpacked', 'pw', '*', '*.pwx'))):
        for i, blk in enumerate(blocks(open(p, 'rb').read())):
            if any(w in blk for w in words):
                tail = blk.rstrip(b'\0')[-60:].decode('cp932', 'replace')
                print(f'{os.path.basename(p)[:-4].upper()} block {i}: {tail}')


if __name__ == '__main__':
    main()
