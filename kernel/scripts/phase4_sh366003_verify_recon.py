#!/usr/bin/env python3
"""Fail-closed static verifier for the GQ5012BF1 SH366003 reconstruction.

No device access is performed. The verifier reads only frozen/rebuilt ELF files
and reconstruction source. It intentionally validates hardware-significant
behavior rather than debug-line/source-path string identity.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STOCK = ROOT / "workspace/phase4-sh366003/oracle/sh366003_fg.stock.ko"
RECON = ROOT / "workspace/phase4-sh366003/recon/sh366003_fg.recon.ko"
SOURCE = ROOT / "kernel/phase4-sh366003-recon/sh366003_fg.c"
AFI = ROOT / "workspace/phase4-sh366003/oracle/sinofs_afi_data.stock.bin"

failures: list[str] = []
passes: list[str] = []

def check(ok: bool, label: str) -> None:
    (passes if ok else failures).append(label)

def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def imports(path: Path) -> set[str]:
    result = set()
    for line in run("llvm-nm", "-u", str(path)).splitlines():
        if line.split():
            result.add(line.split()[-1])
    return result

def modversions(path: Path) -> dict[str, str]:
    result = {}
    for line in run("modprobe", "--show-modversions", str(path)).splitlines():
        crc, name = line.split()[:2]
        result[name] = crc.lower()
    return result

def functions(path: Path) -> dict[str, int]:
    result = {}
    for line in run("llvm-readelf", "-sW", str(path)).splitlines():
        m = re.match(r"\s*\d+:\s+[0-9a-f]+\s+(\d+)\s+FUNC\s+\w+\s+\w+\s+(\S+)\s+(.+)", line)
        if m and m.group(2) != "UND":
            result[m.group(3)] = int(m.group(1))
    return result

def function_bytes(path: Path) -> dict[str, bytes]:
    sec_off: dict[str, int] = {}
    sec_idx: dict[str, str] = {}
    for line in run("llvm-readelf", "-SW", str(path)).splitlines():
        m = re.match(r"\s*\[\s*(\d+)\]\s+(\S+)\s+\S+\s+\S+\s+([0-9a-f]+)", line)
        if m:
            sec_idx[m.group(1)] = m.group(2)
            sec_off[m.group(2)] = int(m.group(3), 16)
    raw = path.read_bytes()
    result = {}
    for line in run("llvm-readelf", "-sW", str(path)).splitlines():
        m = re.match(r"\s*\d+:\s+([0-9a-f]+)\s+(\d+)\s+FUNC\s+\w+\s+\w+\s+(\d+)\s+(.+)", line)
        if not m:
            continue
        value, size, idx, name = int(m.group(1), 16), int(m.group(2)), m.group(3), m.group(4)
        section = sec_idx[idx]
        start = sec_off[section] + value
        result[name] = raw[start:start + size]
    return result

def kcfi_typeids(path: Path) -> dict[str, int]:
    """Return KCFI type words for defined global functions."""
    sections: dict[str, tuple[str, int]] = {}
    for line in run("llvm-readelf", "-SW", str(path)).splitlines():
        m = re.match(r"\s*\[\s*(\d+)\]\s+(\S+)\s+\S+\s+\S+\s+([0-9a-f]+)", line)
        if m:
            sections[m.group(1)] = (m.group(2), int(m.group(3), 16))
    raw = path.read_bytes()
    result: dict[str, int] = {}
    for line in run("llvm-readelf", "-sW", str(path)).splitlines():
        m = re.match(r"\s*\d+:\s+([0-9a-f]+)\s+\d+\s+FUNC\s+GLOBAL\s+DEFAULT\s+(\d+)\s+(\S+)", line)
        if not m:
            continue
        value, idx, name = int(m.group(1), 16), m.group(2), m.group(3)
        _, offset = sections[idx]
        result[name] = int.from_bytes(raw[offset + value - 4:offset + value], "little")
    return result


def require_source(text: str, label: str) -> None:
    check(text in source, label)

for p in (STOCK, RECON, SOURCE, AFI):
    check(p.is_file(), f"artifact exists: {p.relative_to(ROOT)}")
if failures:
    for item in failures:
        print("FAIL:", item)
    sys.exit(1)

source = SOURCE.read_text()
check(sha256(STOCK) == "527bddb4ddb11e94ed85e6969a10f807178cbb3f0fd326c8509824800a3d61a7", "stock oracle SHA256")
check(len(AFI.read_bytes()) == 2142, "AFI size 2142")
check(sha256(AFI) == "4888c5bc4b847ec6c118cd7bd334cbcffbf52c5fa2bf8f8660c3ac65e03359e1", "AFI SHA256")
check(RECON.read_bytes().count(AFI.read_bytes()) == 1, "rebuilt ELF embeds exact AFI once")

stock_imports, recon_imports = imports(STOCK), imports(RECON)
check(stock_imports == recon_imports, "exact undefined/import symbol set")
stock_versions, recon_versions = modversions(STOCK), modversions(RECON)
check(stock_versions == recon_versions, "exact 36-entry MODVERSION map")
for name, crc in {
    "fuelgauge_fw_version": "0x8c280260",
    "yft_fuelgauge_device_add": "0xf5752941",
    "yft_set_fuelgauge_device_used": "0x82093a2e",
}.items():
    check(recon_versions.get(name) == crc, f"stock YFT CRC {name}={crc}")

stock_funcs, recon_funcs = functions(STOCK), functions(RECON)
check(set(stock_funcs) == set(recon_funcs), "exact named function set")
check(len(stock_funcs) == 39 and len(recon_funcs) == 39, "stock/rebuilt function counts 39/39")
stock_kcfi, recon_kcfi = kcfi_typeids(STOCK), kcfi_typeids(RECON)
check(stock_kcfi == recon_kcfi, "exact global-function KCFI type-ID map")

# Parse AFI records and enforce every state transition and count.
blob = AFI.read_bytes()
pos = 0
counts = Counter()
waits = Counter()
writes = Counter()
dataflash_addresses = []
while pos < len(blob):
    op = blob[pos]
    check(op in (1, 2, 3, 4), f"valid AFI opcode at 0x{pos:x}")
    if op not in (1, 2, 3, 4):
        break
    size = 4 if op in (1, 4) else 4 + blob[pos + 3]
    check(pos + size <= len(blob), f"bounded AFI record at 0x{pos:x}")
    rec = blob[pos:pos + size]
    counts[op] += 1
    if op == 4:
        waits[int.from_bytes(rec[2:4], "big")] += 1
    elif op == 2:
        writes[rec[2]] += 1
        if rec[2] == 0x3e and len(rec) >= 6:
            address = int.from_bytes(rec[4:6], "little")
            if address >= 0x4000:
                dataflash_addresses.append(address)
    pos += size
check(pos == 0x85e == len(blob), "AFI terminal offset 0x85e")
check(counts == Counter({2: 104, 4: 104, 3: 1}), "AFI opcode multiset")
check(waits == Counter({2: 51, 5: 51, 1500: 2}), "AFI wait multiset")
check(writes == Counter({0x3e: 52, 0x60: 51, 0x00: 1}), "AFI write-register multiset")
check(len(dataflash_addresses) == 51 and dataflash_addresses[0] == 0x4000 and dataflash_addresses[-1] == 0x47b8 and all(a < b for a, b in zip(dataflash_addresses, dataflash_addresses[1:])), "AFI monotonic data-flash address progression")
check(blob[-18:] == bytes.fromhex("02aa00024500040205dc02aa3e024600040205dc03aa3e044600d38c")[-18:], "AFI final activation/version tail")

# Hardware identity, DT, public ABI, scaling, monitor, update gate, and safety.
for token, label in [
    ("#define SH366003_DEVICE_ID            0x0603", "device ID 0x0603"),
    ("#define CMD_DEVICE_ID                 (CMD_CONTROL | 0x0001)", "device-ID subcommand 0x0001"),
    ('{ .compatible = "sh,sh366003" }', "OF compatible"),
    ('#define SH366003_PSY_NAME             "3rd-gauge"', "power-supply name"),
    ('power_supply_get_by_name("primary_chg")', "primary charger dependency"),
    ('of_find_node_by_path("/chosen")', "chosen boot-mode path"),
    ('of_find_node_by_path("/chosen@0")', "chosen@0 fallback"),
    ('of_get_property(node, "atag,boot", &len)', "atag,boot gate"),
    ("SH366003_ALLOW_AFI_PROGRAMMING 0", "default AFI fail-closed mode"),
    ("if (!sh366003_allow_afi_programming)", "runtime programming safety gate"),
    ("value * 1000", "current raw-to-uA scale"),
    ("sm->temp = ret - 2731", "temperature deciKelvin conversion"),
    ("SH366003_MONITOR_FIRST        2500", "monitor initial delay"),
    ("SH366003_MONITOR_PERIOD       1250", "monitor recurring delay"),
    ("SH366003_UPDATE_DELAY         3000", "update initial delay"),
    ("SH366003_PROFILE_VERSION      0x5a93", "profile version 0x5a93"),
    ("SH366003_MIN_UPDATE_SOC       11", "minimum update SOC"),
    ("SH366003_MIN_FCC              3500", "minimum accepted FCC"),
    ('file_decode_process(sm, "sinofs_afi_data")', "embedded AFI selector"),
    ("0x5678, 0x1234, 0xcdef, 0x90ab", "unseal key sequence"),
]:
    require_source(token, label)

expected_props = [
    "POWER_SUPPLY_PROP_STATUS", "POWER_SUPPLY_PROP_PRESENT",
    "POWER_SUPPLY_PROP_VOLTAGE_NOW", "POWER_SUPPLY_PROP_CURRENT_NOW",
    "POWER_SUPPLY_PROP_CAPACITY", "POWER_SUPPLY_PROP_TEMP",
    "POWER_SUPPLY_PROP_CHARGE_FULL_DESIGN", "POWER_SUPPLY_PROP_TECHNOLOGY",
    "POWER_SUPPLY_PROP_CYCLE_COUNT", "POWER_SUPPLY_PROP_HEALTH",
]
prop_block = re.search(r"sh_fg_battery_props\[\]\s*=\s*\{(.*?)\};", source, re.S)
actual_props = re.findall(r"POWER_SUPPLY_PROP_[A-Z_]+", prop_block.group(1) if prop_block else "")
check(actual_props == expected_props, "exact ordered 3rd-gauge property list")

expected_regs = {
    "SBS_CONTROL": "0x00", "SBS_TEMP": "0x06", "SBS_VOLTAGE": "0x08",
    "SBS_BATTERY_STATUS": "0x0a", "SBS_CURRENT": "0x0c",
    "SBS_REMAINING_CAPACITY": "0x10", "SBS_FCC": "0x12",
    "SBS_INT_TEMP": "0x28", "SBS_CYCLE_COUNT": "0x2a",
    "SBS_RSOC": "0x2c", "SBS_SOH": "0x2e", "SBS_VCHG": "0x30",
    "SBS_ICHG": "0x32", "SBS_MAC": "0x3e", "SBS_MAC_DATA": "0x40",
    "SBS_MAC_CHECKSUM": "0x60",
}
for name, value in expected_regs.items():
    check(re.search(rf"#define\s+{name}\s+{value}\b", source) is not None, f"register {name}={value}")
for cmd in ("0x0021", "0x0030", "0x0041", "0x0046", "0x004c", "0x004d", "0x004e", "0x0050", "0x0051", "0x0052", "0x0053", "0x0054", "0x0055", "0x0056", "0x0057", "0x0060", "0x0067", "0x0071", "0x00c1", "0x00c5", "0x40d9"):
    check(cmd in source, f"MAC command {cmd}")

for attr in ("chipid", "force_upgrade", "fw_version", "manufacturing_date", "manufacturing_year", "manufacturing_month", "manufacturing_day", "manufacturename", "serialnum", "soh"):
    check(re.search(rf"__ATTR\({attr},", source) is not None, f"class attribute {attr}")

for call in ("fg_read_Voltage(sm);", "fg_read_Current(sm);", "fg_read_IntTemperature(sm, &word);", "fg_read_ExtTemperature(sm);", "SBS_SOH", "SBS_CYCLE_COUNT", "SBS_REMAINING_CAPACITY", "fg_read_fcc(sm);", "MAC_DA_STATUS1"):
    check(call in source, f"monitor call/constant {call}")

critical_strings = [b"3rd-gauge\0", b"sh,sh366003\0", b"sh366003\0", b"primary_chg\0", b"sinofs_afi_data\0", b"/chosen\0", b"/chosen@0\0", b"atag,boot\0", b"manufacturing_date\0", b"force_upgrade\0"]
for item in critical_strings:
    check(item in RECON.read_bytes(), f"critical rebuilt string {item[:-1].decode()}")

sf_bytes, rf_bytes = function_bytes(STOCK), function_bytes(RECON)
shared = set(sf_bytes) & set(rf_bytes)
size_identical = sum(len(sf_bytes[n]) == len(rf_bytes[n]) for n in shared)
byte_identical = sum(sf_bytes[n] == rf_bytes[n] for n in shared)

print(f"stock_functions={len(stock_funcs)}")
print(f"reconstructed_functions={len(recon_funcs)}")
print(f"shared_functions={len(set(stock_funcs) & set(recon_funcs))}")
print(f"size_identical_functions={size_identical}")
print(f"byte_identical_functions={byte_identical}")
print(f"stock_imports={len(stock_imports)} reconstructed_imports={len(recon_imports)}")
print(f"modversions={len(stock_versions)} exact_map={stock_versions == recon_versions}")
print(f"global_kcfi={len(stock_kcfi)} exact_map={stock_kcfi == recon_kcfi}")
print(f"checks={len(passes) + len(failures)} passed={len(passes)} failed={len(failures)}")
for item in failures:
    print("FAIL:", item)
if failures:
    print("BEHAVIORAL_VERIFIER=FAIL")
    sys.exit(1)
print("BEHAVIORAL_VERIFIER=PASS")
