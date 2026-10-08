#!/usr/bin/env python3
"""Offline re-implementation of modpost sumversion (GKI 6.1 scripts/mod/sumversion.c).

srcversion = MD4 over, for every object in <module>.mod (in order), the object's
source_ file plus every deps_ file located directly in the object's directory,
with whitespace, backslash-newline and /* */ comments removed (string literals are
hashed verbatim, // comments ARE hashed). Printed as the four MD4 state words
"%08X" each, truncated to 23 characters.

usage: srcversion.py <module.mod> [--override relpath=file ...]
  --override lets the same dependency list be re-hashed with alternative file
  contents (searching which source revision produced a stock srcversion).
"""
import os, struct, sys

def _lrot(x, n): return ((x << n) | (x >> (32 - n))) & 0xffffffff

class MD4:
    """MD4 exactly as GKI 6.1 sumversion.c computes it. NOTE: that code's
    le32_to_cpu_array()/cpu_to_le32_array() call ntohl()/htonl(), so on a
    little-endian host message words are read BIG-endian (except the two final
    length words, which are stored natively) and the state words are byte-swapped
    before printing. This is NOT standard MD4; it is what modpost actually does."""
    def __init__(self):
        self.h = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]; self.buf = bytearray(); self.n = 0
    def update(self, b):
        self.buf += b; self.n += len(b)
        while len(self.buf) >= 64:
            self._blk(struct.unpack(">16I", bytes(self.buf[:64]))); del self.buf[:64]
    def _blk(self, X):
        a, b, c, d = self.h
        F = lambda x, y, z: (x & y) | (~x & z); G = lambda x, y, z: (x & y) | (x & z) | (y & z); H = lambda x, y, z: x ^ y ^ z
        for i in range(16):
            s = [3, 7, 11, 19][i % 4]
            t = (a + F(b, c, d) + X[i]) & 0xffffffff; a, b, c, d = d, _lrot(t, s), b, c
        for i in range(16):
            idx = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15][i]; s = [3, 5, 9, 13][i % 4]
            t = (a + G(b, c, d) + X[idx] + 0x5a827999) & 0xffffffff; a, b, c, d = d, _lrot(t, s), b, c
        for i in range(16):
            idx = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15][i]; s = [3, 9, 11, 15][i % 4]
            t = (a + H(b, c, d) + X[idx] + 0x6ed9eba1) & 0xffffffff; a, b, c, d = d, _lrot(t, s), b, c
        self.h = [(x + y) & 0xffffffff for x, y in zip(self.h, (a, b, c, d))]
    def words(self):
        blk = bytearray(self.buf) + b"\x80"
        if len(blk) > 56:
            blk += b"\0" * (64 - len(blk)); self._blk(struct.unpack(">16I", bytes(blk))); blk = bytearray()
        blk += b"\0" * (56 - len(blk))
        X = list(struct.unpack(">14I", bytes(blk))) + [(self.n << 3) & 0xffffffff, (self.n >> 29) & 0xffffffff]
        self._blk(X)
        return [struct.unpack("<I", struct.pack(">I", w))[0] for w in self.h]

def parse_file(data, out):
    # byte-for-byte transcription of sumversion.c parse_file/parse_string/parse_comment
    i, L = 0, len(data)
    while i < L:
        c = data[i]
        if c == 0x5c and i + 1 < L and data[i + 1] == 0x0a: i += 2; continue
        if c in b" \t\n\v\f\r": i += 1; continue
        if c == 0x22:
            out.append(c); j = 1
            while j < L - i:
                out.append(data[i + j])
                if data[i + j] == 0x22 and data[i + j - 1] != 0x5c: break
                j += 1
            i += j + 1; continue
        if c == 0x2f and i + 1 < L and data[i + 1] == 0x2a:
            j = 2
            while j < L - i:
                if data[i + j - 1] == 0x2a and data[i + j] == 0x2f: break
                j += 1
            i += j + 1; continue
        out.append(c); i += 1

def deps(objfile, base="."):
    # objfile is used verbatim (as modpost does) for the same-directory test
    d, b = os.path.split(objfile); cmd = os.path.join(base, d, "." + b + ".cmd")
    files = []; check = False
    for line in open(cmd, errors="replace").read().split("\n"):
        line = line.lstrip()
        if line.startswith("source_"): files.append(line[line.rfind(" ") + 1:]); continue
        if line.startswith("deps_"): check = True; continue
        if not check: continue
        if not line.endswith("\\"): break
        p = line.split()[0]
        dd = d + "/"
        k = p.find(dd)
        if k >= 0 and k + len(dd) - 1 == p.rfind("/"): files.append(p)
    return files

def srcversion(modfile, overrides=None, base=None):
    overrides = overrides or {}
    out = bytearray(); used = []
    for obj in open(modfile).read().split():
        for f in deps(obj, base or "."):
            used.append(f)
            src = next((v for k, v in overrides.items() if f.endswith("/" + k)), f)
            parse_file(open(src if os.path.isabs(src) else os.path.join(base or ".", src), "rb").read(), out)
    m = MD4(); m.update(bytes(out)); w = m.words()
    return ("%08X%08X%08X%08X" % tuple(w))[:23], used

if __name__ == "__main__":
    mod = sys.argv[1]; ov = dict(a.split("=", 1) for a in sys.argv[3::2]) if "--override" in sys.argv else {}
    base = os.environ.get("SV_BASE", ".")
    sv, used = srcversion(mod, ov, base)
    print(sv); print(f"{len(used)} files", file=sys.stderr)
