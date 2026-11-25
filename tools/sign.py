"""Re-sign the patched EBOOT ELF into a ~PSP EBOOT.BIN (AGENTS.md: never ship the plain ELF; PPSSPP boots either).

    python -X utf8 tools/sign.py IN.elf OUT.bin

sign_np -elf (github.com/swarzesherz/sign_np @ ac77d56, GPLv3, source in tools/sign_np/src, copied with its devkit
argument patch from the growlanser-psp-en project) built for Linux and run through WSL. Build it once:
    wsl -e sh -c "cd tools/sign_np/src && gcc -O2 -w -I./libkirk -o ../sign_np *.c libkirk/*.c -lz"
Header kept as the original's: tag 0xD91613F0 (sign_np tag 5) at ~PSP +0xD0, devkit 0x06000010 at +0x78.
Signed EBOOTs are cached by ELF hash in work/sign/cache, so a rebuild with the same ELF needs no WSL.
"""
import hashlib
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN = "tools/sign_np/sign_np"
TAG, TAG_WORD, DEVKIT = 5, 0xD91613F0, 0x06000010


def sign(elf):
    assert elf[:4] == b"\x7fELF", "not an ELF"
    tmp = ROOT / "work" / "sign"
    cached = tmp / "cache" / (hashlib.sha1(elf + struct.pack("<II", TAG, DEVKIT)).hexdigest() + ".bin")
    if cached.exists():
        return check(cached.read_bytes(), elf)
    cached.parent.mkdir(parents=True, exist_ok=True)
    (tmp / "in.elf").write_bytes(elf)
    out = tmp / "out.bin"
    out.unlink(missing_ok=True)
    assert (ROOT / BIN).exists(), f"{BIN} missing: build it (see tools/sign.py docstring)"
    r = subprocess.run(["wsl", "-e", BIN, "-elf", "work/sign/in.elf", "work/sign/out.bin", str(TAG), f"{DEVKIT:x}"],
                       cwd=ROOT, capture_output=True)
    assert r.returncode == 0 and out.exists(), r.stdout.decode(errors="replace")[-500:]
    d = check(out.read_bytes(), elf)
    cached.write_bytes(d)
    return d


def check(d, elf):
    assert d[:4] == b"~PSP" and struct.unpack_from("<I", d, 0xD0)[0] == TAG_WORD, "sign_np output not ~PSP tag 5"
    assert struct.unpack_from("<I", d, 0x28)[0] == len(elf), "~PSP elf_size differs from the input"
    assert struct.unpack_from("<I", d, 0x78)[0] == DEVKIT, "sign_np without the devkit argument: rebuild it"
    return d


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(sign(Path(sys.argv[1]).read_bytes()))
