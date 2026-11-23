"""Warp to a scene from a cold boot (PPSSPP has no Lua: this drives PPSSPPHeadless over its debugger WebSocket).

    python -X utf8 tools/debug/warp.py ISO SCENE [--out DIR] [--shot-every N] [--frames N]
    python -X utf8 tools/debug/warp.py ISO --all        # regenerate every state in work/states/
    python -X utf8 tools/debug/warp.py ISO --list

SCENE is a name from tools/debug/scenes.txt, or a script id like MS03_00 / FD01_20 / QUEST. Every run ends with
OUT/final.png (default OUT work/qa/warp/SCENE) and work/states/SCENE.ppst. A scene spec is
`script=ID` (cold boot + warp) or `from=SCENE` (start from that scene's state, made first if missing), then
`set=chapter=1,money=5000` (game-state fields, save.py FIELDS), `task=ID` (SetNextTask), then
`mash=FRAMES:k1,k2` (one press per 30 frames, cycled; `-` = no press) and `route=` (route-str, rest of the line).
How: boot -> New Game (tools/routes/boot.txt). When the ADV task starts its first script (MS00_00), a breakpoint at
0x089EB4D8 rewrites the task's params (+4 chapter, +6 sub, +8 type) to the target script, so it runs from block 0
as if the story had called it (chapter cards and opening movies are commands inside MSxx_00). Notes: docs/re/debug.md.
"""
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg, save, trace_pw
from pspdbg import psp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PREFIX = ['MS', 'FD', 'FN', 'ID', 'IN', 'DG', 'KWLNSCR', 'FS', 'QS', 'QUEST']
ADV_LOAD = 0x089EB4D8      # ADV task, state "load script": s1 = params
NEXT_TASK, TASK_SWITCH = 0x08ADD370, 0x09247119   # task ids: docs/re/debug.md "Tasks"


def load_scenes():
    out = {}
    for line in open(os.path.join(HERE, 'scenes.txt'), encoding='utf-8'):
        line = line.split('#')[0].strip()
        if line:
            name, spec = line.split(None, 1); out[name] = spec.strip()
    return out


def parse_script(sid):
    """'MS03_00' -> (type, chapter, sub); 'QUEST' -> (9, 0, 0)."""
    m = re.fullmatch(r'([A-Z]+)(?:(\d\d)_(\d\d))?', sid.upper())
    if not m or m.group(1) not in PREFIX: raise SystemExit(f'bad script id {sid}')
    return PREFIX.index(m.group(1)), int(m.group(2) or 0), int(m.group(3) or 0)


class Warp:
    def __init__(self, script):
        self.target = parse_script(script); self.done = False

    def on_bp(self, s, r):
        if r['pc'] != ADV_LOAD or self.done: return
        t, ch, sub = self.target
        p = r['s1']
        s.write(p + 4, ch.to_bytes(2, 'little') + sub.to_bytes(2, 'little') + bytes([t]))
        self.done = True
        print(f'f{s.frame():06d} warp: ADV params at {p:08x} -> {PREFIX[t]}{ch:02d}_{sub:02d}', flush=True)


def parse_spec(spec):
    """'script=MS01_00 mash=900:circle,right route=60 -;6 start' -> dict; route= takes the rest of the line."""
    out = {}
    if ' route=' in ' ' + spec:
        spec, out['route'] = (' ' + spec).split(' route=', 1)
    for tok in spec.split():
        k, _, v = tok.partition('=')
        out[k] = v if v else k
    return out


def state_path(name): return os.path.join(ROOT, 'work', 'states', f'{name}.ppst')


def mash_steps(spec):
    """'900:circle,right' -> one press (6 frames) per 30 frames for 900 frames, cycling the keys."""
    n, _, keys = spec.partition(':'); keys = keys.split(',')
    steps = []
    for i in range(int(n) // 30):
        k = keys[i % len(keys)]
        steps += [(6, set() if k == '-' else set(k.split('+'))), (24, set())]
    return steps


def run_scene(iso, name, spec, out, shot_every=0, frames=0):
    """Reach scene NAME (spec from scenes.txt, or a bare script id), shoot it, save work/states/NAME.ppst."""
    if re.fullmatch(r'[A-Z]+(\d\d_\d\d)?', spec): spec = f'script={spec} mash=900:circle'
    sp = parse_spec(spec)
    if 'from' in sp and not os.path.exists(state_path(sp['from'])):
        scenes = load_scenes(); run_scene(iso, sp['from'], scenes[sp['from']], out + '_' + sp['from'])
    s = pspdbg.Session(iso, out, state_path(sp['from']) if 'from' in sp else None)
    code = 0
    try:
        f = 0
        if 'script' in sp:
            w = Warp(sp['script']); s.bp(ADV_LOAD)
            f = s.play(psp.parse_route(open(os.path.join(ROOT, 'tools', 'routes', 'boot.txt')).read()), w.on_bp)
            while not w.done and f < 6000:     # New Game is chosen inside the boot route; wait for the ADV task
                f = s.play([(30, set())], w.on_bp, f)
            if not w.done: print('warp never fired'); code = 3
            s.bp_clear(ADV_LOAD)
        if 'set' in sp:                   # game-state fields, as in save.py: set=chapter=1,money=5000
            s.run_to(f + 1); save.poke_state(s, sp['set'].split(','))
            print(f'f{s.frame():06d} set {sp["set"]}', flush=True)
        if 'task' in sp:                  # SetNextTask(id) (0x08A38294): next id + switch flag
            s.run_to(f + 2); s.w32(NEXT_TASK, int(sp['task'])); s.write(TASK_SWITCH, b'\1')
            print(f'f{s.frame():06d} next task -> {sp["task"]}', flush=True)
        for b in trace_pw.BPS: s.bp(b)    # log the scripts the game loads from here on
        steps = (mash_steps(sp['mash']) if 'mash' in sp else []) + psp.parse_route(sp.get('route', ''))
        if frames: steps.append((frames, set()))
        for st in steps:
            f = s.play([st], trace_pw.log_load, f)
            if shot_every and f % shot_every < st[0]: s.shot(f'f{f:06d}.png')
        if psp.blank(s.shot('final.png')): print('final frame is blank'); code = 3
        s.save_state(state_path(name))
        print(f'{name}: f{f} state {state_path(name)} shot {out}/final.png exit {code}', flush=True)
    finally:
        s.close()
    return code


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('scene', nargs='?')
    ap.add_argument('--out', help='default work/qa/warp/<scene>'); ap.add_argument('--list', action='store_true')
    ap.add_argument('--all', action='store_true', help='regenerate every scene state in scenes.txt order')
    ap.add_argument('--frames', type=int, default=0, help='extra idle frames at the end')
    ap.add_argument('--shot-every', type=int, default=0)
    a = ap.parse_args()
    scenes = load_scenes()
    if a.list:
        for k, v in scenes.items(): print(k, v)
        return
    names = list(scenes) if a.all else [a.scene]
    bad = [n for n in names
           if run_scene(a.iso, n, scenes.get(n, n), a.out or os.path.join(ROOT, 'work', 'qa', 'warp', n),
                        a.shot_every, a.frames)]
    if bad: print('FAILED:', ' '.join(bad))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
