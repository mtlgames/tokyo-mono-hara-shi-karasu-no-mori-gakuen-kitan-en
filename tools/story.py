"""Story-pass chapter files (docs/story-reviewer-brief.md) from script/pw, in story order (batches.docs order).

    python -X utf8 tools/story.py [--size 90000]   work/qa/story/chapters/chNN_K.txt, one per <= size chars of a chapter

Then: qa_gate.py init work/qa/story/manifest.tsv work/qa/story/chapters --glob "*.txt". Regenerate after every script
edit; a changed file loses its verdict. Old files are removed first, so a re-run never leaves a stale part.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batches  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "work/qa/story/chapters"


def flat(s):
    return (s or "").replace("\n", " / ")


def main(argv):
    size = int(argv[argv.index("--size") + 1]) if "--size" in argv else 90000
    speakers = {s["id"]: s.get("en") or s["jp"] for s in
                json.loads((ROOT / "script/speakers.json").read_text(encoding="utf-8"))}
    chapters = {}  # "NN" -> [block per script file]
    for path, _, entries in batches.docs():
        if path.parent.parent.name != "pw":
            continue
        lines = [f">> {e['id']} | {speakers.get(e.get('speaker'), e.get('speaker', ''))} | {flat(e['jp'])}\n"
                 f"{flat(e.get('en'))}\n" for e in entries if batches.is_text(e)]
        if lines:
            chapters.setdefault(path.stem[2:4], []).append(f"## {path.stem}\n" + "".join(lines))
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.txt"):
        old.unlink()
    n = 0
    for ch, blocks in chapters.items():
        parts, cur = [], ""
        for b in blocks:
            if cur and len(cur) + len(b) > size:
                parts.append(cur)
                cur = ""
            cur += b
        parts.append(cur)
        for k, text in enumerate(parts):
            (OUT / f"ch{ch}_{k + 1}.txt").write_text(f"# Chapter {int(ch)}, part {k + 1}/{len(parts)}\n" + text,
                                                     encoding="utf-8", newline="\n")
            n += 1
    print(f"{n} files in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
