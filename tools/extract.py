"""extract.py: dump every Japanese string from the ORIGINAL game to script/*.json (format: docs/re/text.md §Repo text).

    python -X utf8 tools/extract.py            # write missing files only
    python -X utf8 tools/extract.py --force    # regenerate jp/context fields, keeping en/notes/status by id;
                                               # prints ids whose jp changed (re-check their translations)

script/pw/<dir>/<stem>.json  story/event script spans (pwx.py), then the scene's choice menus (ksf.py)
script/tables/<stem>.json    CSVB table strings (tables.py)
script/eboot.json            EBOOT strings (eboot_text.py; needs work/exe/NPJH50215_EBOOT.BIN)
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import eboot_text  # noqa: E402
import ksf  # noqa: E402
import pwx  # noqa: E402
import tables  # noqa: E402
from source import members  # noqa: E402

SCRIPT = ROOT / "script"
KEEP = ("en", "notes", "status")  # translator-owned fields, never overwritten
TABLE_DIRS = ("app_init.pak/table/", "table/", "dungeon/")


def stem(path):
    return path.rsplit("/", 1)[-1].rsplit(".", 1)[0]


def extracted():
    """{repo json path (relative to script/): [entry]} from the original ISO and EBOOT."""
    out = {}
    for path, d in members("pw/"):  # each .ksf follows its .pwx in archive order
        key = f"pw/{path.split('/')[1]}/{stem(path)}.json"
        if path.endswith(".pwx"):
            out[key] = pwx.entries(d, stem(path)) + out.get(key, [])
        elif path.endswith(".ksf"):
            out.setdefault(key, []).extend(ksf.entries(d, stem(path)))
    count = {}
    for key, entries in list(out.items()):
        for x in entries:
            if "speaker" in x:
                count[x["speaker"]] = count.get(x["speaker"], 0) + 1
    # speaker names are translated once here; the build writes 【en】 wherever 【jp】 was
    out["speakers.json"] = [{"id": s, "jp": s, "lines": n} for s, n in sorted(count.items(), key=lambda kv: -kv[1])]
    for path, d in members(*TABLE_DIRS):
        if d[:4] == b"CSVB":
            e = tables.entries(d, stem(path))
            if e:
                key = f"tables/{stem(path)}.json"
                assert key not in out, f"two text tables named {key}"
                out[key] = e
    if eboot_text.ELF.exists():
        out["eboot.json"] = [{k: x[k] for k in ("id", "jp", "slot", "refs", "enc")}
                             for x in eboot_text.strings(eboot_text.ELF.read_bytes())]
    return out


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def merge(new, old):
    """New entries with the translator-owned fields of old entries (by id); returns (entries, changed ids)."""
    by = {x["id"]: x for x in old}
    changed = []
    for x in new:
        o = by.get(x["id"])
        if o and o.get("jp") != x["jp"] and o.get("en"):
            changed.append(x["id"])
        for k in KEEP:
            x[k] = o.get(k, "") if o else ""
            if k != "en" and not x[k]:
                del x[k]
    return new, changed


def write(path, entries):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if not eboot_text.ELF.exists():
        print(f"warning: {eboot_text.ELF} missing, eboot.json skipped (docs/re/pak.md: how to dump it)")
    n = files = 0
    for rel, entries in extracted().items():
        p = SCRIPT / rel
        if p.exists() and not a.force:
            continue
        entries, changed = merge(entries, load(p) if p.exists() else [])
        for i in changed:
            print("jp changed, re-check:", i)
        write(p, entries)
        files += 1
        n += len(entries)
    print(f"wrote {files} files, {n} entries")


if __name__ == "__main__":
    main()
