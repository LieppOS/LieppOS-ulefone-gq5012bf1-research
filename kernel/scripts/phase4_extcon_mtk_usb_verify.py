#!/usr/bin/env python3
"""Fail-closed verifier for the GQ5012BF1 extcon-mtk-usb closure (Phase 13).

Every check is an assertion against evidence that must be present on disk. A
missing artifact, a changed byte, a lost symbol or an injected CRC is a FAIL --
the verifier never "passes by default" and never infers a result it could not
measure.

  ./phase4_extcon_mtk_usb_verify.py [--repo DIR] [--verbose]

Exit code 0 only when every check passes.
"""
import argparse
import hashlib
import re
import struct
import subprocess
import sys
from pathlib import Path

STOCK_SHA256 = "9e6adf23de6729f9983f680be75c8aca9eabe22aa6efcaafe7704257b37cb2bf"
STOCK_SIZE = 46864
STOCK_VERMAGIC = ("6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload "
                  "modversions aarch64")
STOCK_FUNCS = 22
STOCK_IMPORTS = 63
STOCK_EXPORTS = 0
STOCK_MODVERSIONS = 64
STOCK_KCFI = 4
LOAD_INDEX = (153, 184)
LOAD_INDEX_RECOVERY = (151, 189)

# provider edges: symbol -> CRC the stock consumer records
PROVIDER_CRCS = {
    "yft_usb_flag": 0x398E9C8B,
    "tcpc_dev_get_by_name": 0xA4A78F74,
    "register_tcp_dev_notifier": 0x796A05C1,
    "tcpm_inquire_remote_cc": 0x199E53C1,
}

# exact DT / sysfs / procfs strings that must survive in both ELFs
CONTRACT_STRINGS = [
    "mediatek,extcon-usb", "mediatek,bypss-typec-sink", "mediatek,u2",
    "vbus-supply", "usb-otg-vbus", "vbus-voltage", "vbus-current",
    "vbus-limit-current", "tcpc", "type_c_port0",
    "otg_gpio_select", "uvc_switch_gpio", "uvc_vbus_gpio",
    "mtk_typec", "smt_u2_cc_mode", "yft_extcon", "extcon_usb",
    "charger", "primary_chg",
]

# behavioural literals that encode the uSmart/YFT state machine
BEHAVIOUR_STRINGS = [
    "[%s] yft_drv ignore usb func for yft_usb_flag",
    "[%s] YFT_OTG_yft_otg_gpio set_high",
    "[%s] YFT_OTG_yft_otg_gpio set_low",
    "cur_dr(%d) new_dr(%d)",
    "online=%d, type=%d",
    "vbus turn %s",
    "source vbus = %dmv",
    "Type-C plug out",
    "Type-C SINK plug in",
    "Type-C SRC plug in",
    "cc1=%d, cc2=%d",
    "Invalid input",
    "shutdown",
]

FORBIDDEN_BUILD_TOKENS = ["KBUILD_MODPOST_WARN"]


class Verifier:
    def __init__(self, repo: Path, verbose: bool):
        self.repo = repo
        self.verbose = verbose
        self.passed = 0
        self.failed = []

    def check(self, name, ok, detail=""):
        if ok:
            self.passed += 1
            if self.verbose:
                print(f"  PASS  {name}" + (f"  [{detail}]" if detail else ""))
        else:
            self.failed.append((name, detail))
            print(f"  FAIL  {name}" + (f"  [{detail}]" if detail else ""))
        return ok

    # ---- helpers -----------------------------------------------------
    @staticmethod
    def sh(args):
        return subprocess.run(args, capture_output=True, text=True).stdout

    def sections(self, p):
        out = {}
        for line in self.sh(["llvm-readelf", "-SW", str(p)]).splitlines():
            m = re.match(r"^\s*\[\s*\d+\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+"
                         r"([0-9a-f]+)\s+([0-9a-f]+)", line)
            if m:
                out[m.group(1)] = (int(m.group(2), 16), int(m.group(3), 16))
        return out

    def funcs(self, p):
        out = {}
        for line in self.sh(["llvm-readelf", "-sW", str(p)]).splitlines():
            m = re.match(r"^\s*\d+:\s+([0-9a-f]{8,16})\s+(\d+)\s+FUNC\s+\w+\s+"
                         r"\w+\s+(\S+)\s+(.+)$", line)
            if m and m.group(3) != "UND":
                n = m.group(4).strip()
                if not n.startswith("$"):
                    out[n] = int(m.group(2))
        return out

    def imports(self, p):
        return {l.split()[-1]
                for l in self.sh(["nm", "-u", str(p)]).splitlines() if l.strip()}

    def exports(self, p):
        secs = self.sections(p)
        return sum(sz for nm, (_, sz) in secs.items()
                   if nm.startswith("__ksymtab") and "strings" not in nm)

    def versions(self, p):
        out = {}
        secs = self.sections(p)
        if "__versions" not in secs:
            return out
        off, size = secs["__versions"]
        blob = Path(p).read_bytes()[off:off + size]
        for i in range(0, size, 64):
            crc = struct.unpack("<Q", blob[i:i + 8])[0]
            nm = blob[i + 8:i + 64].split(b"\0")[0].decode("ascii", "ignore")
            if nm:
                out[nm] = crc
        return out

    def kcfi(self, p):
        return {l.split()[-1]
                for l in self.sh(["llvm-readelf", "-sW", str(p)]).splitlines()
                if "__kcfi_typeid" in l}

    def strings_of(self, p):
        """all NUL-terminated ASCII runs across .rodata* (merge-artifact safe)"""
        blob = b""
        for nm, (off, size) in self.sections(p).items():
            if nm.startswith(".rodata"):
                blob += Path(p).read_bytes()[off:off + size] + b"\0"
        return blob

    # ---- checks ------------------------------------------------------
    def run(self):
        W = self.repo / "workspace/phase4-extcon-mtk-usb"
        K = self.repo / "kernel"
        stock = W / "oracle/extcon-mtk-usb.ko"
        recon = W / "oracle/recon-final.ko"
        # repo-tracked copies are authoritative; workspace/ is gitignored and is
        # only a working area, so a clean clone must still verify.
        src = K / "phase4-extcon-mtk-usb-recon/extcon_mtk_usb.c"
        mk = K / "phase4-extcon-mtk-usb-recon/Makefile"
        vtxt_p = K / "phase4-extcon-mtk-usb-verification.txt"

        print("== artifacts ==")
        for p in (stock, recon, src, mk, vtxt_p,
                  K / "phase4-extcon-mtk-usb-stock-oracle.txt",
                  K / "phase4-extcon-mtk-usb-RED.md",
                  K / "phase4-extcon-mtk-usb-provider-abi.md",
                  K / "phase4-extcon-mtk-usb-dt-contract.md",
                  K / "phase4-extcon-mtk-usb-usmart-contract.md",
                  K / "phase4-extcon-mtk-usb-source-candidates.md",
                  K / "phase4-extcon-mtk-usb-reconstruction.md",
                  K / "phase4-extcon-mtk-usb-modversion-parity.tsv",
                  K / "phase4-extcon-mtk-usb-function-parity.tsv",
                  K / "phase4-extcon-mtk-usb-object-parity.tsv"):
            if not self.check(f"present: {p.relative_to(self.repo)}", p.exists()):
                print("\nFAIL-CLOSED: required artifact missing, aborting.")
                return False

        print("== stock oracle identity ==")
        data = stock.read_bytes()
        self.check("stock sha256", hashlib.sha256(data).hexdigest() == STOCK_SHA256)
        self.check("stock size", len(data) == STOCK_SIZE, f"{len(data)}")
        self.check("stock vermagic", STOCK_VERMAGIC.encode() in data)
        oracle_txt = (K / "phase4-extcon-mtk-usb-stock-oracle.txt").read_text()
        self.check("all stock copies proven identical",
                   "identical=YES" in oracle_txt and "exactly ONE physical stock ELF" in oracle_txt)
        self.check(f"modules.load index {LOAD_INDEX[0]}/{LOAD_INDEX[1]}",
                   f"{LOAD_INDEX[0]}/{LOAD_INDEX[1]}" in oracle_txt)
        self.check(f"recovery load index {LOAD_INDEX_RECOVERY[0]}/{LOAD_INDEX_RECOVERY[1]}",
                   f"{LOAD_INDEX_RECOVERY[0]}/{LOAD_INDEX_RECOVERY[1]}" in oracle_txt)

        print("== source provenance ==")
        srct = src.read_text()
        self.check("source cites stock sha256", STOCK_SHA256 in srct)
        self.check("source carries evidence grades",
                   "[PROVEN_EXACT]" in srct and "[RECONSTRUCTED]" in srct)
        self.check("source vermagic matches frozen oracle",
                   "6.1.115-android14-11-g945dff7bc1bf" in srct)
        self.check("TCPC gate uses the vendor macro spelling",
                   "-DCONFIG_TCPC_CLASS=1" in mk.read_text())
        cand = (K / "phase4-extcon-mtk-usb-source-candidates.md").read_text()
        self.check("donor revision pinned",
                   "957dac185efe46cbf6336b0fff9516d84c8cd78f" in cand)
        self.check("donor sha256 pinned",
                   "ad7a82001ff8f8820582ed2af2f02c7a7cdc9f50f6b2f990380b06e4c0fcc16f" in cand)

        print("== function / object parity ==")
        sf, rf = self.funcs(stock), self.funcs(recon)
        self.check("stock function count", len(sf) == STOCK_FUNCS, f"{len(sf)}")
        missing = sorted(set(sf) - set(rf))
        self.check("no stock function missing from rebuild", not missing, str(missing))

        print("== ABI parity ==")
        si, ri = self.imports(stock), self.imports(recon)
        self.check("stock import count", len(si) == STOCK_IMPORTS, f"{len(si)}")
        self.check("import set exact",
                   si == ri, f"missing={sorted(si-ri)} extra={sorted(ri-si)}")
        self.check("stock exports nothing", self.exports(stock) == STOCK_EXPORTS)
        self.check("rebuild exports nothing", self.exports(recon) == STOCK_EXPORTS)
        sv, rv = self.versions(stock), self.versions(recon)
        self.check("modversion count", len(sv) == STOCK_MODVERSIONS, f"{len(sv)}")
        self.check("modversion symbol set exact", set(sv) == set(rv))
        crc_bad = [n for n in sv if sv[n] != rv.get(n)]
        self.check("modversion CRCs all identical", not crc_bad, str(crc_bad))
        sk, rk = self.kcfi(stock), self.kcfi(recon)
        self.check("KCFI typeid count", len(sk) == STOCK_KCFI, f"{len(sk)}")
        self.check("KCFI typeid set exact", sk == rk)

        print("== provider edges ==")
        for sym, crc in PROVIDER_CRCS.items():
            self.check(f"{sym} imported", sym in si)
            self.check(f"{sym} CRC 0x{crc:08x} preserved", rv.get(sym) == crc,
                       f"got 0x{rv.get(sym, 0):08x}")
        abi = (K / "phase4-extcon-mtk-usb-provider-abi.md").read_text()
        self.check("single yft_usb_flag provider documented",
                   "single real\nprovider" in abi or "the single real" in abi)
        self.check("tcpc witness declared non-shippable",
                   "non-shippable" in abi.lower())

        print("== no CRC injection / no ELF patching ==")
        self.check("no fake-CRC or patch tooling in rebuilt tree",
                   not any((W / "rebuilt" / f).exists()
                           for f in ("patch-elf.sh", "inject-crc.py", "fixup.py")))
        vtxt = vtxt_p.read_text()
        self.check("build recorded rc=0", "rc=0" in vtxt)
        for tok in FORBIDDEN_BUILD_TOKENS:
            logs = list((W / "oracle").glob("build-*.log"))
            hit = [l.name for l in logs if tok in l.read_text(errors="ignore")]
            self.check(f"no {tok} in build logs", not hit, str(hit))
        for log in (W / "oracle").glob("build-stock-abi.log"):
            t = log.read_text(errors="ignore")
            self.check("final build: no warnings", "warning:" not in t)
            self.check("final build: no undefined symbols", "undefined!" not in t)

        print("== DT / GPIO / ABI strings ==")
        sb, rb = self.strings_of(stock), self.strings_of(recon)
        for s in CONTRACT_STRINGS:
            self.check(f"string {s!r}", s.encode() in sb and s.encode() in rb)
        self.check("bypss misspelling preserved verbatim",
                   b"mediatek,bypss-typec-sink" in rb and b"bypass-typec-sink" not in rb)

        print("== uSmart behaviour literals ==")
        for s in BEHAVIOUR_STRINGS:
            self.check(f"literal {s!r}", s.encode() in sb and s.encode() in rb)

        print("== full stock log-literal coverage ==")
        def lits(blob):
            out = set()
            for s in blob.split(b"\0"):
                t = re.sub(rb"^[^\x20-\x7e]+", b"", s).rstrip()
                if len(t) < 4 or not re.fullmatch(rb"[\x20-\x7e]+", t):
                    continue
                if b" " not in t and b":" not in t:
                    continue
                if sum(c in b"0123456789abcdefghijklmnopqrstuvwxyz"
                       b"ABCDEFGHIJKLMNOPQRSTUVWXYZ" for c in t) < 0.5 * len(t):
                    continue
                out.add(t)
            return out
        s_only = [t for t in lits(sb) if t not in rb]
        self.check("every stock log literal present in rebuild", not s_only,
                   f"{len(s_only)} missing")

        print()
        total = self.passed + len(self.failed)
        print(f"{self.passed}/{total} CHECKS PASSED")
        if self.failed:
            print("\nFAILURES:")
            for n, d in self.failed:
                print(f"  - {n} {d}")
        return not self.failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    ok = Verifier(Path(a.repo), a.verbose).run()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
