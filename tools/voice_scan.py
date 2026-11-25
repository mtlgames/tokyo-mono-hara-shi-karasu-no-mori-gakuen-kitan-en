"""Game-wide voice sweeps for the story pass: ids whose English drops a character's speech marker.

    python -X utf8 tools/voice_scan.py [NAME ...]    counts per sweep; --ids NAME prints that sweep's ids, one per line

Sweeps: suzu (のです/です but no "it is"), ken (g-dropping or "ain't"), shibu (Shibukawa: JP 、 pauses, EN without a
pause), mao_honestly, ichiru_hehe, dots6 ("......" for a lone ellipsis), spaced_dash (" -- ").
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def entries():
    for f in sorted((ROOT / "script/pw").glob("*/*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            if e.get("en"):
                yield e


def spk(e, *names):
    s = re.sub(r"\{ruby:([^|}]*)\|[^}]*\}", r"\1", e.get("speaker") or "")
    return s in names


SWEEPS = {
    "suzu": lambda e: spk(e, "鈴") and re.search(r"(の)?です[。！？～…ッ]*$", e["jp"].strip())
    and "it is" not in e["en"],
    "ken": lambda e: spk(e, "鍵") and re.search(r"\b\w+in'|\bain't\b", e["en"]),
    "shibu": lambda e: spk(e, "澁川") and re.search(r"[^\n]、", e["jp"]) and not re.search(r"\.\.\.|,|--", e["en"]),
    "mao_honestly": lambda e: spk(e, "白") and "Honestly" in e["en"],
    "ichiru_hehe": lambda e: spk(e, "いちる") and re.search(r"\bHe+he+\b", e["en"]) and "Ehe" not in e["en"],
    "dots6": lambda e: re.search(r"(?<!\.)\.{6}(?!\.)", e["en"]),
    "spaced_dash": lambda e: " -- " in e["en"],
    "shu": lambda e: spk(e, "蒐") and re.search(r"[^\n]、", e["jp"]) and "," not in e["en"],
    "nagahide": lambda e: spk(e, "長英") and re.search(r"じゃ|けェ|けえ|のう|わし|ほうじゃ", e["jp"])
    and not re.search(r"\b(ye|yer|I tell ya)\b", e["en"]),
    "honestly": lambda e: re.search(r"まったく|全く|やれやれ", e["jp"]) and re.search(r"Honestly|Good grief", e["en"])
    and not spk(e, "巴", "清司郎"),  # Tomoe and Seishiro keep "honestly" (style-reference row)
    "soft_hehe": lambda e: spk(e, "要", "朝子", "弥紀", "紅緒", "久榮") and "ふふ" in e["jp"] and re.search(r"\bHe+he", e["en"]),
    "hisae_roman": lambda e: spk(e, "久榮") and "浪漫" in e["jp"] and "roman" not in e["en"].lower(),
    "angie_ne": lambda e: spk(e, "アンジー") and re.search(r"ネ[。！？～…ッ」]*$", e["jp"].strip()) and not re.search(r"\bne\b", e["en"]),
    "gio_whoa": lambda e: spk(e, "義王", "自信に満ちた声") and "オイオイ" in e["jp"] and re.search(r"\b[Ww]hoa\b", e["en"]),
}


FIX = {  # mechanical sweeps: style-reference `...` for a lone ellipsis, `--` unspaced
    "dots6": lambda s: re.sub(r"(?<!\.)\.{6}(?!\.)", "...", s),
    "spaced_dash": lambda s: s.replace(" -- ", "--"),
    "gio_whoa": lambda s: re.sub(r"\b[Ww]hoa\b", lambda m: "Oi" if m.group()[0] == "W" else "oi", s),  # synopsis: Gio's tag
}


def main(argv):
    if argv[:1] == ["--out"]:  # --out NAME SWEEP..: work/tl/NAME.out.tsv with the fixed English (merge re-wraps)
        rows = []
        for e in entries():
            new = e["en"]
            for n in argv[2:]:
                if SWEEPS[n](e):
                    new = FIX[n](new)
            if new != e["en"]:
                rows.append(f"{e['id']}\t{new.replace(chr(10), ' ')}\n")
        (ROOT / "work/tl" / f"{argv[1]}.out.tsv").write_text("".join(rows), encoding="utf-8", newline="\n")
        print(len(rows), "rows")
        return 0
    if argv[:1] == ["--ids"]:
        for e in entries():
            if SWEEPS[argv[1]](e):
                print(e["id"])
        return 0
    names = argv or list(SWEEPS)
    es = list(entries())
    for n in names:
        print(n, sum(1 for e in es if SWEEPS[n](e)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
