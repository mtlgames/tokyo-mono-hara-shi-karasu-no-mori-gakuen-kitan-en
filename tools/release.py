"""release.py: the release gate and package. Stops at the first failing step.

    python -X utf8 tools/release.py [--version 1.0] [--force] [--steps build,check,...]

Steps: build (build.py, default English mode) -> check (tools/check.py) -> smoke (emu.py) -> jp (jp_left.py on the
EBOOT and every text-bearing CROW.PAK member, vs the original; docs/jp_known.tsv lists Japanese kept on purpose) ->
gate (qa_gate.py check on every work/qa/**/manifest.tsv: visual tour and story pass) -> cover (tools/cover.py report)
-> polish (no unticked docs/polish.md line) -> readme (no template placeholder in README.md or the zip README) ->
debug (the ISO is this run's default build: no --marker/--qa/startroom edits; the debug tools are emulator-side
breakpoints, nothing of them is in the ISO) -> patch (xdelta3 -B) -> verify (re-apply to the original, compare) ->
zip (release/vX.Y/: patch + README.txt, ZIP_STORED). --steps runs only the named steps (iterating on one gate).
Refuses to overwrite release/vX.Y without --force. The playable image stays in build/karasu_en.iso.
"""
import argparse
import contextlib
import hashlib
import io
import re
import subprocess
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
from skill import SCRIPTS  # noqa: E402

SCRIPTS = Path(SCRIPTS)  # skill.py gives a str

PY = [sys.executable, "-X", "utf8"]
ISO = ROOT / "build" / "karasu_en.iso"
NAME = "Tokyo_Mono_Hara_Shi_Karasu_no_Mori_EN"
TEXT_EXT = {"pwx", "ksf", "bin", "ini", "g2d", "lay", "ipk", ""}  # media (gim z3n znt at3 g3a pbd bpc phd) is QA'd by eye
KNOWN = ROOT / "docs" / "jp_known.tsv"
PLACEHOLDER = re.compile(r"<(?:Game title|platform|publisher|year|repo|file|size|sha1|game|ext)>|<[A-Z][a-z]+ / ")
STEPS = "build check smoke jp gate cover polish readme debug patch verify zip".split()


def run(cmd):
    print("$", " ".join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), cwd=ROOT).returncode


def hashes(path):
    s, m, c = hashlib.sha1(), hashlib.md5(), 0
    with open(path, "rb") as f:
        while b := f.read(1 << 24):
            s.update(b), m.update(b)
            c = zlib.crc32(b, c)
    return f"{c:08X}", m.hexdigest(), s.hexdigest()


def text_members(iso):
    from source import members
    for path, data in members("", iso=iso):
        leaf = path.rsplit("/", 1)[-1]
        if (leaf.rsplit(".", 1)[-1].lower() if "." in leaf else "") in TEXT_EXT:
            yield path, data


def known():
    """{path: [offset | * | row:col]}; a path may be a glob (dungeon/*.ini)."""
    import fnmatch
    rows = [line.split("\t")[:2] for line in KNOWN.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")] if KNOWN.exists() else []

    class Keep(dict):
        def get(self, path, default=()):
            return [off for pat, off in rows if fnmatch.fnmatchcase(path, pat)] or default

        def __contains__(self, path):
            return bool(self.get(path))
    return Keep()


def eboot_short(elf):
    """jp_left needs 4+ chars, so 1-char strings (春, 壇, pn君, %s型) slipped through: report every NUL-started string
    in the string pool that still holds kana/kanji within 0x48 bytes of an extracted entry (inside a text table;
    farther out, data words decode as stray kanji).
    shortcut: the window caught 20 of the 24 found by hand (4 nickname slots sat farther out; 0x80 already flags a
    data word as 護), upgrade to a pointer/reloc-reach test if a short string slips again."""
    import bisect, json
    import eboot_text
    ids = sorted(int(e["id"].split(":")[1], 16) for e in json.loads((ROOT / "script" / "eboot.json").read_text("utf-8")))
    jp, out, known_ids = re.compile("[぀-ヿ㐀-鿿]"), [], set(ids)
    for m in re.finditer(rb"(?<=\x00)[^\x00]+", elf[eboot_text.POOL:0x2F0000]):
        o = eboot_text.POOL + m.start()
        try:
            s = m.group().decode("cp932")
        except UnicodeDecodeError:
            continue
        i = bisect.bisect(ids, o)
        if o in known_ids:  # extracted: script/ tracks it (untranslated ones are the kana keyboard, name codes)
            continue
        if jp.search(s) and min(abs(o - ids[j]) for j in (i - 1, i) if 0 <= j < len(ids)) <= 0x48:
            out.append(f"{o:#x}: {s}")
    return out


def step_jp(state):
    """jp_left --sjis --orig per file: Japanese runs whose bytes the build left unchanged."""
    sys.path.insert(0, str(SCRIPTS))
    import build
    import eboot
    import iso9660
    import jp_left
    with open(ISO, "rb") as f:
        lba, size = next((lba, ln) for p, lba, ln, _ in iso9660.listing(f) if p == build.EBOOT)
        f.seek(lba * 2048)
        if f.read(4) != b"~PSP":
            print(f"{build.EBOOT} in {ISO} is not a signed ~PSP EBOOT")
            return 1
    pairs = [("EBOOT.BIN", ISO.with_suffix(".elf").read_bytes(), eboot.ELF.read_bytes())]
    orig = dict(text_members(None))
    pairs += [(p, d, orig.get(p)) for p, d in text_members(ISO)]
    import csvb
    keep, report, hits = known(), [], 0
    with tempfile.TemporaryDirectory() as tmp:
        b, o, k = Path(tmp, "b"), Path(tmp, "o"), Path(tmp, "k")
        for path, data, before in pairs:
            if "*" in keep.get(path, ()):
                continue
            if data[:4] == b"CSVB":
                # English is appended and repointed, the old Japanese stays unreferenced: check what pointers reach
                bad = [f"row {r} col {c:#x}: {s.decode('cp932', 'replace')}" for r, c, _, s in csvb.strings(data)
                       if jp_left.scan(s, jp_left.sjis_char, 0, len(s), 2) and f"{r}:{c:#x}" not in keep.get(path, ())]
                if bad:
                    hits += 1
                    report.append(f"## {path}\n" + "\n".join(bad) + "\n")
                continue
            b.write_bytes(data)
            args = [str(b), "--sjis"]
            if before is not None:
                o.write_bytes(before)
                args += ["--orig", str(o)]
            if path in keep:
                k.write_text("\n".join(keep.get(path)) + "\n", encoding="utf-8")
                args += ["--known", str(k)]
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                try:
                    code = jp_left.main(args)
                except SystemExit as e:
                    code = e.code
            if code:
                hits += 1
                report.append(f"## {path}\n{out.getvalue()}")
    short = eboot_short(pairs[0][1])
    if short:
        hits += 1
        report.append("## EBOOT.BIN short strings (1-3 chars, inside an extracted table)\n" + "\n".join(short) + "\n")
    rep = ROOT / "work" / "release" / "jp_left.txt"
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text("".join(report), encoding="utf-8")
    print(f"jp_left: {len(pairs)} files scanned, {hits} with unlisted Japanese (report {rep})")
    return 1 if hits else 0


def step_gate(state):
    manifests = sorted((ROOT / "work" / "qa").rglob("manifest.tsv"))
    if not any("story" in m.parts for m in manifests):
        print("no story-pass manifest (work/qa/story/manifest.tsv)")
        return 1
    return max(run(PY + [SCRIPTS / "qa_gate.py", "check", m, m.parent / "verdicts"]) for m in manifests)


def zip_readme(state):
    t = (ROOT / "docs" / "release-readme.txt").read_text(encoding="utf-8")
    return t.replace("{version}", state["version"]).replace("{patch}", state["patch"].name) \
        .replace("{crc32}", state["built"][0]).replace("{sha1}", state["built"][2])


def step_readme(state):
    bad = [f"README.md: {m.group()}" for m in PLACEHOLDER.finditer((ROOT / "README.md").read_text(encoding="utf-8"))]
    t = (ROOT / "docs" / "release-readme.txt").read_text(encoding="utf-8")
    bad += [f"release-readme.txt: {m.group()}" for m in PLACEHOLDER.finditer(t)]
    base = hashes(ROOT / __import__("build").ISO)
    state["base"] = base
    for where, text in (("README.md", (ROOT / "README.md").read_text(encoding="utf-8")), ("release-readme.txt", t)):
        bad += [f"{where}: base hash {h} missing" for h in base if h.lower() not in text.lower()]
    print("\n".join(bad) or "readme: no placeholders, base hashes present")
    return 1 if bad else 0


def step_debug(state):
    if "built_sha1" not in state:
        print("debug: run with the build step, so the ISO is known to be this run's default build")
        return 1
    ok = hashes(ISO)[2] == state["built_sha1"]
    print("debug: ISO is this run's default build" if ok else "debug: ISO changed after the build step")
    return 0 if ok else 1


def step_patch(state):
    import build
    state["patch"].parent.mkdir(parents=True, exist_ok=True)
    state["patch"].unlink(missing_ok=True)
    return run(["xdelta3", "-e", "-9", "-B", build.ISO.stat().st_size, "-s", build.ISO, ISO, state["patch"]])


def step_verify(state):
    import build
    out = state["patch"].with_suffix(".check.iso")
    code = run(["xdelta3", "-d", "-f", "-B", build.ISO.stat().st_size, "-s", build.ISO, state["patch"], out])
    try:
        if code:
            return code
        got, want = hashes(out), hashes(ISO)
        state["built"] = want
        print(f"verify: re-applied sha1 {got[2]} vs build {want[2]}")
        return 0 if got == want else 1
    finally:
        out.unlink(missing_ok=True)


def step_zip(state):
    state.setdefault("built", hashes(ISO))
    z = state["patch"].with_name(f"{NAME}_v{state['version']}.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_STORED) as f:
        f.write(state["patch"], state["patch"].name)
        f.writestr("README.txt", zip_readme(state))
    print(f"zip: {z} ({z.stat().st_size} bytes)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite an existing release/vX.Y")
    ap.add_argument("--steps", help="comma list from: " + ",".join(STEPS))
    a = ap.parse_args(argv)
    steps = a.steps.split(",") if a.steps else STEPS
    if unknown := set(steps) - set(STEPS):
        sys.exit(f"unknown steps {sorted(unknown)}")
    out_dir = ROOT / "release" / f"v{a.version}"
    if {"patch", "zip"} & set(steps) and out_dir.exists() and not a.force:
        sys.exit(f"{out_dir} exists: pass --force to overwrite version {a.version}")
    state = {"version": a.version, "patch": out_dir / f"{NAME}_v{a.version}.xdelta"}
    actions = {
        "build": lambda s: run(PY + ["build.py"]),
        "check": lambda s: run(PY + ["tools/check.py"]),
        "smoke": lambda s: run(PY + [SCRIPTS / "emu.py", ISO, "--out", "work/qa/smoke", "--route",
                                     "tools/routes/boot.txt", "--smoke"]),
        "jp": step_jp, "gate": step_gate,
        "cover": lambda s: run(PY + ["tools/cover.py", "report"]),
        "polish": lambda s: run(PY + ["tools/polish.py", "count"]),
        "readme": step_readme, "debug": step_debug, "patch": step_patch, "verify": step_verify, "zip": step_zip,
    }
    for name in steps:
        print(f"== {name}", flush=True)
        code = actions[name](state)
        if name == "build" and not code:
            state["built_sha1"] = hashes(ISO)[2]
        if code:
            print(f"release: step {name} failed (exit {code})")
            return 1
    print("release: all steps passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
