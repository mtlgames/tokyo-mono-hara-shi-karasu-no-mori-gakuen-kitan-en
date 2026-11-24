"""Visual QA of qa_gate chunks by `codex exec` (Orca runs allow no nested Claude subagents: this is the read-only
reviewer pass the skill wants, one codex session per chunk, per docs/visual-qa-brief.md).

    python -X utf8 tools/vqa_codex.py [CHUNK.txt ..] [--jobs 3]    # default: every work/qa/chunks/*.txt with no verdict file

Each run writes work/qa/verdicts/<chunk>.tsv and leaves its log in work/qa/vqa_logs/<chunk>.log.
"""
import argparse, shutil, subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "work" / "qa"
PROMPT = """You are a read-only visual-QA reviewer. Read docs/visual-qa-brief.md (in parts if long) and follow it.
Chunk file: {chunk}. Verdict file to write (the only file you may create besides scratch zooms in work/qa/vqa_tmp/):
{verdict}. Look at every sheet image listed in the chunk (open the PNG files with your image viewer tool); zoom into
source frames with `python -X utf8 <skill>/scripts/sheet.py` where text is small (<skill> = output of
`python tools/skill.py`). Do not edit anything else, no git. Write one line per id: id<TAB>ok|issue<TAB>note.
Finish with a short summary of the issues."""


def run(chunk):
    chunk = Path(chunk).resolve()
    verdict = QA / "verdicts" / f"{chunk.stem}.tsv"
    log = QA / "vqa_logs" / f"{chunk.stem}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    (QA / "vqa_tmp").mkdir(exist_ok=True)
    prompt = PROMPT.format(chunk=chunk.relative_to(ROOT).as_posix(), verdict=verdict.relative_to(ROOT).as_posix())
    with open(log, "w", encoding="utf-8") as f:  # prompt on stdin ("-"): a multi-line argv breaks through codex.cmd
        code = subprocess.run([shutil.which("codex"), "exec", "--sandbox", "workspace-write", "--skip-git-repo-check",
                               "-C", str(ROOT), "-"], input=prompt.encode("utf-8"), stdout=f,
                              stderr=subprocess.STDOUT).returncode
    return chunk.stem, code, verdict.exists()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chunks", nargs="*")
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    chunks = a.chunks or [c for c in sorted((QA / "chunks").glob("*.txt"))
                          if not (QA / "verdicts" / f"{c.stem}.tsv").exists()]
    print(len(chunks), "chunks", flush=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        for stem, code, ok in ex.map(run, chunks):
            print(stem, "exit", code, "verdict" if ok else "NO VERDICT", flush=True)


if __name__ == "__main__":
    main()
