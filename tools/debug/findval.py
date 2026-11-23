"""Load a savestate and find a u32 value in RAM (e.g. a class's vtable, to locate its instances), or dump a range.

    python -X utf8 tools/debug/findval.py ISO STATE find 08ac2d20 [08ac2ba8 ...]
    python -X utf8 tools/debug/findval.py ISO STATE dump ADDR SIZE FILE
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg

RAM, RAM_SIZE = 0x08800000, 0x01800000   # PSP user RAM (32 MB model, game uses the first 24 MB)


def main():
    iso, state, cmd, *args = sys.argv[1:]
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'work', 'qa', 'findval')
    s = pspdbg.Session(iso, out, state)
    try:
        s.run_to(1)
        if cmd == 'dump':
            open(args[2], 'wb').write(s.read(int(args[0], 16), int(args[1], 16))); print('wrote', args[2]); return
        ram = s.read(RAM, RAM_SIZE)
        for v in args:
            pat = struct.pack('<I', int(v, 16)); i = ram.find(pat); hits = []
            while i >= 0:
                if i % 4 == 0: hits.append(f'{RAM + i:08x}')
                i = ram.find(pat, i + 1)
            print(v, ' '.join(hits[:40]), f'({len(hits)})')
    finally:
        s.close()


if __name__ == '__main__':
    main()
