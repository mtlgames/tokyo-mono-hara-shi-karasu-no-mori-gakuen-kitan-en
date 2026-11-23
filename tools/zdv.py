"""zdv.py: the game's .zdv compression wrapper: LE u32 usize, u32 usize, u32 1, u32 csize, then a zlib stream.
csize 0xFFFFFFFF means the payload is stored uncompressed."""
import struct
import zlib

STORED = 0xFFFFFFFF


def inflate(d):
    usize, usize2, n, csize = struct.unpack_from("<4I", d)
    assert n == 1 and usize == usize2, "unknown zdv variant"
    out = d[16:16 + usize] if csize == STORED else zlib.decompress(d[16:16 + csize])
    assert len(out) == usize
    return out


def is_stored(d):
    return struct.unpack_from("<I", d, 12)[0] == STORED


def deflate(u, level=6, stored=False):
    """Level 6 reproduces all 11,283 compressed originals byte for byte (phase 3 identity build)."""
    if stored:
        return struct.pack("<4I", len(u), len(u), 1, STORED) + u
    c = zlib.compress(u, level)
    return struct.pack("<4I", len(u), len(u), 1, len(c)) + c
