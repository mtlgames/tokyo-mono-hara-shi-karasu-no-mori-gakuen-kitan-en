"""Save editor: read and edit the game's save (plain DATA.BIN), make saves from scenes, load them in the emulator.

    python -X utf8 tools/debug/save.py show SAVE                       # SAVE = save folder, its parent, or DATA.BIN
    python -X utf8 tools/debug/save.py edit SAVE OUTDIR money=99999 chapter=3 ...
    python -X utf8 tools/debug/save.py make ISO NAME --from SCENE      # save from a field scene -> work/saves/NAME
    python -X utf8 tools/debug/save.py load ISO SAVE [--name N]        # title -> Continue -> slot 1; shot + state

Saves are written unencrypted (tools/debug/noenc.ini, passed by pspdbg.Session), and only an unencrypted save can be
edited: make one with `make`. DATA.BIN is the game-state block the game copies to RAM as is (no checksum; header u32
size 0x25510 at 0), so a field offset here is also the offset from the game-state pointer *(0x09256ED8) in RAM
(warp.py `set=`). Fields: docs/re/debug.md "Saves". The folder must be named DIRNAME inside the memstick.
"""
import argparse, os, shutil, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DIRNAME = 'ULJM05638_KARASUNOMORI_0000'
STATE_PTR = 0x09256ED8
SIZE = 0x25510
# name: (offset, struct format, note)
FIELDS = {
    'size':    (0x0000, '<I', 'header: data size, must stay 0x25510'),
    'money':   (0x0BD4, '<I', 'yen (verified: shows in the menu)'),
    'chapter': (0x3060, '<h', 'story chapter, 0 = prologue (verified: picks MSnn_xx at the end of free movement)'),
    'name_given': (0x0442, '8s', 'SJIS, 千馗'),
    'name_family': (0x0462, '8s', 'SJIS, 七代'),
    'dun_area':  (0x6878, '<i', 'dungeon area = dungeonareainfo.bin row (0 tutorial, 1 bg01_00 秋・第一階層; verified)'),
}
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LOAD_ROUTE = ('300 -;6 circle;200 -;6 circle;200 -;6 circle;600 -;6 start;300 -;6 down;30 -;6 down;60 -;'
              '6 circle;120 -;6 circle;120 -;6 circle;120 -;6 left;60 -;6 circle;600 -')
SAVE_ROUTE = ('6 start;90 -;6 up;40 -;6 circle;150 -;'              # field -> menu -> セーブ・ロード
              '30 -;6 circle;60 -;6 circle;60 -;6 circle;60 -;6 left;30 -;6 circle;300 -;6 circle;120 -;6 circle;120 -')


def data_path(save):
    for p in (save, os.path.join(save, 'DATA.BIN'), os.path.join(save, DIRNAME, 'DATA.BIN')):
        if os.path.isfile(p): return p
    sys.exit(f'no DATA.BIN in {save}')


def parse_value(name, v):
    fmt = FIELDS[name][1]
    return v.encode('cp932').ljust(struct.calcsize(fmt), b'\0') if fmt.endswith('s') else int(v, 0)


def get(b, name):
    off, fmt, _ = FIELDS[name]
    v = struct.unpack_from(fmt, b, off)[0]
    return v.rstrip(b'\0').decode('cp932', 'replace') if isinstance(v, bytes) else v


def put(b, name, value):
    off, fmt, _ = FIELDS[name]
    struct.pack_into(fmt, b, off, value)


def check(b):
    if get(b, 'size') != SIZE: sys.exit('not a plain save (encrypted, or another game): header size wrong')


def show(save):
    b = open(data_path(save), 'rb').read(); check(b)
    for k, (off, fmt, note) in FIELDS.items(): print(f'{k:12s} @{off:05x} = {get(b, k)!r:14}  {note}')


def edit(save, out, assigns):
    src = os.path.dirname(data_path(save)); dst = os.path.join(out, DIRNAME)
    if os.path.abspath(src) != os.path.abspath(dst):
        shutil.rmtree(dst, ignore_errors=True); shutil.copytree(src, dst)
    p = os.path.join(dst, 'DATA.BIN'); b = bytearray(open(p, 'rb').read()); check(b)
    for a in assigns:
        k, _, v = a.partition('=')
        if k not in FIELDS: sys.exit(f'unknown field {k}; known: {" ".join(FIELDS)}')
        put(b, k, parse_value(k, v))
    open(p, 'wb').write(b)
    print('wrote', dst)


def poke_state(s, assigns):
    """warp.py set=: write fields into the live game state (same offsets as DATA.BIN)."""
    base = s.u32(STATE_PTR)
    for a in assigns:
        k, _, v = a.partition('=')
        off, fmt, _ = FIELDS[k]; val = parse_value(k, v)
        s.write(base + off, struct.pack(fmt, val))


def make(iso, name, scene):
    import pspdbg, warp
    from pspdbg import psp
    if not os.path.exists(warp.state_path(scene)):
        warp.run_scene(iso, scene, warp.load_scenes()[scene], os.path.join(ROOT, 'work', 'qa', 'warp', scene))
    out = os.path.join(ROOT, 'work', 'qa', 'save_make', name)
    shutil.rmtree(out, ignore_errors=True)
    s = pspdbg.Session(iso, out, warp.state_path(scene))
    try:
        s.route(psp.parse_route(SAVE_ROUTE)); s.shot('final.png')
    finally:
        s.close()
    src = os.path.join(out, 'memstick', 'PSP', 'SAVEDATA', DIRNAME)
    if not os.path.isdir(src): sys.exit(f'no save written (see {out}/final.png)')
    dst = os.path.join(ROOT, 'work', 'saves', name)
    edit(src, dst, [])
    show(dst)


def load(iso, save, name):
    import pspdbg, warp
    from pspdbg import psp
    folder = os.path.dirname(data_path(save))
    out = os.path.join(ROOT, 'work', 'qa', 'save_load', name)
    shutil.rmtree(out, ignore_errors=True)
    s = pspdbg.Session(iso, out, sav=folder)
    if os.path.basename(folder) != DIRNAME: sys.exit(f'save folder must be named {DIRNAME}')
    try:
        s.route(psp.parse_route(LOAD_ROUTE))
        blank = psp.blank(s.shot('final.png'))
        s.save_state(warp.state_path(name))
    finally:
        s.close()
    print(f'{name}: shot {out}/final.png state {warp.state_path(name)}')
    return 3 if blank else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('show'); p.add_argument('save')
    p = sub.add_parser('edit'); p.add_argument('save'); p.add_argument('out'); p.add_argument('assign', nargs='+')
    p = sub.add_parser('make'); p.add_argument('iso'); p.add_argument('name'); p.add_argument('--from', dest='scene', default='field_ch01')
    p = sub.add_parser('load'); p.add_argument('iso'); p.add_argument('save'); p.add_argument('--name')
    a = ap.parse_args()
    if a.cmd == 'show': show(a.save)
    elif a.cmd == 'edit': edit(a.save, a.out, a.assign)
    elif a.cmd == 'make': make(a.iso, a.name, a.scene)
    else: sys.exit(load(a.iso, a.save, a.name or 'load_' + os.path.basename(os.path.normpath(a.save))))


if __name__ == '__main__':
    main()
