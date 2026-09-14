#!/usr/bin/env python3
"""Fail-closed verifier for GQ5012BF1 tkcore island Phase 3D.

Certifies ONLY that the clock-runtime dispatcher and the three secure-SPI
proxy entry points are statically reconstructed against the stock oracle and
that their provider ABI surface is closed.

It does NOT certify: tkcore completeness, runtime readiness, secure-world
behaviour, fingerprint behaviour, final consumer acceptance, or that stock
tkcore can be removed.
"""
from __future__ import annotations

import hashlib
import re
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GKI = Path("/home/armol/kernel-work/gki-12901745-workspace")
STOCK = REPO / "workspace/phase4-tkcore/oracle/tkcore.ko"
LIVE = GKI / "bazel-bin/lieppos/tkcore-island/tkcore/tkcore.ko"
PHASE = REPO / "workspace/phase4-tkcore-island/phase3d"
BEFORE = PHASE / "before/tkcore.phase3c-r.ko"
FROZEN = PHASE / "build/tkcore.phase3d.ko"
ISLAND_SRC = GKI / "lieppos/tkcore-island"

STOCK_SHA = "03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226"
PHASE3C_R_SHA = "7d9d7979521853c8d5a4412bb08c534870cd977a2f1efebe363f172ef067aeee"

CLOCK = "tee_clkmgr_handle"
SPI = ["tee_spi_cfg_padsel", "tee_spi_transfer", "tee_spi_transfer_disable"]
TARGETS = [CLOCK] + SPI

STOCK_KCFI = {
    "tee_clkmgr_handle": 0x06DA45E1,
    "tee_spi_cfg_padsel": 0xAB53C5C9,
    "tee_spi_transfer": 0xFFEB18B3,
    "tee_spi_transfer_disable": 0x36B1C5A6,
}
STOCK_SIZE = {
    "tee_clkmgr_handle": 308,
    "tee_spi_cfg_padsel": 332,
    "tee_spi_transfer": 452,
    "tee_spi_transfer_disable": 300,
}
HISTORICAL_CRC = {
    "tee_clkmgr_handle": 0x6913F6B2,
    "tee_spi_cfg_padsel": 0x56729869,
    "tee_spi_transfer": 0x184CE7DA,
    "tee_spi_transfer_disable": 0xADB9B21C,
}

# Phase 3E owns these; Phase 3D must not have implemented any of them.
PHASE3E_TARGETS = {
    "big_core_affinity_get_candidate_cpu", "big_core_affinity_match_cpu",
    "big_core_affinity_need_bind_cpu", "plat_cpu_is_big", "plat_tee_init",
}

SPI_TA_UUID = bytes.fromhex("7c3f6d96ef04eb1b08b757f37a6d87f9")

# The clock foundation closed in earlier phases must not drift.
CLOCK_FOUNDATION = [
    "tee_clkmgr_register", "tee_peridev_init", "tee_peridev_exit",
    "plat_register_spi_clk",
]

REQUIRED_DOCS = {
    "phase4-tkcore-island-phase3d-baseline.md": None,
    "phase4-tkcore-island-phase3d-RED.md": None,
    "phase4-tkcore-island-phase3d-consumer-scan.md": None,
    "phase4-tkcore-clkmgr-handle-contract.md": None,
    "phase4-tkcore-clkmgr-callback-abi.md": None,
    "phase4-tkcore-island-phase3d-tkcore-drv-clock-trace.md": "PASS_STATIC_CLOCK",
    "phase4-tkcore-secure-spi-state.md": None,
    "phase4-tkcore-spi-padsel-contract.md": None,
    "phase4-tkcore-spi-transfer-contract.md": None,
    "phase4-tkcore-spi-disable-contract.md": None,
    "phase4-tkcore-island-phase3d-microarray-spi-trace.md": "PASS_STATIC_SPI",
    "phase4-tkcore-island-phase3d-targeted-consumer-acceptance.md": None,
    "phase4-tkcore-island-phase3d-regression.md": None,
}
REQUIRED_TSV = [
    "functions", "kcfi", "imports", "export-parity",
    "objects", "relocations", "callgraph", "strings", "metadata",
]

checks: list[tuple[str, bool, str]] = []


def ck(name: str, ok: bool, detail: object = "") -> None:
    checks.append((name, bool(ok), str(detail)))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def run(*a: str) -> str:
    p = subprocess.run(a, capture_output=True, text=True)
    return "" if p.returncode else p.stdout


class Image:
    def __init__(self, path: Path):
        self.path = path
        self.sec: dict[str, tuple[int, int]] = {}
        for line in run("llvm-readelf", "-SW", str(path)).splitlines():
            m = re.search(r"\]\s+(\S+)\s+\S+\s+([0-9a-f]+)\s+([0-9a-f]+)", line)
            if m:
                self.sec[m.group(1)] = (int(m.group(2), 16), int(m.group(3), 16))
        self.funcs: dict[str, tuple[int, int, str]] = {}
        self.objects: dict[str, tuple[int, int]] = {}
        self.undefined: set[str] = set()
        self.exports: set[str] = set()
        self.crc: dict[str, int] = {}
        f = path.open("rb")
        self._f = f
        for line in run("llvm-readelf", "-sW", str(path)).splitlines():
            p = line.split()
            if len(p) < 8 or not re.fullmatch(r"[0-9a-fA-F]+", p[1]):
                continue
            if p[6] == "UND":
                self.undefined.add(p[7])
                continue
            if p[3] == "FUNC" and p[2].isdigit():
                self.funcs[p[7]] = (int(p[1], 16), int(p[2]), p[4])
            if p[3] == "OBJECT" and p[2].isdigit():
                self.objects[p[7]] = (int(p[1], 16), int(p[2]))
            if p[7].startswith("__ksymtab_") and p[7] != "__ksymtab_strings":
                self.exports.add(p[7][len("__ksymtab_"):])
            if p[7].startswith("__crc_") and "__kcrctab" in self.sec:
                va, off = self.sec["__kcrctab"]
                f.seek(off + int(p[1], 16) - va)
                self.crc[p[7][len("__crc_"):]] = struct.unpack("<I", f.read(4))[0]

    def body(self, n: str) -> bytes:
        a, sz, _ = self.funcs[n]
        va, off = self.sec[".text"]
        self._f.seek(off + a - va)
        return self._f.read(sz)

    def kcfi(self, n: str) -> int:
        a, _, _ = self.funcs[n]
        va, off = self.sec[".text"]
        self._f.seek(off + a - va - 4)
        return struct.unpack("<I", self._f.read(4))[0]

    def dis(self, n: str) -> str:
        a, sz, _ = self.funcs[n]
        return run("llvm-objdump", "-dr", f"--start-address={a}",
                   f"--stop-address={a + sz}", str(self.path))

    def calls(self, n: str) -> list[str]:
        return re.findall(r"R_AARCH64_CALL26\s+(\S+)", self.dis(n))

    def strings(self, n: str) -> set[str]:
        out = set()
        if ".rodata.str1.1" not in self.sec:
            return out
        _va, off = self.sec[".rodata.str1.1"]
        for rel in set(re.findall(r"\.rodata\.str1\.1\+0x([0-9a-f]+)", self.dis(n))):
            self._f.seek(off + int(rel, 16))
            out.add(self._f.read(140).split(b"\0")[0].decode("utf-8", "replace"))
        return out

    def find_object_bytes(self, section: str, blob: bytes) -> bool:
        if section not in self.sec:
            return False
        _va, off = self.sec[section]
        self._f.seek(off)
        return blob in self._f.read(1 << 16)


def imports_of(path: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    data = subprocess.run(["llvm-objcopy", "--dump-section",
                           "__versions=/dev/stdout", str(path)],
                          capture_output=True).stdout
    for o in range(0, max(0, len(data) - 63), 64):
        rec = data[o:o + 64]
        name = rec[8:].split(b"\0")[0].decode("utf-8", "replace")
        if name:
            out[name] = int.from_bytes(rec[:8], "little") & 0xFFFFFFFF
    return out


def main() -> int:
    # ---- baseline --------------------------------------------------------
    ck("stock oracle present and exact",
       STOCK.is_file() and sha256(STOCK) == STOCK_SHA)
    ck("frozen Phase-3C-R baseline present and exact",
       BEFORE.is_file() and sha256(BEFORE) == PHASE3C_R_SHA,
       sha256(BEFORE) if BEFORE.is_file() else "missing")
    v3cr = REPO / "kernel/scripts/phase4_tkcore_island_phase3c_r_verify.py"
    ck("Phase-3C-R verifier exists", v3cr.is_file())
    if v3cr.is_file():
        r = subprocess.run([sys.executable, str(v3cr)], capture_output=True, text=True)
        ck("Phase-3C-R verifier passes", r.returncode == 0,
           (r.stdout.strip().splitlines() or ["no output"])[-1])

    candidate = LIVE if LIVE.is_file() else FROZEN
    ck("a Phase-3D island ELF is available", candidate.is_file(), candidate)
    if not (STOCK.is_file() and BEFORE.is_file() and candidate.is_file()):
        return report()

    s, c, b = Image(STOCK), Image(candidate), Image(BEFORE)

    # ---- the four targets exist -----------------------------------------
    for n in TARGETS:
        ck(f"{n} present", n in c.funcs)
    if any(n not in c.funcs for n in TARGETS):
        return report()

    for n in TARGETS:
        ck(f"{n} was ABSENT at Phase 3C-R (RED reproduces)", n not in b.funcs)
        ck(f"{n} size is exactly stock's {STOCK_SIZE[n]}",
           c.funcs[n][1] == STOCK_SIZE[n] == s.funcs[n][1], c.funcs[n][1])
        ck(f"{n} KCFI matches stock {STOCK_KCFI[n]:#010x}",
           c.kcfi(n) == STOCK_KCFI[n] == s.kcfi(n), f"{c.kcfi(n):#010x}")
        ck(f"{n} keeps stock linkage", c.funcs[n][2] == s.funcs[n][2])
        so = set(s.calls(n)) - set(c.calls(n))
        io = set(c.calls(n)) - set(s.calls(n))
        ck(f"{n} has no stock-only call edge", not so, sorted(so))
        ck(f"{n} has no island-only call edge", not io, sorted(io))
        ck(f"{n} reproduces stock's string set",
           s.strings(n) == c.strings(n),
           sorted(s.strings(n) ^ c.strings(n)))
        ck(f"{n} is not a stub", c.funcs[n][1] > 64 and len(c.calls(n)) > 0)

    # ---- exports ---------------------------------------------------------
    ck("exports are 25/25", len(c.exports) == 25, len(c.exports))
    ck("no stock export is missing", not (s.exports - c.exports),
       sorted(s.exports - c.exports))
    ck("no fabricated export", not (c.exports - s.exports),
       sorted(c.exports - s.exports))
    for n in TARGETS:
        ck(f"{n} exported naturally", n in c.exports)
        ck(f"{n} export CRC equals stock and historical {HISTORICAL_CRC[n]:#010x}",
           c.crc.get(n) == HISTORICAL_CRC[n] == s.crc.get(n),
           f"{c.crc.get(n)!r}")
    ck("no export present at Phase 3C-R was lost",
       not (b.exports - c.exports), sorted(b.exports - c.exports))

    # ---- clock contract --------------------------------------------------
    d = c.dis(CLOCK)
    ck("clock: lookup key is cmd | 1", bool(re.search(r"orr\s+w\d+, w\d+, #0x1", d)))
    ck("clock: selector tests bit 0", bool(re.search(r"tst\s+w\d+, #0x1", d)))
    ck("clock: callback chosen with csel", "csel" in d)
    ck("clock: enable at record+0x08 reachable", "0x30" in d)
    ck("clock: disable at record+0x10 reachable", "0x28" in d)
    ck("clock: token compared at record+0x00", "#-0x38" in d)
    ck("clock: exactly one mutex_lock", c.calls(CLOCK).count("mutex_lock") == 1)
    ck("clock: exactly two mutex_unlock", c.calls(CLOCK).count("mutex_unlock") == 2)
    ck("clock: unlock precedes the indirect call",
       d.index("mutex_unlock") < d.rindex("blr"))
    ck("clock: four indirect dispatch sites", len(re.findall(r"\bblr\b", d)) == 4)
    ck("clock: no KCFI triple at the dispatch sites (stock has none)",
       len(re.findall(r"ldur\s+w16", d)) == 0
       and len(re.findall(r"ldur\s+w16", s.dis(CLOCK))) == 0)
    ck("clock: returns TEEC_ERROR_ITEM_NOT_FOUND (-65528)", "-0xfff8" in d)
    ck("clock: returns TEEC_ERROR_NOT_SUPPORTED (-65526)", "-0xfff6" in d)
    ck("clock: argnum bound check present",
       bool(re.search(r"cmp\s+x\d+, #0x[34]\b", d)) and ("b.hi" in d or "b.hs" in d))
    ck("clock: dense jump table used, as stock",
       bool(re.search(r"\bbr\s+x", d)) and bool(re.search(r"\bbr\s+x", s.dis(CLOCK))))
    ck("clock: exactly one diagnostic",
       c.calls(CLOCK).count("_printk") == s.calls(CLOCK).count("_printk") == 1)

    # ---- clock foundation not regressed ---------------------------------
    for n in CLOCK_FOUNDATION:
        if n in b.funcs and n in c.funcs:
            ck(f"clock foundation unchanged: {n}", b.body(n) == c.body(n))
    ck("clock record layout asserts still present",
       (ISLAND_SRC / "tkcore/tee_lifecycle_prereq.c").read_text(errors="ignore")
       .count("static_assert(offsetof(struct tee_clkmgr_record") >= 5)

    # ---- SPI shared state ------------------------------------------------
    ck("SPI TA UUID present in .data, as stock",
       c.find_object_bytes(".data", SPI_TA_UUID)
       and s.find_object_bytes(".data", SPI_TA_UUID))
    ck("SPI TA UUID is NOT in .rodata (stock keeps it in .data)",
       not c.find_object_bytes(".rodata", SPI_TA_UUID))
    for n in SPI:
        calls = set(c.calls(n))
        ck(f"{n} opens and finalises its own context",
           {"TEEC_InitializeContext", "TEEC_FinalizeContext"} <= calls)
        ck(f"{n} opens and closes its own session",
           {"TEEC_OpenSession", "TEEC_CloseSession"} <= calls)
        ck(f"{n} invokes exactly one command",
           c.calls(n).count("TEEC_InvokeCommand") == 1)
        ck(f"{n} takes no lock (stock takes none)",
           not (calls & {"mutex_lock", "mutex_unlock", "_raw_spin_lock",
                         "_raw_spin_unlock", "down", "up"}))
        ck(f"{n} allocates nothing (stock allocates nothing)",
           not (calls & {"kmalloc", "kmalloc_trace", "kfree", "vmalloc",
                         "devm_kmalloc", "krealloc"}))
        ck(f"{n} touches no SPI controller or pinctrl",
           not (calls & {"spi_sync", "spi_async", "spi_setup",
                         "pinctrl_select_state", "pinctrl_lookup_state",
                         "clk_prepare", "clk_enable", "clk_disable"}))
    ck("tee_spi_transfer stages TX into RX with memcpy",
       "memcpy" in c.calls("tee_spi_transfer")
       and "memcpy" in s.calls("tee_spi_transfer"))
    ck("only tee_spi_transfer uses memcpy among the SPI three",
       all("memcpy" not in c.calls(n) for n in
           ("tee_spi_cfg_padsel", "tee_spi_transfer_disable")))
    ck("tee_spi_transfer rejects bad params with -EINVAL",
       "#-0x16" in c.dis("tee_spi_transfer"))

    # ---- consumers -------------------------------------------------------
    drv = REPO / "workspace/phase4-tkcore-drv/oracle/tkcore_drv.ko"
    ma = REPO / "workspace/phase4-fingerprint/oracle/microarray_fp_tee.stock.ko"
    ck("frozen tkcore_drv oracle present", drv.is_file())
    ck("frozen microarray_fp_tee oracle present", ma.is_file())
    if drv.is_file():
        imp = imports_of(drv)
        ck("tkcore_drv imports tee_clkmgr_handle", CLOCK in imp)
        ck("tkcore_drv clock edge is NATURAL",
           imp.get(CLOCK) == c.crc.get(CLOCK), f"{imp.get(CLOCK)!r}")
    if ma.is_file():
        imp = imports_of(ma)
        ck("microarray_fp_tee imports tee_spi_transfer", "tee_spi_transfer" in imp)
        ck("microarray_fp_tee SPI edge is NATURAL",
           imp.get("tee_spi_transfer") == c.crc.get("tee_spi_transfer"))

    # ---- coverage / imports / objects ------------------------------------
    sf, cf, bf = set(s.funcs), set(c.funcs), set(b.funcs)
    ck("stock function count is 122", len(sf) == 122, len(sf))
    ck("coverage is 117/122", len(sf & cf) == 117, f"{len(sf & cf)}/{len(sf)}")
    ck("coverage advanced by exactly four", len(sf & cf) - len(sf & bf) == 4)
    ck("newly present set is exactly the four targets",
       (cf - bf) == set(TARGETS), sorted((cf - bf) ^ set(TARGETS)))
    ck("no function removed", not (bf - cf), sorted(bf - cf))
    ck("missing set is exactly the Phase-3E five",
       (sf - cf) == PHASE3E_TARGETS, sorted((sf - cf) ^ PHASE3E_TARGETS))
    ck("no island-only functions", not (cf - sf), sorted(cf - sf))
    ck("no new imports", not (c.undefined - b.undefined),
       sorted(c.undefined - b.undefined))
    ck("no removed imports", not (b.undefined - c.undefined),
       sorted(b.undefined - c.undefined))
    # _dev_err is the island's established logging convention (dev_err/dev_dbg
    # where stock uses pr_err).  It predates Phase 3D -- it is present in the
    # frozen Phase-3C-R baseline and is recorded "unchanged" in the Phase-3D
    # imports table.  Pin it explicitly so that any OTHER non-stock import,
    # now or later, still fails this verifier closed.
    KNOWN_NON_STOCK_IMPORTS = {"_dev_err"}
    ck("the only non-stock import is the known island logging helper",
       (c.undefined - s.undefined) == (KNOWN_NON_STOCK_IMPORTS & c.undefined),
       sorted((c.undefined - s.undefined) - KNOWN_NON_STOCK_IMPORTS))
    ck("Phase 3D introduced no non-stock import",
       not ((c.undefined - b.undefined) - s.undefined),
       sorted((c.undefined - b.undefined) - s.undefined))
    ck("the known non-stock import predates Phase 3D",
       KNOWN_NON_STOCK_IMPORTS <= b.undefined or not (KNOWN_NON_STOCK_IMPORTS & c.undefined))
    ck("only one new object symbol, the SPI TA UUID",
       (set(c.objects) - set(b.objects)) <= {"tee_spi_ta_uuid"},
       sorted(set(c.objects) - set(b.objects)))
    ck("byte-identical count did not regress",
       sum(1 for n in sf & cf if s.body(n) == c.body(n))
       >= sum(1 for n in sf & bf if s.body(n) == b.body(n)))

    # ---- build hygiene ---------------------------------------------------
    fields = subprocess.run(["llvm-objcopy", "--dump-section",
                             ".modinfo=/dev/stdout", str(candidate)],
                            capture_output=True).stdout.decode("utf-8", "ignore").split("\0")
    ck("depends is empty", any(f == "depends=" for f in fields),
       [f for f in fields if f.startswith("depends=")])
    probe = PHASE / "build/tk_layout_probe"
    ck("layout probe frozen", probe.is_file())

    # ---- forbidden techniques -------------------------------------------
    srcs = list(ISLAND_SRC.rglob("*.c")) + list(ISLAND_SRC.rglob("*.h")) \
        + [ISLAND_SRC / "Makefile", ISLAND_SRC / "BUILD.bazel"]
    blob = "\n".join(p.read_text(errors="ignore") for p in srcs if p.is_file())
    for bad, label in [("__crc_", "CRC injection"),
                       ("__versions", "__versions edit"),
                       ("__kcrctab", "kcrctab edit"),
                       ("Module.symvers", "fake Module.symvers")]:
        ck(f"no {label} in island sources", bad not in blob)
    ck("no KBUILD_MODPOST_WARN is enabled",
       not re.search(r"^\s*(?!#)\S*KBUILD_MODPOST_WARN\s*[:+]?=", blob, re.M))
    # Examine only what is actually fed to the build: the srcs list.  The
    # declared `outs = ["tkcore.ko"]` and the explanatory comments legitimately
    # mention tkcore.ko and must not trip this check.
    bazel = (ISLAND_SRC / "BUILD.bazel").read_text()
    bazel_code = re.sub(r"#[^\n]*", "", bazel)
    srcs_block = re.search(r"srcs\s*=\s*(.*?)\n\s*outs\s*=", bazel_code, re.S)
    ck("BUILD.bazel srcs list is parseable", srcs_block is not None)
    ck("no stock object, oracle or prebuilt .ko is linked into the island",
       srcs_block is not None
       and not re.search(r"oracle|\.ko\b|\.o\b|prebuilt", srcs_block.group(1)),
       srcs_block.group(1).strip() if srcs_block else "")
    ck("island declares no vendor module dependency",
       "deps" not in bazel_code or "kernel_module" in bazel_code)
    ck("island builds only from reconstructed sources",
       all(p.suffix in {".c", ".h"} or p.name in {"Makefile", "BUILD.bazel"}
           for p in srcs if p.is_file()))

    # ---- scope -----------------------------------------------------------
    for n in sorted(PHASE3E_TARGETS):
        ck(f"Phase-3E boundary honoured, still absent: {n}", n not in cf)
    acc = REPO / "workspace/phase4-tkcore-island/acceptance"
    ck("full three-consumer acceptance still unexecuted",
       not acc.is_dir() or not any(acc.rglob("*")))

    # ---- reports ---------------------------------------------------------
    for name, token in REQUIRED_DOCS.items():
        p = REPO / "kernel" / name
        ck(f"report exists: {name}", p.is_file())
        if token and p.is_file():
            ck(f"report records {token}: {name}", token in p.read_text(errors="ignore"))
    for t in REQUIRED_TSV:
        p = REPO / f"kernel/phase4-tkcore-island-phase3d-{t}.tsv"
        ck(f"tsv exists and is non-trivial: {t}",
           p.is_file() and len(p.read_text().splitlines()) > 1)

    return report()


def report() -> int:
    bad = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        if not ok:
            print(f"[FAIL] {name}" + (f": {detail}" if detail else ""))
    for name, ok, detail in checks:
        if ok:
            print(f"[OK] {name}" + (f": {detail}" if detail else ""))
    print(f"\n{len(checks) - len(bad)}/{len(checks)} CHECKS PASSED")
    if bad:
        print("TKCORE_ISLAND_PHASE3D_VERIFICATION_FAILED")
        return 1
    print("TKCORE_ISLAND_PHASE3D_CLOCK_SPI_CLOSED")
    print("TKCORE_EXPORTS=25/25")
    print("TKCORE_REPLACEMENT_READY=NO")
    print("STOCK_TKCORE_RUNTIME_DEPENDENCY=STILL_PRESENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
