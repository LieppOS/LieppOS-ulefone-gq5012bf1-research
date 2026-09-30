#!/usr/bin/env python3
"""Binary-differential harness for the Awinic AW3651x LED family modules.

Answers, from the frozen stock `.ko` files only (no source, no device):

  * do two modules expose the same function set, and which functions differ?
  * are the differing functions *semantically* different, or do they only differ
    in operands that reference the module-name string or its `.rodata` offsets?
  * are the writable data tables byte-identical?
  * which call targets does one module have that the other lacks, and inside
    which function does each extra call sit?

Findings derived with this tool: ../findings/aw36518-family-structural-delta.md

Usage:
    tools/ko-family-delta.py                  # aw36518 vs aw36518_v2 vs aw36515
    tools/ko-family-delta.py --verbose        # show the operand-level diff
    tools/ko-family-delta.py --json           # machine-readable output
    tools/ko-family-delta.py --self-test      # golden regression check
"""
from __future__ import annotations

import argparse
import difflib
import glob
from collections import Counter
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEFAULT_MODULES = os.path.join(
    ROOT, "workspace", "gq5012bf1", "stock", "partitions",
    "vendor_dlkm", "lib", "modules",
)
sys.path.insert(0, os.path.join(HERE, os.pardir, "re", "tools"))

FUNC_HDR = re.compile(r"<([^+<>]+)>:$")
INSN = re.compile(r"\s+[0-9a-f]+:\s+(.*)$")
SYMTAB = re.compile(r"\s*\d+:\s+([0-9a-f]+)\s+(\d+)\s+\S+\s+\w+\s+\w+\s+\d+\s+(\S+)")
RELA = re.compile(r"^\s*([0-9a-f]{8,16}):?\s+[0-9a-f]+\s+(\S+)\s+[0-9a-f]+\s+(\S+)")
SHT_NOBITS = 8
TIERS = (0, 1, 2, 3)
TIER_NAMES = {0: "verbatim", 1: "modulo_module_name", 2: "modulo_anchor_offsets",
               3: "modulo_immediates"}
# a "real" string: starts with a letter, then mostly text-ish characters. Filters
# out $x/$d mapping symbols and hash fragments in the string pools.
WORD = re.compile(r"[A-Za-z][A-Za-z0-9_ %()\[],.:/=+-]{5,}")


def objdump() -> str:
    """GNU objdump in this environment has no aarch64 target; prefer LLVM's."""
    found = shutil.which("llvm-objdump")
    if found:
        return found
    for pat in ("/usr/lib/llvm/*/bin/llvm-objdump", "/usr/bin/llvm-objdump-*"):
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    raise SystemExit("llvm-objdump not found (needed for aarch64 disassembly)")


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def stem(name: str) -> str:
    """Module-independent function key: aw36518_v2_probe -> probe."""
    for pre in ("aw36518_v2_", "aw36518_", "aw36515_"):
        if name.startswith(pre):
            return name[len(pre):]
    return name


class Module:
    def __init__(self, path: str, od: str):
        self.path = path
        self.name = os.path.basename(path)[:-3]
        self.raw = open(path, "rb").read()
        self._sections()
        self._symbols()
        self._funcs(od)
        self._calls(od)
        self._imports()
        self._strings()
        self._modinfo()

    # ---- ELF ------------------------------------------------------------
    def _sections(self) -> None:
        from elfpeek import ELF  # local helper in ../re/tools/elfpeek.py
        e = ELF(self.path)
        self.sections: dict[str, bytes] = {}
        for sh in e.secs:  # [name_off, type, addr, off, size, link, name]
            if sh[1] != SHT_NOBITS and sh[4]:
                self.sections[sh[6]] = e.d[sh[3]: sh[3] + sh[4]]

    def _symbols(self) -> None:
        """Symbol sizes, keyed by `canon()` name (max size wins on collisions)."""
        self.sizes: dict[str, int] = {}
        for line in run(["readelf", "-sW", self.path]).splitlines():
            m = SYMTAB.match(line)
            if m:
                k = self.canon(m.group(3))
                self.sizes[k] = max(self.sizes.get(k, 0), int(m.group(2)))

    def canon(self, name: str) -> str:
        """Module-independent key: every occurrence of the module name (either
        case, as it appears in symbols vs. in the Kbuild description string)
        becomes '@'."""
        out = name.replace(self.name, "@").replace(self.name.upper(), "@")
        return out[1:].lstrip("_") if out.startswith("@") else out

    def _funcs(self, od: str) -> None:
        """Per-function instruction streams, keyed by `canon()` symbol name."""
        self.funcs: dict[str, list[str]] = {}
        cur = None
        for line in run([od, "-d", "--no-show-raw-insn", self.path]).splitlines():
            head = FUNC_HDR.search(line.rstrip())
            if head and re.match(r"^[0-9a-f]{4,}", line):
                key = self.canon(head.group(1))
                cur = None if key.startswith("$") else key
                if cur is not None:
                    self.funcs.setdefault(cur, [])
                continue
            if cur is None:
                continue
            m = INSN.match(line)
            if m:
                self.funcs[cur].append(m.group(1).strip())

    def _calls(self, od: str) -> None:
        """Call targets per containing function, from the RELA entries."""
        self.calls: dict[str, list[str]] = {}
        self.call_total = 0
        sym = {}
        for line in run(["readelf", "-sW", self.path]).splitlines():
            m = SYMTAB.match(line)
            if m:
                sym[m.group(3)] = (int(m.group(1), 16), int(m.group(2)))
        for line in run(["readelf", "-rW", self.path]).splitlines():
            m = RELA.match(line)
            if not m or m.group(2) != "R_AARCH64_CALL26":
                continue
            self.call_total += 1
            off = int(m.group(1), 16)
            # the smallest symbol whose range contains the call site owns it
            owners = [(s, n) for n, (v, s) in sym.items()
                      if s and v <= off < v + s and not n.startswith(("$", "____"))]
            owner = self.canon(min(owners)[1]) if owners else "?"
            # An unlinked module object has no addend for a local call, so
            # readelf prints no callee name at all. Keep those edges, but label
            # them: they corroborate *that* a call exists, never *which* callee,
            # so they must never be counted with the symbol-backed ones.
            self.calls.setdefault(owner, []).append(
                m.group(3) or f"UNRESOLVED@{off:#x}")

    def _imports(self) -> None:
        self.imports = {l.split()[-1].split(".")[0]
                        for l in run(["nm", "-u", self.path]).splitlines() if l.strip()}

    def _strings(self) -> None:
        raw = [s for s in run(["strings", "-n", "4", self.path]).splitlines() if s.strip()]
        self.strings = set(raw)
        self.strings_bytes = sum(len(s) + 1 for s in raw)
        # keep human-readable strings only: the rest is mapping symbols ($x/$d),
        # build-id/modversion hash fragments and .rela padding, which differ for
        # reasons that say nothing about the driver
        self.strings_multi = Counter(self.canon(s) for s in raw if WORD.fullmatch(s))

    def _modinfo(self) -> None:
        self.modinfo = {}
        for line in run(["modinfo", self.path]).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                self.modinfo[k.strip()] = v.strip()

    # ---- comparison helpers ---------------------------------------------
    def sig(self, ins: str, mode: int) -> str:
        """Instruction signature.

        mode 0: verbatim text (identical => byte-exact same code)
        mode 1: + module name canonicalised (identical => the only difference is
                the embedded module-name string)
        mode 2: + every `<sym+off>` anchor offset canonicalised. In an unlinked
                module object objdump/llvm-objdump annotate data references with
                the *nearest preceding function symbol*, so one function growing
                shifts those anchors in every caller without changing a single
                instruction. Identical at this tier => same code, shifted pool.
        mode 3: + every hex immediate masked (identical => same *structure*, only
                constant operands differ)
        """
        s = ins if mode < 1 else self.canon(ins)
        if mode >= 1:
            s = re.sub(r"0x[0-9a-f]+(?=\s*<)", "TGT", s)
        s = re.sub(r"\s*//\s*=\s*\d+$", "", s)  # llvm re-prints the immediate in decimal
        if mode >= 2:
            # data-page references: the annotation is only the nearest preceding
            # symbol, so mask it entirely; branch targets keep their offset, which
            # is real control-flow information
            if s.split()[0] in ("adrp", "add", "ldr", "mov"):
                s = re.sub(r"<[^>]*>", "<DATA>", s)
            else:
                s = re.sub(r"<([^+>]+)\+0x[0-9a-f]+>", r"<\1+OFF>", s)
        if mode >= 3:
            s = re.sub(r"#0x[0-9a-f]+", "#IMM", s)
        return re.sub(r"\s+", " ", s).strip()


def name_explained(a: bytes, b: bytes, la: str, lb: str) -> dict:
    """Can every differing byte between two equal-length blobs be explained by
    one module's name occurring where the other's does not?"""
    diffs = [(i, x, y) for i, (x, y) in enumerate(zip(a, b)) if x != y]
    hit_a = [i for i in range(len(a) - len(la) + 1) if a[i:i + len(la)] == la.encode()]
    hit_b = [i for i in range(len(b) - len(lb) + 1) if b[i:i + len(lb)] == lb.encode()]
    covered = all(any(i >= h and i < h + max(len(la), len(lb)) for h in hit_b)
                  for i, _, _ in diffs) if diffs else True
    return {"diff_bytes": len(diffs), "length": len(a),
            "name_offsets_a": hit_a[:8], "name_offsets_b": hit_b[:8],
            "all_diffs_inside_name_field": covered}


def compare(x: Module, y: Module, verbose: bool, args_all_sections: bool = False) -> dict:
    shared = sorted(set(x.funcs) & set(y.funcs))
    tier = {}
    for k in shared:
        for mode in TIERS:
            if [x.sig(i, mode) for i in x.funcs[k]] == [y.sig(i, mode) for i in y.funcs[k]]:
                tier[k] = mode
                break
    by_tier = {m: sorted(k for k in shared if tier.get(k) == m) for m in TIERS}
    sem = sorted(k for k in shared if k not in tier)
    out = {
        "pair": f"{x.name} vs {y.name}",
        "functions": {"shared": len(shared),
                      "identical_verbatim": len(by_tier[0]),
                      "identical_modulo_module_name": len(by_tier[1]),
                      "identical_modulo_anchor_offsets": len(by_tier[2]),
                      "identical_modulo_immediates": len(by_tier[3]),
                      "tiers": {TIER_NAMES[m]: by_tier[m] for m in TIERS},
                      "structurally_differing": sem},
        "only_in_first": sorted(set(x.funcs) - set(y.funcs)),
        "only_in_second": sorted(set(y.funcs) - set(x.funcs)),
        "size_diffs": {k: [x.sizes.get(k), y.sizes.get(k)]
                       for k in sorted(shared)
                       if x.sizes.get(k) != y.sizes.get(k)},
        "imports": {"first": len(x.imports), "second": len(y.imports),
                    "first_only": sorted(x.imports - y.imports),
                    "second_only": sorted(y.imports - x.imports)},
        "strings": {"first": len(x.strings), "second": len(y.strings),
                    "bytes": [x.strings_bytes, y.strings_bytes],
                    "first_only": sorted((x.strings_multi - y.strings_multi).elements()),
                    "second_only": sorted((y.strings_multi - x.strings_multi).elements())},
        "sections": {}, "extra_calls": {}, "diff_details": {},
    }
    skip = (".rela", "__ksymtab", "__versions", "__mcount", "__crc", ".note", ".strtab",
            ".symtab", ".gnu.attributes", ".init.text", ".exit.text")
    for sec in sorted(set(x.sections) & set(y.sections)):
        if not args_all_sections and (sec.startswith(skip) or len(x.sections[sec]) > 8192):
            continue
        a, b = x.sections[sec], y.sections[sec]
        if len(a) == len(b):
            out["sections"][sec] = name_explained(a, b, x.name, y.name)
        else:
            out["sections"][sec] = {"lengths": [len(a), len(b)]}
    code = set(x.funcs) | set(y.funcs)
    for fn in sorted(set(x.calls) | set(y.calls)):
        c1, c2 = sorted(x.calls.get(fn, [])), sorted(y.calls.get(fn, []))
        if c1 == c2:
            continue
        f_only, s_only = sorted(set(c1) - set(c2)), sorted(set(c2) - set(c1))
        loose = lambda xs: [x for x in xs if x.startswith("UNRESOLVED")]
        # first_only/second_only are the STRICT tier: every edge names a callee
        # the symbol table corroborates. unresolved_* is the lenient remainder.
        entry = {"first_only": [x for x in f_only if not x.startswith("UNRESOLVED")],
                 "second_only": [x for x in s_only if not x.startswith("UNRESOLVED")],
                 "unresolved_first_only": loose(f_only),
                 "unresolved_second_only": loose(s_only),
                 "counts": [len(c1), len(c2)]}
        if fn in code:
            out["extra_calls"][fn] = entry
        else:
            out.setdefault("noncode_calls", {})[fn] = entry
    if verbose:
        for fn in sem + sorted(out["size_diffs"]):
            a = [i for i in x.funcs.get(fn, [])]
            b = [i for i in y.funcs.get(fn, [])]
            blocks = []
            for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
                if tag == "equal":
                    continue
                blocks.append({"op": tag,
                               "first": [x.sig(i, 3) for i in a[i1:i2]],
                               "second": [y.sig(i, 3) for i in b[j1:j2]]})
            out["diff_details"][fn] = {"insns": [len(a), len(b)], "blocks": blocks[:12]}
    return out


def self_test(mods: list[Module]) -> list[str]:
    """Golden invariants of the frozen stock module set."""
    fails = []

    def check(cond, what):
        if not cond:
            fails.append(what)

    by = {m.name: m for m in mods}
    if {"aw36518", "aw36518_v2"} <= set(by):
        a, b = by["aw36518"], by["aw36518_v2"]
        check(set(a.funcs) == set(b.funcs), "function sets must match")
        check(not (a.imports ^ b.imports) or (a.imports ^ b.imports) == {"is_yft_cts_board"},
              "import delta must be exactly is_yft_cts_board")
        check(a.sections[".data"] == b.sections[".data"], ".data must be byte-identical")
        d = name_explained(a.sections[".rodata"], b.sections[".rodata"], a.name, b.name)
        check(d["diff_bytes"] and d["all_diffs_inside_name_field"],
              ".rodata diffs must be explained by the module-name field")
        d = compare(a, b, False)
        check(d["extra_calls"].get("parse_dt", {}).get("first_only") == ["is_yft_cts_board"],
              "parse_dt must own the extra is_yft_cts_board call")
        check(all("yft" in s for s in d["strings"]["first_only"]) and
              all("depends=" in s for s in d["strings"]["second_only"]),
              "string pool delta must be limited to the yft vendor hook")
        check(a.modinfo.get("depends", "").startswith("yft_devinfo")
              and "yft_devinfo" not in b.modinfo.get("depends", ""),
              "only aw36518.ko may depend on yft_devinfo")
        check(d["functions"]["structurally_differing"] == ["parse_dt"],
              "parse_dt must be the only structurally differing function")
    if {"aw36518", "aw36515"} <= set(by):
        a, c = by["aw36518"], by["aw36515"]
        check({"led1_get_ctrl", "led1_set_ctrl"} <= set(c.funcs),
              "aw36515 must expose the led1 channel functions")
        check(a.sections[".data"] == c.sections[".data"],
              ".data must be byte-identical family-wide")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser(description="AW3651x module family differ")
    ap.add_argument("modules", nargs="*", help=".ko paths (default: the stock trio)")
    ap.add_argument("--modules-dir", default=DEFAULT_MODULES)
    ap.add_argument("--base", help="base module stem (default: first)")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all-sections", action="store_true",
                    help="also byte-compare symbol/reloc/init sections")
    ap.add_argument("--self-test", action="store_true",
                    help="assert the invariants quoted in the findings doc")
    args = ap.parse_args()

    od = objdump()
    paths = args.modules or [os.path.join(args.modules_dir, n)
                            for n in ("aw36518.ko", "aw36518_v2.ko", "aw36515.ko")]
    mods = [Module(p, od) for p in paths]

    if args.self_test:
        fails = self_test(mods)
        for m in mods:
            print(f"{m.name}: {len(m.funcs)} symbols, {len(m.imports)} imports, "
                  f"{m.call_total} CALL26")
        print("SELF_TEST:", "PASS" if not fails else "FAIL " + "; ".join(fails))
        return 0 if not fails else 1

    base = mods[0] if not args.base else next(m for m in mods if stem(m.name) == stem(args.base))
    report = [compare(base, other, args.verbose, args.all_sections)
              for other in mods if other is not base]
    for r in report:
        f = r["functions"]
        print(f"\n=== {r['pair']} ===")
        print(f"  functions: shared={f['shared']} verbatim-identical="
              f"{f['identical_verbatim']} +name={f['identical_modulo_module_name']} "
              f"+anchors={f['identical_modulo_anchor_offsets']} "
              f"+immediates={f['identical_modulo_immediates']}")
        print(f"  structurally differing: {', '.join(f['structurally_differing']) or '-'}")
        print(f"  only in first: {r['only_in_first'] or '-'}")
        print(f"  only in second: {r['only_in_second'] or '-'}")
        print(f"  size diffs: " + (", ".join(f"{k} {a}->{b}" for k, (a, b) in r["size_diffs"].items()) or "-"))
        for label, keys in f["tiers"].items():
            if label != "verbatim" and keys:
                print(f"    identical {label}: {keys}")
        print(f"  imports: {r['imports']['first']} vs {r['imports']['second']}; "
              f"first-only={r['imports']['first_only']} second-only={r['imports']['second_only']}")
        s = r["strings"]
        print(f"  strings: {s['first']}/{s['second']} ({s['bytes'][0]}/{s['bytes'][1]} B) "
              f"canonicalised diff first-only={s['first_only']} second-only={s['second_only']}")
        strict = sum(len(d["first_only"]) + len(d["second_only"])
                     for d in r["extra_calls"].values())
        loose = sum(len(d["unresolved_first_only"]) + len(d["unresolved_second_only"])
                    for d in r["extra_calls"].values())
        print(f"  evidence: strict={strict} symbol-corroborated, "
              f"strict+unresolved={strict + loose} total differing call edges")
        for sec, d in r["sections"].items():
            if "lengths" in d:
                print(f"  {sec}: {d['lengths'][0]}B vs {d['lengths'][1]}B")
            else:
                print(f"  {sec}: {d['length']}B, {d['diff_bytes']} differing bytes"
                      + (", all inside the module-name field"
                         if d["diff_bytes"] and d["all_diffs_inside_name_field"] else ""))
        for fn, d in r["extra_calls"].items():
            print(f"  calls {fn}: {d['counts']} first-only={d['first_only']} "
                  f"second-only={d['second_only']}")
            for k, tag in (("unresolved_first_only", "first"),
                           ("unresolved_second_only", "second")):
                if d[k]:
                    print(f"    {tag}-only unresolved: {d[k]}")
        if args.verbose:
            for fn, d in r.get("noncode_calls", {}).items():
                print(f"    (data) {fn}: {d['counts']} first-only={d['first_only']} "
                      f"second-only={d['second_only']}")
        for fn, d in r["diff_details"].items():
            print(f"  --- {fn} ({d['insns'][0]} vs {d['insns'][1]} insns)")
            for b in d["blocks"]:
                for i in b["first"]:
                    print(f"      - {i}")
                for i in b["second"]:
                    print(f"      + {i}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
