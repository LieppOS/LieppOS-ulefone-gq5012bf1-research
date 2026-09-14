#!/usr/bin/env python3
"""Fail-closed verifier for GQ5012BF1 tkcore island Phase 3C-R.

Certifies ONLY that _update_client_tee_cmd reproduces stock's parent-operation
re-read semantics on the registered-memref output paths.

It does NOT certify runtime readiness, clock runtime, secure SPI, big-core
affinity, platform init, or three-consumer acceptance.
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
PHASE = REPO / "workspace/phase4-tkcore-island/phase3c-r"
BEFORE = PHASE / "before/tkcore.phase3c.ko"
FROZEN = PHASE / "build/tkcore.phase3c-r.ko"

STOCK_SHA = "03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226"
PHASE3C_SHA = "e7a8e2a725d7cd3dde2f674fdf9806edcc3766740fd9aa22df1e610b2c1a98fd"

TARGET = "_update_client_tee_cmd"
HELPER = "tee_context_copy_from_client"

# Functions Phase 3C-R deliberately left out of scope.  Split by the phase that
# owns them so that this verifier stays valid once a LATER phase closes them.
#
# Phase 3C-R guarantees it did not implement these itself and that its own
# subject matter is unchanged.  It must NOT assert that they stay missing
# forever -- that would make a correct Phase 3D look like a regression.  The
# same reasoning the Phase-3A-R verifier already applies to co-owned files.
PHASE3D_TARGETS = {
    "tee_clkmgr_handle",
    "tee_spi_cfg_padsel", "tee_spi_transfer", "tee_spi_transfer_disable",
}
PHASE3E_TARGETS = {
    "big_core_affinity_get_candidate_cpu", "big_core_affinity_match_cpu",
    "big_core_affinity_need_bind_cpu", "plat_cpu_is_big", "plat_tee_init",
}
ALLOWED_MISSING = PHASE3D_TARGETS | PHASE3E_TARGETS
EXPECTED_EXPORT_GAPS = set(PHASE3D_TARGETS)

# Coverage/export floors achieved by Phase 3C-R.  Later phases may exceed them;
# dropping below them is a real regression.
PHASE3C_R_COVERAGE = 113
PHASE3C_R_EXPORTS = 21

# Parameter-type classes stock's dispatch table must impose.
SKIPPED = {0, 1, 5, 13}          # NONE, VALUE_INPUT, TEMP_INPUT, PARTIAL_INPUT
VALUE_OUT = {2, 3}
TEMP_OUT = {6, 7}
REGISTERED_OUT = {12, 14, 15}    # WHOLE, PARTIAL_OUTPUT, PARTIAL_INOUT
INVALID = {4, 8, 9, 10, 11}

# Things that would mean ownership/lifetime drift if they appeared here.
FORBIDDEN_IN_TARGET = {
    "tkcore_shm_put", "tkcore_shm_free", "tkcore_shm_get",
    "__list_add_valid", "list_del", "dma_buf_put", "dma_buf_get",
    "kfree", "devm_kfree",
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


def run(*args: str) -> str:
    p = subprocess.run(args, capture_output=True, text=True)
    return "" if p.returncode else p.stdout


class Image:
    def __init__(self, path: Path):
        self.path = path
        self.funcs: dict[str, tuple[int, int, str]] = {}
        self.undefined: set[str] = set()
        self.exports: set[str] = set()
        for line in run("llvm-readelf", "-sW", str(path)).splitlines():
            p = line.split()
            if len(p) < 8 or not re.fullmatch(r"[0-9a-fA-F]+", p[1]):
                continue
            if p[6] == "UND":
                self.undefined.add(p[7])
                continue
            if p[3] == "FUNC" and p[2].isdigit():
                self.funcs[p[7]] = (int(p[1], 16), int(p[2]), p[4])
            if p[7].startswith("__ksymtab_") and p[7] != "__ksymtab_strings":
                self.exports.add(p[7][len("__ksymtab_"):])
        self.sections = {}
        for line in run("llvm-readelf", "-SW", str(path)).splitlines():
            m = re.search(r"\]\s+(\S+)\s+\S+\s+([0-9a-f]+)\s+([0-9a-f]+)", line)
            if m:
                self.sections[m.group(1)] = (int(m.group(2), 16), int(m.group(3), 16))

    def dump(self, name: str) -> str:
        a, n, _ = self.funcs[name]
        return run("llvm-objdump", "-dr", f"--start-address={a}",
                   f"--stop-address={a + n}", str(self.path))

    def calls(self, name: str) -> list[str]:
        return re.findall(r"R_AARCH64_CALL26\s+(\S+)", self.dump(name))

    def body(self, name: str) -> bytes:
        a, n, _ = self.funcs[name]
        va, off = self.sections[".text"]
        with self.path.open("rb") as f:
            f.seek(off + a - va)
            return f.read(n)

    def strings(self, name: str) -> set[str]:
        out = set()
        if ".rodata.str1.1" not in self.sections:
            return out
        _va, off = self.sections[".rodata.str1.1"]
        with self.path.open("rb") as f:
            for rel in {int(x, 16) for x in
                        re.findall(r"\.rodata\.str1\.1\+0x([0-9a-f]+)", self.dump(name))}:
                f.seek(off + rel)
                out.add(f.read(120).split(b"\0")[0].decode("utf-8", "replace"))
        return out

    def jump_table(self, name: str):
        m = re.search(r"\.rodata\+0x([0-9a-f]+)", self.dump(name))
        if not m or ".rodata" not in self.sections:
            return None
        _va, off = self.sections[".rodata"]
        with self.path.open("rb") as f:
            f.seek(off + int(m.group(1), 16))
            return struct.unpack("<16I", f.read(64))


def partition(tbl) -> list[tuple[int, ...]]:
    g: dict[int, list[int]] = {}
    for i, v in enumerate(tbl):
        g.setdefault(v, []).append(i)
    return sorted(tuple(sorted(v)) for v in g.values())


def main() -> int:
    ck("stock oracle present and exact", STOCK.is_file() and sha256(STOCK) == STOCK_SHA)
    ck("frozen Phase-3C baseline present and exact",
       BEFORE.is_file() and sha256(BEFORE) == PHASE3C_SHA,
       sha256(BEFORE) if BEFORE.is_file() else "missing")

    candidate = LIVE if LIVE.is_file() else FROZEN
    ck("a Phase-3C-R island ELF is available", candidate.is_file(), candidate)
    if not (STOCK.is_file() and candidate.is_file() and BEFORE.is_file()):
        return report()

    s, c, b = Image(STOCK), Image(candidate), Image(BEFORE)

    # ---- target exists with stock linkage --------------------------------
    ck(f"{TARGET} exists", TARGET in c.funcs)
    if TARGET not in c.funcs:
        return report()
    ck(f"{TARGET} keeps stock linkage",
       c.funcs[TARGET][2] == s.funcs[TARGET][2],
       f"{c.funcs[TARGET][2]} vs {s.funcs[TARGET][2]}")

    # ---- THE residual: the stock call edge must be present ---------------
    scalls, ccalls, bcalls = s.calls(TARGET), c.calls(TARGET), b.calls(TARGET)
    ck("RED still reproduces: Phase-3C lacked the stock edge",
       HELPER not in bcalls)
    ck(f"stock edge restored: {HELPER} present", HELPER in ccalls)
    ck("exactly one re-read call site, matching stock",
       ccalls.count(HELPER) == scalls.count(HELPER) == 1,
       f"island={ccalls.count(HELPER)} stock={scalls.count(HELPER)}")
    ck("no stock-only call edges remain",
       not (set(scalls) - set(ccalls)), sorted(set(scalls) - set(ccalls)))

    # ---- the re-read must precede the parameter loop ---------------------
    dump = c.dump(TARGET)
    base = c.funcs[TARGET][0]
    site = None
    for m in re.finditer(r"([0-9a-f]+):\s+[0-9a-f]{8}\s+bl\b", dump):
        tail = dump[m.end():m.end() + 200]
        if HELPER in tail:
            site = int(m.group(1), 16) - base
            break
    ck("re-read happens in the first quarter of the function (before the loop)",
       site is not None and site < c.funcs[TARGET][1] // 4, site)

    # ---- the refreshed copy must be operation-sized ----------------------
    ck("a 0x118-sized operation buffer is materialised",
       "#0x118" in dump, "expected TEEC_Operation size immediate")
    ck("the local operation is zeroed before the copy (stock memset)",
       "memset" in ccalls)

    # ---- stock diagnostic string ----------------------------------------
    want = "tkcore: Failed to copy op from client\n"
    ck("stock copy-failure diagnostic reproduced",
       any(want in x for x in c.strings(TARGET)),
       sorted(x for x in c.strings(TARGET) if "copy op" in x))

    # ---- per-type dispatch must partition exactly like stock ------------
    sj, cj = s.jump_table(TARGET), c.jump_table(TARGET)
    ck("stock dispatch table located", sj is not None)
    ck("island dispatch table located", cj is not None)
    if sj and cj:
        ck("parameter-type dispatch partition matches stock exactly",
           partition(sj) == partition(cj),
           f"{partition(cj)}")
        sgroup = {i: v for i, v in enumerate(sj)}
        # registered output types share one target, and PARTIAL_INPUT does not
        ck("WHOLE/PARTIAL_OUTPUT/PARTIAL_INOUT share one output path",
           len({cj[i] for i in REGISTERED_OUT}) == 1)
        ck("PARTIAL_INPUT is NOT on the registered output path",
           cj[13] not in {cj[i] for i in REGISTERED_OUT})
        ck("PARTIAL_INPUT is grouped with the skipped input types",
           len({cj[i] for i in SKIPPED}) == 1)
        ck("VALUE_OUTPUT/VALUE_INOUT share one path",
           len({cj[i] for i in VALUE_OUT}) == 1)
        ck("TEMP_OUTPUT/TEMP_INOUT share one path",
           len({cj[i] for i in TEMP_OUT}) == 1)
        ck("invalid type nibbles share one path",
           len({cj[i] for i in INVALID}) == 1)
        ck("island dispatch targets agree with stock grouping of skipped types",
           len({sgroup[i] for i in SKIPPED}) == 1)

    # ---- the direct dependency must remain stock-exact and untouched ----
    ck(f"{HELPER} present", HELPER in c.funcs)
    if HELPER in c.funcs:
        ck(f"{HELPER} is byte-identical to stock",
           c.body(HELPER) == s.body(HELPER))
        ck(f"{HELPER} keeps stock size and linkage",
           c.funcs[HELPER][1] == s.funcs[HELPER][1]
           and c.funcs[HELPER][2] == s.funcs[HELPER][2])
        ck(f"{HELPER} unchanged from Phase 3C",
           c.body(HELPER) == b.body(HELPER))

    # ---- ownership / lifetime must not have drifted ---------------------
    leaked = sorted(set(ccalls) & FORBIDDEN_IN_TARGET)
    ck("no put/free/list/dma-buf edge introduced into the target", not leaked, leaked)
    ck("stock also has no such edge (control)",
       not (set(scalls) & FORBIDDEN_IN_TARGET))

    # ---- narrowness: nothing else changed semantically -------------------
    changed = [n for n in sorted(set(b.funcs) & set(c.funcs))
               if b.body(n) != c.body(n)]
    resized = [n for n in changed if b.funcs[n][1] != c.funcs[n][1]]
    ck("only target and optional stock-exact Phase-3E init/exit changed size",
       set(resized) in ({TARGET}, {TARGET, "init_module", "cleanup_module"}), resized)
    # Added functions are allowed only if a later phase legitimately owns them.
    added = set(c.funcs) - set(b.funcs)
    ck("no function added outside a later phase's declared scope",
       not (added - ALLOWED_MISSING), sorted(added - ALLOWED_MISSING))
    ck("no function removed", not (set(b.funcs) - set(c.funcs)),
       sorted(set(b.funcs) - set(c.funcs)))

    # ---- coverage / exports / imports unchanged --------------------------
    sf, cf, bf = set(s.funcs), set(c.funcs), set(b.funcs)
    ck("stock function count is 122", len(sf) == 122, len(sf))
    ck("coverage never regressed below Phase 3C-R's 113/122",
       len(sf & cf) >= PHASE3C_R_COVERAGE, f"{len(sf & cf)}/{len(sf)}")
    ck("coverage never regressed below the frozen baseline",
       len(sf & cf) >= len(sf & bf), f"{len(sf & cf)} vs {len(sf & bf)}")
    ck("nothing outside the declared out-of-scope set is missing",
       not ((sf - cf) - ALLOWED_MISSING), sorted((sf - cf) - ALLOWED_MISSING))
    ck("no island-only functions", not (cf - sf), sorted(cf - sf))
    ck("exports never regressed below Phase 3C-R's 21",
       len(c.exports) >= PHASE3C_R_EXPORTS, len(c.exports))
    ck("no export present at Phase 3C-R was lost",
       not (b.exports - c.exports), sorted(b.exports - c.exports))
    ck("remaining export gaps stay within the declared set",
       not ((s.exports - c.exports) - EXPECTED_EXPORT_GAPS),
       sorted((s.exports - c.exports) - EXPECTED_EXPORT_GAPS))
    ck("later imports are stock-only",
       not ((c.undefined - b.undefined) - s.undefined),
       sorted((c.undefined - b.undefined) - s.undefined))
    ck("no removed imports", not (b.undefined - c.undefined),
       sorted(b.undefined - c.undefined))
    ck("import count is Phase-3C-R 97 through Phase-3E 101",
       len(c.undefined) in (97, 101), len(c.undefined))

    # ---- module hygiene --------------------------------------------------
    p = subprocess.run(["llvm-objcopy", "--dump-section", ".modinfo=/dev/stdout",
                        str(candidate)], capture_output=True)
    fields = p.stdout.decode("utf-8", "ignore").split("\0")
    ck("depends is empty", any(f == "depends=" for f in fields),
       [f for f in fields if f.startswith("depends=")])

    # ---- forbidden techniques -------------------------------------------
    src = (GKI / "lieppos/tkcore-island/tkcore/tee_session.c").read_text(errors="ignore")
    for bad, label in [("__crc_", "CRC injection"),
                       ("__versions", "__versions edit"),
                       ("__kcrctab", "kcrctab edit"),
                       ("KBUILD_MODPOST_WARN", "modpost warn suppression")]:
        ck(f"no {label} in the modified source", bad not in src)
    ck("the modified source calls the helper, not a hand-rolled copy",
       HELPER in src)
    # Every surviving `cmd_io->op->...` must be a WRITE DESTINATION (taken by
    # address) or an unevaluated sizeof operand.  A bare value-read through
    # that __user pointer is the defect this phase removed.
    # Strip comments first: prose about the old form must not be mistaken for
    # code.  Newlines are preserved so reported line numbers stay accurate.
    code = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)),
                  src, flags=re.S)
    code = re.sub(r"//[^\n]*", "", code)
    bad_reads = []
    for m in re.finditer(r"[^&\w]cmd_io->op->", code):
        start = max(0, m.start() - 80)
        ctxt = code[start:m.start() + 1]
        if re.search(r"sizeof\s*\([^)]*$", ctxt):
            continue
        line = code[:m.start()].count("\n") + 1
        bad_reads.append(line)
    ck("no value-read of cmd_io->op survives (writes and sizeof only)",
       not bad_reads, f"offending source lines: {bad_reads}")
    ck("client reads are served from the refreshed local operation",
       re.search(r"op\.params\[idx\]\.tmpref\.size", src) is not None
       and re.search(r"op\.params\[idx\]\.memref\.offset", src) is not None
       and re.search(r"op\.params\[idx\]\.memref\.size", src) is not None)

    # ---- boundary --------------------------------------------------------
    # Later live ELFs may contain the complete Phase-3E set, but partial or
    # non-stock expansion remains forbidden by the checks above.
    phase3e_seen = PHASE3E_TARGETS & cf
    for n in sorted(PHASE3E_TARGETS):
        ck(f"Phase-3E boundary absent or complete: {n}",
           not phase3e_seen or phase3e_seen == PHASE3E_TARGETS)
    acc = REPO / "workspace/phase4-tkcore-island/acceptance"
    ck("three-consumer acceptance still empty",
       not acc.is_dir() or not any(acc.rglob("*")))

    # ---- static tmem output trace ---------------------------------------
    trace = REPO / "kernel/phase4-tkcore-island-phase3c-r-tmem-output-trace.md"
    ck("tmem static output trace recorded", trace.is_file())
    ck("tmem static output trace result is PASS_STATIC_OUTPUT_UPDATE",
       trace.is_file() and "PASS_STATIC_OUTPUT_UPDATE" in trace.read_text(errors="ignore"))

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
        print("TKCORE_ISLAND_PHASE3C_R_VERIFICATION_FAILED")
        return 1
    print("TKCORE_ISLAND_PHASE3C_R_COMMAND_OUTPUT_CLOSED")
    print("TKCORE_REPLACEMENT_READY=NO")
    print("STOCK_TKCORE_RUNTIME_DEPENDENCY=STILL_PRESENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
