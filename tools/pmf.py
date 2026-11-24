"""pmf.py: PSP PSMF movies (.PMF): read the H.264 stream, swap in a re-encoded one without touching the container.

    python -X utf8 tools/pmf.py info MOVIE.PMF          # packs, frames, keyframes, frame sizes
    python -X utf8 tools/pmf.py es MOVIE.PMF OUT.264    # the video elementary stream (Annex B)

A PMF is a 0x800-byte PSMF header (stream info, EP map) + 2048-byte MPEG-PS packs; video is PES stream 0xE0, the
PSP's own per-pack tables are private stream 2 (0xBF). Re-muxing from scratch would have to rebuild all of that, so
`swap` keeps every pack, PES header, timestamp and table byte for byte and only overwrites the 0xE0 payload bytes:
the new stream must have the same access units (frames) with each one no bigger than the original's, padded to the
same size with a filler NAL (type 12) and trailing zeros. Same frame count, same keyframes (EP map), same sizes ->
the container stays valid on hardware as well as in PPSSPP.
"""
import argparse
import struct
import sys

PACK = 2048


def pes_payloads(data):
    """[(offset, length)] of every video (0xE0) PES payload, in stream order."""
    out = []
    pos = 0x800 if data[:4] == b"PSMF" else 0
    while pos + 4 <= len(data):
        if data[pos:pos + 3] != b"\x00\x00\x01":
            raise ValueError(f"no start code at 0x{pos:x}")
        sid = data[pos + 3]
        if sid == 0xBA:                             # pack header (MPEG-2): 14 bytes + stuffing
            pos += 14 + (data[pos + 13] & 7)
            continue
        if sid == 0xB9:                             # program end
            pos += 4
            continue
        n = struct.unpack(">H", data[pos + 4:pos + 6])[0]
        if sid == 0xE0:
            hl = data[pos + 8]                      # MPEG-2 PES: flags, flags, header length
            out.append((pos + 9 + hl, n - 3 - hl))
        pos += 6 + n
    return out


def es(data):
    return b"".join(data[o:o + n] for o, n in pes_payloads(data))


def nals(stream):
    """[(start of the start code, nal type)] in an Annex B stream."""
    out = []
    i = stream.find(b"\x00\x00\x01")
    while i >= 0:
        s = i - 1 if i > 0 and stream[i - 1] == 0 else i
        out.append((s, stream[i + 3] & 0x1F))
        i = stream.find(b"\x00\x00\x01", i + 3)
    return out


def access_units(stream):
    """Split at access unit delimiters (type 9) or, without them, before each SPS/first slice (first_mb == 0)."""
    ns = nals(stream)
    starts = []
    if any(t == 9 for _, t in ns):
        starts = [s for s, t in ns if t == 9]
    else:
        seen_slice = False
        pending = None
        for s, t in ns:
            if t in (6, 7, 8) and pending is None:
                pending = s
            if t in (1, 5):
                hdr = stream.find(b"\x00\x00\x01", s) + 4
                first_mb_zero = stream[hdr] & 0x80     # ue(v) first_mb_in_slice == 0 -> leading bit 1
                if first_mb_zero:
                    starts.append(pending if pending is not None else s)
                    seen_slice = True
                pending = None
        if not seen_slice:
            raise ValueError("no slices")
    starts[0] = 0
    return [stream[a:b] for a, b in zip(starts, starts[1:] + [len(stream)])]


def is_key(au):
    return any(t == 5 for _, t in nals(au))


def pad(au, size):
    """au padded to exactly size bytes: filler NAL (00 00 01 0C FF.. 80) then zero bytes."""
    room = size - len(au)
    if room < 0:
        raise ValueError(f"frame {len(au)} > {size}")
    if room >= 6:
        return au + b"\x00\x00\x01\x0c" + b"\xff" * (room - 5) + b"\x80"
    return au + b"\x00" * room


def swap(data, new_aus):
    """data with its video payload replaced by new_aus padded to the original frame sizes."""
    old = access_units(es(data))
    if len(old) != len(new_aus):
        raise ValueError(f"{len(new_aus)} frames, original has {len(old)}")
    over = [(i, len(n), len(o)) for i, (o, n) in enumerate(zip(old, new_aus)) if len(n) > len(o)]
    if over:
        raise ValueError(f"{len(over)} frames too big (index, new, old): {over[:8]}")
    keys = [i for i, o in enumerate(old) if is_key(o)]
    nkeys = [i for i, n in enumerate(new_aus) if is_key(n)]
    if keys != nkeys:
        raise ValueError(f"keyframes differ: original {keys}, new {nkeys}")
    stream = b"".join(pad(n, len(o)) for o, n in zip(old, new_aus))
    out = bytearray(data)
    pos = 0
    for o, n in pes_payloads(data):
        out[o:o + n] = stream[pos:pos + n]
        pos += n
    assert pos == len(stream)
    return bytes(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["info", "es"])
    ap.add_argument("pmf")
    ap.add_argument("out", nargs="?")
    a = ap.parse_args()
    data = open(a.pmf, "rb").read()
    stream = es(data)
    if a.cmd == "es":
        open(a.out, "wb").write(stream)
        return
    aus = access_units(stream)
    keys = [i for i, au in enumerate(aus) if is_key(au)]
    sizes = [len(au) for au in aus]
    print(f"{len(data)} bytes, {len(pes_payloads(data))} video PES, {len(aus)} frames, keyframes {keys}")
    print(f"frame bytes min {min(sizes)} max {max(sizes)} mean {sum(sizes) // len(sizes)}")
    print("nal types of frame 0/1:", [t for _, t in nals(aus[0])], [t for _, t in nals(aus[1])])


if __name__ == "__main__":
    sys.exit(main())
