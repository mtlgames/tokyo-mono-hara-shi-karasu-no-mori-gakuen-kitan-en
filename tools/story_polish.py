"""Story-pass reports -> docs/polish.md lines (phase 9), and voice-sweep id lists for the fix agents.

    python -X utf8 tools/story_polish.py append      every `- ` item under Important/Minor in work/qa/story/reports/*.md
                                                     becomes `- [ ] chNN_K: item` ([I] = Important: fix, don't waive)
                                                     in a new polish.md section; then one line per voice sweep
    python -X utf8 tools/story_polish.py chunks N    work/polish/cNN.txt from that section: voice lines one chunk each
                                                     (c31..), the rest in N chunks (c21..)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import voice_scan  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
POLISH = ROOT / "docs/polish.md"
HEAD = "## Phase 9 story pass (worker 23; [I] = Important from the story reviewer: fix, never waive)"
VOICE = {  # sweep -> what the agent does with each id in work/polish/voice_<sweep>.txt
    "suzu": "Suzu's のです/です ending: restore her childlike \"..., it is\" tag (\"Please go safely, it is~!\") on the "
            "lines where the JP ends in のです/です and it reads naturally; keep third-person \"Suzu\" and \"Hawawa\"",
    "ken": "Ken (鍵) is courtly-folksy (style-reference retainer row): drop g-dropping and \"ain't\"/\"sorta\" (Toji's "
           "markers), \"young master\" never \"sir\", vary \"Oh my\" with \"Well now\"/\"Ah\"",
    "shibu": "Shibukawa's comma-pause speech (待たせた、な): keep the halting pauses and clipped brevity "
             "(\"Sorry... for the wait.\", \"...You came, then. Work, is it?\")",
    "shu": "Shu's comma-halting speech (、 mid-phrase): keep the odd pauses (\"Squares. I was, looking.\", "
           "\"Lovely squares, are waiting.\")",
    "nagahide": "Nagahide's Aki (Hiroshima) dialect: his own markers \"ye\" (you), \"yer\" (your), tag \"I tell ya\", "
                "\"Osu!!\"; one scheme throughout (not \"ya\" for you, not Scots \"wee\"), so he is not a second Toji",
    "honestly": "まったく/やれやれ rendered \"Honestly\"/\"Good grief\" for every speaker: vary per speaker "
                "(Mao \"Tsk.\"/\"Bah,\"/\"Truly,\"; Isachi \"Tch, kids...\"; Migiri \"Tch.\"; Hisae \"Really,\"; "
                "Benio \"What manner of person...\"); Tomoe and Seishiro keep theirs",
    "mao_honestly": "Mao's \"Honestly\" is Tomoe's tic: \"Tsk.\" / \"Bah,\" / \"Truly,\" (archaic, haughty)",
    "soft_hehe": "ふふ as \"Hehe\" for Kaname (\"Fufu.\"/\"Hm, hm.\"), Asako, Minori, Benio, Hisae (\"Hee hee\"/\"Hm hm\")",
    "angie_ne": "Angie's ネ ending: keep \"ne\" and her foreign-speaker English (uncontracted, \"Angie\" in third "
                "person) consistent with ms09_01:295-309",
    "ichiru_hehe": "Ichiru's えへへ is \"Ehehe\" (style-reference), never \"Hehe\"",
    "hisae_roman": "Hisae's 浪漫 catchphrase is \"How romantic\"/\"romance\" (synopsis)",
}


def append():
    items = []
    for f in sorted((ROOT / "work/qa/story/reports").glob("*.md")):
        sec = None
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("####"):
                sec = "I" if "Important" in line else "M" if "Minor" in line else None
            elif line.startswith("### "):
                sec = None
            elif sec and line.startswith("- "):
                items.append(f"- [ ] {'[I] ' if sec == 'I' else ''}{f.stem}: {line[2:]}")
    voice = []
    for name, what in VOICE.items():
        ids = [e["id"] for e in voice_scan.entries() if voice_scan.SWEEPS[name](e)]
        (ROOT / f"work/polish/voice_{name}.txt").write_text("".join(i + "\n" for i in ids), encoding="utf-8")
        voice.append(f"- [ ] [I] voice:{name}: {what} ({len(ids)} ids in work/polish/voice_{name}.txt)")
    text = POLISH.read_text(encoding="utf-8").rstrip("\n")
    assert HEAD not in text, "section already appended"
    POLISH.write_text(text + f"\n\n{HEAD}\n" + "\n".join(items + voice) + "\n", encoding="utf-8", newline="\n")
    print(len(items), "items,", len(voice), "voice lines")


def chunks(n):
    lines = POLISH.read_text(encoding="utf-8").split("\n")
    start = lines.index(HEAD)
    todo = [(i + 1, s) for i, s in enumerate(lines) if i > start and s.startswith("- [ ] ")]
    voice = [t for t in todo if " voice:" in t[1]]
    rest = [t for t in todo if t not in voice]
    out = ROOT / "work/polish"
    for k, t in enumerate(voice):
        (out / f"c{31 + k}.txt").write_text(f"{t[0]}\t{t[1]}\n", encoding="utf-8")
    size = -(-len(rest) // n)
    for k in range(n):
        part = rest[k * size:(k + 1) * size]
        (out / f"c{21 + k}.txt").write_text("".join(f"{i}\t{s}\n" for i, s in part), encoding="utf-8")
    print(f"voice c31..c{30 + len(voice)}, rest c21..c{20 + n} (<= {size} lines)")


if __name__ == "__main__":
    {"append": lambda: append(), "chunks": lambda: chunks(int(sys.argv[2]))}[sys.argv[1]]()
