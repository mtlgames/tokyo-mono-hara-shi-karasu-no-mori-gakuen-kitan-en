"""ipk.py: the game's bitmap font format (app_init.pak/system/font/*.ipk). Format: docs/re/font.md.

`IPK ` u32 size, then chunks (tag, u32 size incl. 8-byte header): INFO, CLUT, IMG , TERM (size 0).
INFO: u16 glyphs, u16 2, u16 page w, u16 page h, u16 cell w, u16 cell h, then per glyph (sorted by code)
      u16 SJIS code (ASCII and half-width kana as one byte), u8 width (advance), u8 ink height, u16 0.
IMG:  u32 ?, u32 page bytes, then pages of 4bpp linear pixels (low nibble = left pixel);
      glyph i is cell (i % per_page) of page i // per_page, cells left to right, top to bottom.

    python -X utf8 tools/ipk.py FONT.ipk OUT.png [FIRST [COUNT]]   # render glyphs to a sheet
"""
import struct
import sys


class Font:
    def __init__(self, data):
        self.data = bytearray(data)
        o, self.chunks = 8, {}
        while True:
            tag, size = self.data[o:o + 4].decode(), struct.unpack_from("<I", self.data, o + 4)[0]
            self.chunks[tag] = o
            if size == 0:
                break
            o += size
        i = self.chunks["INFO"] + 8
        n, _, self.pw, self.ph, self.cw, self.ch = struct.unpack_from("<6H", self.data, i)
        self.info = i + 12
        self.codes = {struct.unpack_from("<H", self.data, self.info + 6 * k)[0]: k for k in range(n)}
        self.img = self.chunks["IMG "] + 8 + 8
        self.cols = self.pw // self.cw
        self.per_page = self.cols * (self.ph // self.ch)

    def index(self, code):
        return self.codes[code]

    def metrics(self, k):
        return struct.unpack_from("<BB", self.data, self.info + 6 * k + 2)

    def set_metrics(self, k, width, height):
        struct.pack_into("<BB", self.data, self.info + 6 * k + 2, width, height)

    def _pos(self, k, x, y):
        page, cell = divmod(k, self.per_page)
        px = (cell % self.cols) * self.cw + x
        py = (cell // self.cols) * self.ch + y
        return self.img + page * self.pw * self.ph // 2 + (py * self.pw + px) // 2, px & 1

    def glyph(self, k):
        """Rows of 4-bit values, cw x ch."""
        out = []
        for y in range(self.ch):
            row = []
            for x in range(self.cw):
                a, hi = self._pos(k, x, y)
                row.append(self.data[a] >> 4 if hi else self.data[a] & 15)
            out.append(row)
        return out

    def set_glyph(self, k, rows):
        for y in range(self.ch):
            for x in range(self.cw):
                a, hi = self._pos(k, x, y)
                v = rows[y][x] if y < len(rows) and x < len(rows[y]) else 0
                self.data[a] = (self.data[a] & 0x0F) | (v << 4) if hi else (self.data[a] & 0xF0) | v

    def sheet(self, first=0, count=256, scale=2):
        from PIL import Image
        cols = 32
        im = Image.new("L", (cols * (self.cw + 1), (count + cols - 1) // cols * (self.ch + 1)), 40)
        for n, k in enumerate(range(first, min(first + count, len(self.codes)))):
            g = self.glyph(k)
            w = self.metrics(k)[0]
            ox, oy = n % cols * (self.cw + 1), n // cols * (self.ch + 1)
            for y in range(self.ch):
                for x in range(self.cw):
                    im.putpixel((ox + x, oy + y), g[y][x] * 17 if g[y][x] else (0 if x < w else 25))
        return im.resize((im.width * scale, im.height * scale), Image.NEAREST)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    f = Font(open(sys.argv[1], "rb").read())
    a = [int(x, 0) for x in sys.argv[3:]]
    f.sheet(*a).save(sys.argv[2])
    print(f"{len(f.codes)} glyphs, cell {f.cw}x{f.ch}, page {f.pw}x{f.ph} -> {sys.argv[2]}")
