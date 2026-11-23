"""PPSSPPHeadless debugger session for this game: boot, run to a frame, read/write RAM, breakpoints.

Library for tools/debug/warp.py and RE probes (PPSSPP has no Lua). Wraps the skill's psp.Run (WebSocket API).

    python -X utf8 tools/debug/pspdbg.py ISO --out DIR [--route R] [--frames N] dump ADDR SIZE FILE
    python -X utf8 tools/debug/pspdbg.py ISO --out DIR modules
"""
import argparse, base64, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from skill import SCRIPTS
sys.path.insert(0, SCRIPTS)
import psp  # noqa: E402

NOENC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'noenc.ini')
MOD_BASE = 0x08804000   # EBOOT load address in PPSSPP (checked with `modules`); RAM = MOD_BASE + ELF vaddr


class Session(psp.Run):
    def __init__(self, iso, out, state=None, memstick=None, sav=None, plain_saves=True):
        ms = os.path.abspath(memstick or os.path.join(out, 'memstick'))
        if sav: psp.seed_saves(ms, sav)
        # plain_saves: the game's saves are written unencrypted (noenc.ini), so save.py can edit them
        extra = [f'--appendconfig={NOENC}'] if plain_saves else []
        super().__init__(psp.find_emu(None), iso, out, state, memstick=ms, extra=extra)

    def read(self, addr, size):
        out = b''
        while size > 0:   # the API caps one read; keep chunks modest
            n = min(size, 0x100000); out += self.ws.mem(addr, n); addr += n; size -= n
        return out

    def u32(self, addr): return int.from_bytes(self.read(addr, 4), 'little')

    def write(self, addr, data):
        self.ws.call('memory.write', address=addr, base64=base64.b64encode(bytes(data)).decode())

    def w32(self, addr, v): self.write(addr, (v & 0xffffffff).to_bytes(4, 'little'))

    def route(self, steps, start=0):
        """Play [(frames, keys)] from frame START; returns the end frame."""
        f = start
        for n, keys in steps:
            self.run_to(f); self.press(keys); f += n
        self.run_to(f); return f

    def bp(self, addr, cond=None):
        p = {'address': addr, 'enabled': True}
        if cond: p['condition'] = cond
        self.ws.call('cpu.breakpoint.add', **p)

    def bp_clear(self, addr): self.ws.call('cpu.breakpoint.remove', address=addr)

    def regs(self):
        r = self.ws.call('cpu.getAllRegs')
        return {n: v for cat in r['categories'] if cat['name'] == 'GPR' for n, v in zip(cat['registerNames'], cat['uintValues'])}

    def run_until_bp(self, max_frames):
        """Resume; return the regs dict if a breakpoint stopped the CPU before MAX_FRAMES more frames, else None."""
        target = self.ws.call('cpu.status')['us'] + round(max_frames * psp.FRAME_US)
        self.ws.call('cpu.runUntilTime', us=target)
        self.ws.wait('cpu.stepping')
        st = self.ws.call('cpu.status')
        return None if st['us'] >= target - 100 else self.regs()

    def play(self, steps, on_bp=None, start=0):
        """Like route(), but breakpoints may fire: each stop calls ON_BP(self, regs) and the run goes on."""
        f = start
        for n, keys in steps + [(0, set())]:
            self.press(keys); end = f + n
            while self.frame() < end:
                r = self.run_until_bp(end - self.frame())
                if r and on_bp: on_bp(self, r)
            f = end
        return f


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('--out', required=True)
    ap.add_argument('--route'); ap.add_argument('--frames', type=int, default=0)
    ap.add_argument('--state')
    ap.add_argument('cmd', choices=['dump', 'modules']); ap.add_argument('args', nargs='*')
    a = ap.parse_args()
    s = Session(a.iso, a.out, a.state)
    try:
        f = s.route(psp.parse_route(open(a.route).read())) if a.route else 0
        s.run_to(max(f, a.frames))
        if a.cmd == 'modules':
            for m in s.ws.call('hle.module.list')['modules']: print(m)
        else:
            addr, size, dest = int(a.args[0], 16), int(a.args[1], 16), a.args[2]
            open(dest, 'wb').write(s.read(addr, size)); print('wrote', dest)
    finally:
        s.close()


if __name__ == '__main__':
    main()
