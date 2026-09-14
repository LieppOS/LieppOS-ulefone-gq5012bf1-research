#!/usr/bin/env python3
"""Fail-closed verifier for GQ5012BF1 tkcore island Phase 3C.

Certifies ONLY the ioctl / compat / command-marshalling static closure plus the
two authorized direct uaccess prerequisites.

It deliberately does NOT certify: runtime readiness, clock runtime, secure SPI,
big-core affinity, platform init, or three-consumer natural-link acceptance.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GKI = Path("/home/armol/kernel-work/gki-12901745-workspace")
STOCK = REPO / "workspace/phase4-tkcore/oracle/tkcore.ko"
LIVE = GKI / "bazel-bin/lieppos/tkcore-island/tkcore/tkcore.ko"
PHASE = REPO / "workspace/phase4-tkcore-island/phase3c"
FROZEN = PHASE / "build/tkcore.phase3c.ko"

STOCK_SHA = "03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226"

PRIMARY = [
    "tee_internal_ioctl",
    "tee_session_internal_ioctl",
    "tee_compat_ioctl",
    "tee_session_compat_ioctl",
    "convert_compat_tee_cmd",
    "convert_compat_tee_shm_io",
    "convert_compat_tee_spta_inst",
]
PREREQ = ["uaccess_ttbr0_enable", "uaccess_ttbr0_disable"]

# Functions whose address is taken (fops slots) or that stock gives a KCFI
# prologue.  Values are the stock type ids.
EXPECTED_KCFI = {
    "convert_compat_tee_cmd": 0xBB8E9218,
    "convert_compat_tee_shm_io": 0xDAEE5623,
    "convert_compat_tee_spta_inst": 0xBA9DD2D9,
    "tee_ioctl": 0xE01408CD,
    "tee_compat_ioctl": 0xE01408CD,
    "tee_session_ioctl": 0xE01408CD,
    "tee_session_compat_ioctl": 0xE01408CD,
}

# Byte-for-byte equality that Phase 3C must not lose.
BYTE_EXACT = ["convert_compat_tee_shm_io", "uaccess_ttbr0_enable", "uaccess_ttbr0_disable"]

# The only functions still permitted to be absent: the explicitly excluded
# clock / SPI / affinity / platform subsystems.
ALLOWED_MISSING = {
    "tee_clkmgr_handle",
    "tee_spi_cfg_padsel",
    "tee_spi_transfer",
    "tee_spi_transfer_disable",
    "big_core_affinity_get_candidate_cpu",
    "big_core_affinity_match_cpu",
    "big_core_affinity_need_bind_cpu",
    "plat_cpu_is_big",
    "plat_tee_init",
}

FOPS_EDGES = {
    ("tee_client_fops", 0x50): "tee_ioctl",
    ("tee_client_fops", 0x58): "tee_compat_ioctl",
    ("tee_admin_fops", 0x50): "tee_ioctl",
    ("tee_admin_fops", 0x58): "tee_compat_ioctl",
    ("tee_session_fops", 0x50): "tee_session_ioctl",
    ("tee_session_fops", 0x58): "tee_session_compat_ioctl",
}

checks: list[tuple[str, bool, str]] = []


def ck(name: str, ok: bool, detail: object = "") -> None:
    checks.append((name, bool(ok), str(detail)))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(*args: str, binary: bool = False):
    p = subprocess.run(args, capture_output=True, text=not binary)
    if p.returncode:
        return b"" if binary else ""
    return p.stdout


class Image:
    def __init__(self, path: Path):
        self.path = path
        self.funcs: dict[str, tuple[int, int, str, int]] = {}
        self.objects: dict[str, tuple[int, int, str, int]] = {}
        self.undefined: set[str] = set()
        self.exports: set[str] = set()
        self.secnames: dict[int, str] = {}
        self.symnames: set[str] = set()
        for line in run("llvm-readelf", "-sW", str(path)).splitlines():
            p = line.split()
            if len(p) < 8 or not re.fullmatch(r"[0-9a-fA-F]+", p[1]):
                continue
            self.symnames.add(p[7])
            if p[6] == "UND":
                self.undefined.add(p[7])
                continue
            if not p[6].isdigit() or not p[2].isdigit():
                continue
            rec = (int(p[1], 16), int(p[2]), p[4], int(p[6]))
            if p[3] == "FUNC":
                self.funcs[p[7]] = rec
            elif p[3] == "OBJECT":
                self.objects[p[7]] = rec
            if p[7].startswith("__ksymtab_") and p[7] != "__ksymtab_strings":
                self.exports.add(p[7][len("__ksymtab_"):])
        for line in run("llvm-readelf", "-SW", str(path)).splitlines():
            m = re.search(r"\[\s*(\d+)\]\s+(\S+)\s+\S+\s+([0-9a-f]+)\s+([0-9a-f]+)", line)
            if m:
                self.secnames[int(m.group(1))] = m.group(2)
        self.text = run("llvm-objcopy", "--dump-section", ".text=/dev/stdout",
                        str(path), binary=True)
        self.relocs: dict[str, list[tuple[int, str]]] = {}
        cur = None
        for line in run("llvm-readelf", "-rW", str(path)).splitlines():
            m = re.match(r"Relocation section '(\S+)'", line)
            if m:
                cur = m.group(1)
                self.relocs[cur] = []
                continue
            p = line.split()
            if cur and p and re.fullmatch(r"[0-9a-fA-F]{8,}", p[0]) and len(p) >= 5:
                self.relocs[cur].append((int(p[0], 16), " ".join(p[4:]), p[2]))

    def kcfi(self, name: str) -> int | None:
        """KCFI type id lives in the word preceding the entry point."""
        if name not in self.funcs:
            return None
        off = self.funcs[name][0]
        return int.from_bytes(self.text[off - 4:off], "little") if off >= 4 else None

    def address_taken(self, name: str) -> bool:
        """True when some NON-.text section stores this function's address.

        This is the property that actually decides whether a function needs a
        KCFI prologue: an indirect-callable slot (a fops table, an ops struct)
        holds its address.  A function only ever reached by `bl` is
        direct-call-only, and stock emits no type word for it.
        """
        if name not in self.funcs:
            return False
        addr, size, _b, sec = self.funcs[name]
        if self.secnames.get(sec) != ".text":
            return False
        for relsec, entries in self.relocs.items():
            if relsec == ".rela.text":
                continue
            for _off, sym, rtype in entries:
                # Only a stored 64-bit pointer makes a function indirectly
                # callable.  __bug_table / __ex_table / __jump_table /
                # altinstructions reference instruction addresses INSIDE a
                # function body using PREL32; that is metadata, not an
                # address-taken function pointer.
                if rtype != "R_AARCH64_ABS64":
                    continue
                m = re.match(r"\.text\s*\+\s*(\w+)", sym)
                if m and addr <= int(m.group(1), 16) < addr + max(size, 1):
                    return True
                if sym.split("+")[0].strip() == name:
                    return True
        return False

    def blob(self, name: str) -> bytes:
        addr, size, _bind, sec = self.funcs[name]
        if self.secnames.get(sec) != ".text":
            return b""
        base = None
        for line in run("llvm-readelf", "-SW", str(self.path)).splitlines():
            if re.search(r"\]\s+\.text\s", line):
                m = re.search(r"\.text\s+PROGBITS\s+([0-9a-f]+)", line)
                base = int(m.group(1), 16)
                break
        return self.text[addr - base: addr - base + size]

    def fops_edge(self, obj: str, slot: int) -> str | None:
        if obj not in self.objects:
            return None
        base, size, _b, sec = self.objects[obj]
        target = ".rela" + self.secnames[sec]
        for off, sym, _rtype in self.relocs.get(target, []):
            if off - base != slot:
                continue
            m = re.match(r"\.text\s*\+\s*(\w+)", sym)
            if not m:
                return sym.split("+")[0].strip()
            a = int(m.group(1), 16)
            for n, (ad, sz, _bb, si) in self.funcs.items():
                if self.secnames.get(si) == ".text" and ad <= a < ad + max(sz, 1):
                    return n
            return sym
        return None


def main() -> int:
    ck("stock oracle present and exact", STOCK.is_file() and sha256(STOCK) == STOCK_SHA)
    candidate = LIVE if LIVE.is_file() else FROZEN
    ck("a Phase-3C island ELF is available", candidate.is_file(), candidate)
    if not (STOCK.is_file() and candidate.is_file()):
        return report()

    s, c = Image(STOCK), Image(candidate)

    # --- presence, linkage and size of the nine authorized targets ---------
    for n in PRIMARY + PREREQ:
        present = n in c.funcs
        ck(f"present: {n}", present)
        if not present or n not in s.funcs:
            continue
        ck(f"stock linkage preserved: {n}", c.funcs[n][2] == s.funcs[n][2],
           f"{c.funcs[n][2]} vs {s.funcs[n][2]}")

    # --- KCFI exactness ----------------------------------------------------
    for n, want in EXPECTED_KCFI.items():
        got = c.kcfi(n) if n in c.funcs else None
        ck(f"KCFI exact: {n}", got == want,
           f"{'none' if got is None else hex(got)} want {hex(want)}")
        if n in s.funcs:
            ck(f"KCFI matches stock image: {n}", got == s.kcfi(n),
               f"{got} vs {s.kcfi(n)}")

    # --- the two internal handlers are direct-call-only in BOTH images -----
    for n in ("tee_internal_ioctl", "tee_session_internal_ioctl"):
        ck(f"direct-call-only preserved: {n}",
           (not c.address_taken(n)) and (not s.address_taken(n)),
           f"island={c.address_taken(n)} stock={s.address_taken(n)}")

    # --- every KCFI-bearing target really is address-taken in both images --
    for n in EXPECTED_KCFI:
        ck(f"address-taken classification matches stock: {n}",
           c.address_taken(n) == s.address_taken(n),
           f"island={c.address_taken(n)} stock={s.address_taken(n)}")

    # --- byte-for-byte equality that must not regress ----------------------
    for n in BYTE_EXACT:
        ok = n in c.funcs and n in s.funcs and c.blob(n) == s.blob(n)
        ck(f"byte-identical to stock: {n}", ok,
           f"{c.funcs.get(n, ('','',''))[1]} vs {s.funcs.get(n, ('','',''))[1]}")

    # --- exact stock size where achieved -----------------------------------
    for n in ("convert_compat_tee_shm_io", "convert_compat_tee_spta_inst",
              "tee_session_compat_ioctl", "tee_session_ioctl",
              "uaccess_ttbr0_enable", "uaccess_ttbr0_disable"):
        if n in c.funcs and n in s.funcs:
            ck(f"stock size reproduced: {n}", c.funcs[n][1] == s.funcs[n][1],
               f"{c.funcs[n][1]} vs {s.funcs[n][1]}")

    # --- coverage ----------------------------------------------------------
    sf, cf = set(s.funcs), set(c.funcs)
    missing = sf - cf
    island_only = cf - sf
    ck("stock function count is 122", len(sf) == 122, len(sf))
    ck("coverage is 113/122", len(sf & cf) == 113, f"{len(sf & cf)}/{len(sf)}")
    ck("missing set is exactly the excluded subsystems",
       missing == ALLOWED_MISSING, sorted(missing ^ ALLOWED_MISSING))
    ck("no island-only (fabricated) functions", not island_only, sorted(island_only))

    # --- file_operations edges --------------------------------------------
    for (obj, slot), want in FOPS_EDGES.items():
        got = c.fops_edge(obj, slot)
        ck(f"fops edge {obj}+0x{slot:02x} -> {want}", got == want, got)
        ck(f"fops edge matches stock: {obj}+0x{slot:02x}",
           got == s.fops_edge(obj, slot), f"{got} vs {s.fops_edge(obj, slot)}")
    for obj in ("tee_client_fops", "tee_admin_fops", "tee_session_fops"):
        ck(f"{obj} is 272 bytes with stock binding",
           obj in c.objects and c.objects[obj][1] == 272
           and c.objects[obj][2] == s.objects[obj][2],
           c.objects.get(obj))
    ck("compat slots are not aliased to the native handlers",
       c.fops_edge("tee_client_fops", 0x58) != c.fops_edge("tee_client_fops", 0x50)
       and c.fops_edge("tee_session_fops", 0x58) != c.fops_edge("tee_session_fops", 0x50))

    # --- the feature-flags object stock never writes -----------------------
    ck("nsdrv_feature_flags object present and 4 bytes",
       "nsdrv_feature_flags" in c.objects and c.objects["nsdrv_feature_flags"][1] == 4,
       c.objects.get("nsdrv_feature_flags"))

    # --- module hygiene ----------------------------------------------------
    modinfo = run("llvm-objcopy", "--dump-section", ".modinfo=/dev/stdout",
                  str(candidate), binary=True)
    fields = modinfo.decode("utf-8", "ignore").split("\0")
    depends = [f for f in fields if f.startswith("depends=")]
    ck("depends is empty", depends == ["depends="] or depends and depends[0] == "depends=",
       depends)
    ck("no new undefined imports vs stock", len(c.undefined) <= len(s.undefined),
       f"{len(c.undefined)} vs {len(s.undefined)}")

    # --- boundary: excluded subsystems must NOT have been implemented ------
    for n in sorted(ALLOWED_MISSING):
        ck(f"boundary honoured, still absent: {n}", n not in cf)

    # --- acceptance must remain deferred -----------------------------------
    acc = REPO / "workspace/phase4-tkcore-island/acceptance"
    ck("three-consumer acceptance still empty",
       not acc.is_dir() or not any(acc.rglob("*")))

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
        print("TKCORE_ISLAND_PHASE3C_VERIFICATION_FAILED")
        return 1
    print("TKCORE_ISLAND_PHASE3C_IOCTL_COMMAND_CLOSED")
    print("TKCORE_REPLACEMENT_READY=NO")
    print("STOCK_TKCORE_RUNTIME_DEPENDENCY=STILL_PRESENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
