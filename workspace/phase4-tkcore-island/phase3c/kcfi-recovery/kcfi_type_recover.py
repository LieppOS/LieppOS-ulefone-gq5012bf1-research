#!/usr/bin/env python3
"""Recover a C struct tag from a Clang KCFI type id.

Clang -fsanitize=kcfi stores, in the word preceding a function entry point:

    type_id = low 32 bits of xxHash64("_ZTSF" <Itanium mangled func type> "E")

The hash is named in the emitted IR: !{i32 4, !"kcfi-hash", !"xxHash64"}.

This only works when the function SIGNATURE SHAPE is already pinned by binary
evidence (here: the stock call site sets exactly one register and tests a
32-bit result, so the signature is `int f(struct X *)` and X is the single
unknown).  It recovers TAGS ONLY -- KCFI ids do not depend on member names, so
this says nothing about struct members.

Usage:
    python3 kcfi_type_recover.py            # self-test + recover 0xba9dd2d9
"""
from __future__ import annotations

import itertools
import sys

M = (1 << 64) - 1
P1 = 11400714785074694791
P2 = 14029467366897019727
P3 = 1609587929392839161
P4 = 9650029242287828579
P5 = 2870177450012600261


def _rol(x: int, r: int) -> int:
    return ((x << r) | (x >> (64 - r))) & M


def _round(a: int, i: int) -> int:
    return (_rol((a + (i * P2 & M)) & M, 31) * P1) & M


def xxh64(b: bytes, seed: int = 0) -> int:
    n = len(b)
    i = 0
    if n >= 32:
        v1 = (seed + P1 + P2) & M
        v2 = (seed + P2) & M
        v3 = seed & M
        v4 = (seed - P1) & M
        while i + 32 <= n:
            v1 = _round(v1, int.from_bytes(b[i:i + 8], "little"))
            v2 = _round(v2, int.from_bytes(b[i + 8:i + 16], "little"))
            v3 = _round(v3, int.from_bytes(b[i + 16:i + 24], "little"))
            v4 = _round(v4, int.from_bytes(b[i + 24:i + 32], "little"))
            i += 32
        h = (_rol(v1, 1) + _rol(v2, 7) + _rol(v3, 12) + _rol(v4, 18)) & M
        for v in (v1, v2, v3, v4):
            h = (h ^ _round(0, v)) & M
            h = (h * P1) & M
            h = (h + P4) & M
    else:
        h = (seed + P5) & M
    h = (h + n) & M
    while i + 8 <= n:
        k = _round(0, int.from_bytes(b[i:i + 8], "little"))
        h = _rol((h ^ k) & M, 27)
        h = (((h * P1) & M) + P4) & M
        i += 8
    if i + 4 <= n:
        h = (h ^ ((int.from_bytes(b[i:i + 4], "little") * P1) & M)) & M
        h = _rol(h, 23)
        h = (((h * P2) & M) + P3) & M
        i += 4
    while i < n:
        h = (h ^ ((b[i] * P5) & M)) & M
        h = _rol(h, 11)
        h = (h * P1) & M
        i += 1
    h ^= h >> 33
    h = (h * P2) & M
    h ^= h >> 29
    h = (h * P3) & M
    h ^= h >> 32
    return h


def type_id(tag: str) -> int:
    """KCFI id for `int f(struct <tag> *)`."""
    return xxh64(f"_ZTSFiP{len(tag)}{tag}E".encode()) & 0xFFFFFFFF


REFERENCE_VECTORS = {b"": 0xEF46DB3751D8E999,
                     b"a": 0xD24EC4F1A98C6E5B,
                     b"abc": 0x44BC2CF5AD770999}

# Produced independently by clang -fsanitize=kcfi, used to pin the mangling.
COMPILER_ANCHORS = {"tee_cmd_io": 0xBB8E9218,
                    "tee_shm_io": 0xDAEE5623,
                    "tee_spta_inst": 0x014A7540}

VOCAB = ["tee", "spta", "inst", "install", "ta", "sp", "compat", "io", "ioc", "ioctl",
         "arg", "args", "cmd", "command", "data", "info", "desc", "req", "request",
         "param", "params", "blob", "image", "img", "load", "name", "uuid", "size",
         "buf", "buffer", "shm", "mem", "user", "kern", "kernel", "sec", "secure",
         "trusted", "app", "obj", "entry", "item", "rec", "record", "hdr", "header",
         "id", "idx", "num", "op", "ops", "ctx", "sess", "session", "dev", "drv",
         "tkcore", "trustkernel", "tk", "gp", "client", "core", "pta", "sta", "stat",
         "state"]


def selftest() -> bool:
    ok = True
    for data, want in REFERENCE_VECTORS.items():
        got = xxh64(data)
        print(f"  xxh64({data!r:6}) = {got:016x} want {want:016x} "
              f"{'OK' if got == want else 'FAIL'}")
        ok &= got == want
    for tag, want in COMPILER_ANCHORS.items():
        got = type_id(tag)
        print(f"  mangling {tag:14} -> {got:08x} want {want:08x} "
              f"{'OK' if got == want else 'FAIL'}")
        ok &= got == want
    return ok


def search(target: int, depth: int = 4):
    hits, tried = [], 0
    for k in range(1, depth + 1):
        for parts in itertools.product(VOCAB, repeat=k):
            base = "_".join(parts)
            for cand in (base, "_" + base, base + "_t", "__" + base):
                tried += 1
                if type_id(cand) == target:
                    hits.append(cand)
    return hits, tried


if __name__ == "__main__":
    print("self-test:")
    if not selftest():
        sys.exit("hash or mangling self-test FAILED")
    target = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0xBA9DD2D9
    print(f"\nsearching for {target:08x} (pure-python; the Go port is ~100x faster)")
    hits, tried = search(target)
    print(f"tried={tried} hits={hits}")
    if len(hits) == 1:
        print(f"expected false positives at this corpus size: {tried / 2**32:.4f}")
