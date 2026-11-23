"""Find a class's RTTI typeinfo, vtable and the code that stores the vtable (constructors) in the RAM-dumped EBOOT.

    python -X utf8 tools/debug/rtti.py [--bin work/exe/main_ram.bin] CLBadendTask CLContinueTask ...

GCC RTTI: the name string ("12CLBadendTask"), a typeinfo {vptr, &name[, &base]}, a vtable {0, &typeinfo, methods...}.
Constructors load the vtable address with lui/addiu (or lui/ori) and store it to the object; this lists those sites.
"""
import argparse, os, re, struct

BASE = 0x08804000
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def words(b):
    return struct.unpack(f'<{len(b) // 4}I', b[:len(b) // 4 * 4])


def lui_pairs(w, target):
    """Code sites building TARGET with lui hi + addiu/ori lo (same register, within 8 instructions)."""
    hi, lo = (target + 0x8000) >> 16, target & 0xffff
    out = []
    for i, x in enumerate(w):
        if x >> 26 == 0x0f and x & 0xffff in (hi, target >> 16):
            rt = (x >> 16) & 31
            for j in range(i + 1, min(i + 9, len(w))):
                y = w[j]; op = y >> 26
                if (y >> 21) & 31 == rt and y & 0xffff == lo and (op == 0x09 and x & 0xffff == hi or op == 0x0d and x & 0xffff == target >> 16):
                    out.append(BASE + 4 * i); break
    return out


def find(b, w, name):
    m = re.search(rb'\d+' + name.encode() + rb'\x00', b)
    if not m: return print(f'{name}: no name string')
    s = BASE + m.start()
    for ti in [BASE + 4 * i - 4 for i, x in enumerate(w) if x == s]:
        vts = [BASE + 4 * i - 4 for i, x in enumerate(w) if x == ti and w[i - 1] == 0]
        print(f'{name}: name {s:08x} typeinfo {ti:08x} vtable+8 {" ".join(f"{v + 8:08x}" for v in vts)}')
        for v in vts:
            print(f'  vtable {v + 8:08x} built at {" ".join(f"{a:08x}" for a in lui_pairs(w, v + 8))}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--bin', default=os.path.join(ROOT, 'work', 'exe', 'main_ram.bin'))
    ap.add_argument('names', nargs='+')
    a = ap.parse_args()
    b = open(a.bin, 'rb').read(); w = words(b)
    for n in a.names: find(b, w, n)


if __name__ == '__main__':
    main()
