#!/usr/bin/env python3
"""Fail-closed static verifier for the GQ5012BF1 WL2868 reconstruction."""
from __future__ import annotations

import collections
import csv
import hashlib
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "workspace/phase4-custom-ldo-wl2868"
STOCK = EVIDENCE / "stock-custom-ldo-wl2868.ko"
RECON = EVIDENCE / "recon-closure-custom_ldo_wl2868.ko"
STOCK_CONSUMER = EVIDENCE / "stock-custom-ldo.ko"
RECON_CONSUMER = EVIDENCE / "recon-closure-custom_ldo.ko"
SOURCE = ROOT / "kernel/phase4-custom-ldo-wl2868-reconstructed-source.c"
BUILD_LOG = EVIDENCE / "recon-build-closure.log"
CONSUMER_BUILD_LOG = EVIDENCE / "custom-ldo-downstream-closure-build.log"

EXPECTED_SHA256 = "dab36e3d2593546d72b4fa7257b4a303c65c0ad4c507bbd1fbb50e1578111d48"
EXPECTED_FUNCTIONS = {
    "cleanup_module": (".exit.text", 0x4, 36, 0xA540670C),
    "init_module": (".init.text", 0x4, 132, 0x36B1C5A6),
    "wl2864c_vin2_power": (".text", 0x4, 92, 0x00050794),
    "wl2864c_ldo_vout": (".text", 0x64, 576, 0x56E5B5A5),
    "wl2864c_ldo_en": (".text", 0x2A8, 572, 0x56E5B5A5),
    "wl2868c_ldo_vout": (".text", 0x4E8, 576, 0x56E5B5A5),
    "wl2868c_ldo_en": (".text", 0x72C, 568, 0x56E5B5A5),
    "will_ldo_vout": (".text", 0x968, 136, 0x56E5B5A5),
    "will_ldo_en": (".text", 0x9F4, 72, 0x56E5B5A5),
    "wl2864c_llseek": (".text", 0xA40, 84, 0xE61887DE),
    "wl2864c_probe": (".text", 0xA98, 660, 0x5EF138AA),
    "wl2864c_remove": (".text", 0xD30, 64, 0x8EFFDD6D),
    "wl2864c_read": (".text", 0xD74, 940, 0xE866E2F4),
    "wl2864c_write": (".text", 0x1124, 600, 0x9A660EA0),
    "wl2864c_open": (".text", 0x1380, 76, 0x8F07CA55),
}
EXPECTED_VERSIONS = {
    "_printk": 0x92997ED8,
    "gpio_to_desc": 0x0EC43F6F,
    "gpiod_set_raw_value": 0x8DAE9ED0,
    "i2c_transfer": 0xAF50D612,
    "_dev_info": 0xEF3CB484,
    "__stack_chk_fail": 0xC2C193D2,
    "i2c_register_driver": 0x50F5D94E,
    "i2c_del_driver": 0xFEE5BE94,
    "devm_gpiod_get": 0x66E8AB95,
    "_dev_err": 0xF27ED00B,
    "gpiod_set_value": 0x6DBACF3B,
    "devm_gpiod_put": 0xA8CB2B21,
    "usleep_range_state": 0xC3055D20,
    "msleep": 0xF9A482F9,
    "misc_register": 0x06987AEB,
    "misc_deregister": 0x94A9D12B,
    "kmalloc_caches": 0x0F15B38A,
    "kmalloc_trace": 0xB78E7543,
    "__copy_overflow": 0x7682BA4E,
    "__check_object_size": 0x88DB9F48,
    "alt_cb_patch_nops": 0x1348649E,
    "gic_nonsecure_priorities": 0x4B0A3F52,
    "__arch_copy_to_user": 0x9A85EEBB,
    "kfree": 0x037A0CBA,
    "cpu_hwcaps": 0x79E4C52B,
    "memdup_user": 0x5DC263FD,
    "module_layout": 0xEA759D7F,
}
EXPECTED_EXPORTS = {"will_ldo_vout": 0x23EC3223, "will_ldo_en": 0xDD9B9EA1}
EXPECTED_CONSUMER_EXPORTS = {"custom_ldo_vout": 0xFDA530E0, "custom_ldo_en": 0x239D3DF2}
EXPECTED_OBJECT_SIZES = {
    "wl2864c_data": 112,
    "wl2864c_i2c_driver": 280,
    "wl2864c_miscdev": 80,
    "wl2864c_dt_match": 400,
    "wl2864c_id": 64,
    "wl2864c_fops": 272,
    "____versions": 1728,
    "__this_module": 1088,
}
EXPECTED_STRINGS = [
    b"wl2864c_probe", b"WL2864 & WL2868 Power IC Driver", b"will,wl2864c_pmu",
    b"wl2864c", b"vin1", b"reset", b"wl2864c_power_on",
    b"wl2864c_probe successed! chip id = %d", b"wl2864c: update read pos to %02X",
    b"failed to request vin1_en GPIO: %d", b"failed to request reset GPIO: %d",
    b"wl2864c: read REG[%02X %02X]", b"wl2864c: write REG[%02X %02X]",
]


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def dump_section(path: Path, name: str) -> bytes:
    with tempfile.NamedTemporaryFile() as tmp:
        proc = subprocess.run(["llvm-objcopy", "--dump-section", f"{name}={tmp.name}", str(path)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if proc.returncode:
            return b""
        return Path(tmp.name).read_bytes()


class Elf:
    def __init__(self, path: Path):
        self.path = path
        self.sections: dict[str, dict[str, int | str]] = {}
        self.section_index: dict[str, str] = {}
        for line in run("llvm-readelf", "-SW", str(path)).splitlines():
            m = re.match(r"\s*\[\s*(\d+)\]\s+(\S*)\s+(\S+)\s+[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)", line)
            if m:
                idx, name, typ, off, size = m.groups()
                self.section_index[idx] = name
                self.sections[name] = {"type": typ, "offset": int(off, 16), "size": int(size, 16)}
        self.symbols: dict[str, dict[str, int | str]] = {}
        for line in run("llvm-readelf", "-sW", str(path)).splitlines():
            m = re.match(r"\s*\d+:\s+([0-9a-fA-F]+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*(.*)", line)
            if m:
                value, size, typ, bind, vis, ndx, name = m.groups()
                name = name.strip()
                if name and name not in self.symbols:
                    self.symbols[name] = {
                        "value": int(value, 16), "size": int(size), "type": typ,
                        "binding": bind, "visibility": vis, "ndx": ndx,
                        "section": self.section_index.get(ndx, ndx),
                    }
        self.relocations: list[dict[str, int | str]] = []
        relsec = ""
        for line in run("llvm-readelf", "-rW", str(path)).splitlines():
            m = re.match(r"Relocation section '([^']+)'", line)
            if m:
                relsec = m.group(1)
                continue
            m = re.match(r"([0-9a-fA-F]{16})\s+[0-9a-fA-F]{16}\s+(R_AARCH64_\S+)\s+[0-9a-fA-F]{16}\s+(\S+)\s+\+\s+(\S+)", line)
            if m:
                off, typ, symbol, addend = m.groups()
                target = relsec[5:] if relsec.startswith(".rela") else ""
                if target == "_jump_table":
                    target = "__jump_table"
                self.relocations.append({"relsec": relsec, "target": target,
                                         "offset": int(off, 16), "type": typ,
                                         "symbol": symbol, "addend": int(addend, 16)})
        self.functions = {n: s for n, s in self.symbols.items()
                          if s["type"] == "FUNC" and s["ndx"] != "UND"}
        for r in self.relocations:
            r["owner"] = ""
            for name, sym in self.functions.items():
                if sym["section"] == r["target"] and sym["value"] <= r["offset"] < sym["value"] + sym["size"]:
                    r["owner"] = name
                    break

    def section(self, name: str) -> bytes:
        return dump_section(self.path, name)

    def versions(self) -> dict[str, int]:
        data = self.section("__versions")
        if len(data) % 64:
            raise AssertionError("partial __versions record")
        return {data[i + 8:i + 64].split(b"\0", 1)[0].decode(): struct.unpack_from("<Q", data, i)[0]
                for i in range(0, len(data), 64)}

    def kcfi(self, name: str) -> int:
        sym = self.functions[name]
        data = self.section(str(sym["section"]))
        return struct.unpack_from("<I", data, int(sym["value"]) - 4)[0]

    def export_crcs(self) -> dict[str, int]:
        data = self.section("__kcrctab")
        result = {}
        for name, sym in self.symbols.items():
            if name.startswith("__crc_") and sym["section"] == "__kcrctab":
                result[name[6:]] = struct.unpack_from("<I", data, int(sym["value"]))[0]
        return result

    def calls(self, name: str) -> collections.Counter[str]:
        return collections.Counter(str(r["symbol"]) for r in self.relocations
                                   if r["owner"] == name and r["type"] == "R_AARCH64_CALL26")

    def function_bytes(self, name: str) -> bytes:
        sym = self.functions[name]
        data = self.section(str(sym["section"]))
        off, size = int(sym["value"]), int(sym["size"])
        return data[off:off + size]

    def object_relative_relocs(self, name: str) -> list[tuple[int, str, str]]:
        sym = self.symbols[name]
        start, end, section = int(sym["value"]), int(sym["value"]) + int(sym["size"]), str(sym["section"])
        return sorted((int(r["offset"]) - start, str(r["type"]), str(r["symbol"]))
                      for r in self.relocations if r["target"] == section and start <= int(r["offset"]) < end)


def expect(checks: list[tuple[str, bool]], name: str, condition: bool) -> None:
    checks.append((name, bool(condition)))


def main() -> int:
    required = [STOCK, RECON, STOCK_CONSUMER, RECON_CONSUMER, SOURCE, BUILD_LOG, CONSUMER_BUILD_LOG]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        print("MISSING:", *missing, sep="\n")
        return 1

    stock, recon = Elf(STOCK), Elf(RECON)
    stock_consumer, recon_consumer = Elf(STOCK_CONSUMER), Elf(RECON_CONSUMER)
    source = SOURCE.read_text()
    checks: list[tuple[str, bool]] = []

    expect(checks, "stock oracle SHA256", hashlib.sha256(STOCK.read_bytes()).hexdigest() == EXPECTED_SHA256)
    expect(checks, "stock oracle size", STOCK.stat().st_size == 35544)
    expect(checks, "exact stock function set", set(stock.functions) == set(EXPECTED_FUNCTIONS))
    expect(checks, "exact reconstructed function set", set(recon.functions) == set(EXPECTED_FUNCTIONS))
    expect(checks, "stock function section/offset/size", all(
        (s["section"], s["value"], s["size"]) == expected[:3]
        for name, expected in EXPECTED_FUNCTIONS.items() for s in [stock.functions[name]]))
    expect(checks, "stock KCFI map", all(stock.kcfi(name) == values[3] for name, values in EXPECTED_FUNCTIONS.items()))
    expect(checks, "reconstructed KCFI map", all(recon.kcfi(name) == values[3] for name, values in EXPECTED_FUNCTIONS.items()))
    expect(checks, "exact 27 stock MODVERSION map", stock.versions() == EXPECTED_VERSIONS)
    expect(checks, "exact 27 reconstructed MODVERSION map", recon.versions() == EXPECTED_VERSIONS)
    expect(checks, "exact stock exports/CRCs", stock.export_crcs() == EXPECTED_EXPORTS)
    expect(checks, "exact reconstructed exports/CRCs", recon.export_crcs() == EXPECTED_EXPORTS)
    expect(checks, "all per-function call multisets", all(stock.calls(name) == recon.calls(name) for name in EXPECTED_FUNCTIONS))

    for name, size in EXPECTED_OBJECT_SIZES.items():
        expect(checks, f"stock object {name} size", name in stock.symbols and stock.symbols[name]["size"] == size)
        expect(checks, f"recon object {name} size", name in recon.symbols and recon.symbols[name]["size"] == size)

    expect(checks, "stock/recon exact .data bytes", stock.section(".data") == recon.section(".data"))
    expect(checks, "stock/recon exact important strings", stock.section(".rodata.str1.1") == recon.section(".rodata.str1.1"))
    combined_stock = STOCK.read_bytes()
    combined_recon = RECON.read_bytes()
    expect(checks, "all exact important strings present", all(x in combined_stock and x in combined_recon for x in EXPECTED_STRINGS))

    tables = [
        struct.pack("<7i", 60000, 60000, 120000, 120000, 120000, 120000, 120000),
        struct.pack("<7i", -6000, -6000, -12000, -12000, -12000, -12000, -12000),
        struct.pack("<7i", 49600, 49600, 150400, 150400, 150400, 150400, 150400),
        struct.pack("<7i", -4960, -4960, -15040, -15040, -15040, -15040, -15040),
    ]
    expect(checks, "stock voltage tables exact offsets", all(stock.section(".rodata")[o:o + 28] == t
           for o, t in zip((0x2E0, 0x2FC, 0x318, 0x334), tables)))
    expect(checks, "recon voltage tables exact content", all(t in recon.section(".rodata") for t in tables))
    expect(checks, "voltage source formulas exact", all(x in source for x in [
        "value / 100", "/ 125", "/ 80", "WL2864C_VOUT_FIRST + ldo_num - 1",
        "value < floor[ldo_num - 1] ? 0", "return ret < 0 ? ret : 0",
    ]))
    expect(checks, "enable register/bit mapping source", all(x in source for x in [
        "WL2864C_REG_ENABLE       0x0e", "BIT(ldo_num - 1)",
        "write_value = value ? value | BIT(7) : 0", "if (enable)",
    ]))
    expect(checks, "chip dispatch IDs and forced address", all(x in source for x in [
        "WL2864C_ID               0x01", "WL2868C_ID               0x82",
        "WL2864C_FORCED_I2C_ADDR  0x2f", "client->addr = WL2864C_FORCED_I2C_ADDR",
    ]))

    probe_calls = stock.calls("wl2864c_probe")
    expect(checks, "probe no I2C transfer", probe_calls["i2c_transfer"] == 0)
    expect(checks, "probe GPIO/misc/delay call counts", all(probe_calls[k] == v for k, v in {
        "devm_gpiod_get": 2, "devm_gpiod_put": 2, "gpiod_set_value": 4,
        "usleep_range_state": 3, "msleep": 1, "misc_register": 1,
    }.items()))
    normalized = re.sub(r"\s+", " ", source)
    probe_tokens = [
        'devm_gpiod_get(dev, "vin1", GPIOD_OUT_HIGH)',
        'devm_gpiod_get(dev, "reset", GPIOD_OUT_HIGH)',
        "gpiod_set_value(wl2864c_data.reset, 1); usleep_range(10000, 11000); gpiod_set_value(wl2864c_data.reset, 0); usleep_range(10000, 11000); gpiod_set_value(wl2864c_data.reset, 1); usleep_range(10000, 11000);",
        "msleep(1); client->addr = WL2864C_FORCED_I2C_ADDR; wl2864c_data.chip_id = WL2868C_ID;",
    ]
    expect(checks, "exact probe/GPIO source order", all(x in normalized for x in probe_tokens))
    expect(checks, "private struct exact static assertions", all(x in source for x in [
        "sizeof(struct wl2864c_state) == 0x70", "reset) == 0x30", "vin1) == 0x38",
        "vin2_gpio) == 0x40", "chip_id) == 0x44", "read_pos) == 0x68", "probe_ready) == 0x6c",
    ]))

    fops_expected = [(0x0, "R_AARCH64_ABS64", "__this_module"),
                     (0x8, "R_AARCH64_ABS64", "wl2864c_llseek"),
                     (0x10, "R_AARCH64_ABS64", ".text"),
                     (0x18, "R_AARCH64_ABS64", ".text"),
                     (0x70, "R_AARCH64_ABS64", ".text")]
    expect(checks, "stock fops exact slots", stock.object_relative_relocs("wl2864c_fops") == fops_expected)
    expect(checks, "recon fops exact slots", recon.object_relative_relocs("wl2864c_fops") == fops_expected)
    expect(checks, "misc ABI source quirks", all(x in source for x in [
        ".minor = 250", "return file->f_pos", "out = kmalloc(128, GFP_KERNEL)",
        "if (count > 20)", "for (i = 0; i < count; i += 6)",
        "return -ENODEV", "(void)copy_to_user", "return count",
    ]) and ".release" not in source and ".unlocked_ioctl" not in source)

    expect(checks, "raw I2C only and transfer topology", source.count("i2c_transfer(") == 2
           and ".len = 1" in source and ".len = 2" in source and "I2C_M_RD" in source
           and "regmap" not in source and "i2c_smbus" not in source)
    expect(checks, "lifecycle callback slots/calls", stock.calls("wl2864c_remove") == recon.calls("wl2864c_remove")
           and stock.calls("cleanup_module") == recon.calls("cleanup_module")
           and ".shutdown" not in source and "misc_deregister(&wl2864c_miscdev)" in source)

    expect(checks, "build log success", "Build completed successfully" in BUILD_LOG.read_text()
           and not re.search(r"\bwarning:", BUILD_LOG.read_text(), re.I)
           and "check_no_remaining" in BUILD_LOG.read_text())
    expect(checks, "consumer build log success", "Build completed successfully" in CONSUMER_BUILD_LOG.read_text()
           and not re.search(r"\bwarning:", CONSUMER_BUILD_LOG.read_text(), re.I)
           and "check_no_remaining" in CONSUMER_BUILD_LOG.read_text())
    cvers = recon_consumer.versions()
    expect(checks, "downstream provider import CRCs", cvers.get("will_ldo_vout") == EXPECTED_EXPORTS["will_ldo_vout"]
           and cvers.get("will_ldo_en") == EXPECTED_EXPORTS["will_ldo_en"])
    expect(checks, "downstream custom_ldo export CRCs", recon_consumer.export_crcs() == EXPECTED_CONSUMER_EXPORTS)
    expect(checks, "downstream two function bytes exact", all(
        name in stock_consumer.functions and name in recon_consumer.functions
        and stock_consumer.function_bytes(name) == recon_consumer.function_bytes(name)
        for name in EXPECTED_CONSUMER_EXPORTS))

    passed = sum(ok for _, ok in checks)
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}\t{name}")
    print(f"{passed}/{len(checks)} CHECKS PASSED")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
