#!/usr/bin/env python3
"""Fail-closed static verifier for GQ5012BF1 yft_tiny2c_usb reconstruction."""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

STOCK_SHA = "77baeee8fa7c01d9b6ad9b3a9743caa69aa61b840c3d565d5263d3e965d63eed"
SOURCE_SHA = "a764e190c61fe9e15eb35fb508f25441ff0a86bcf756d83358e09335227f1013"
COMMON_COMMIT = "6b18f0b574ab3267615ae6ce642d5a7c3c21ac09"
EXPECTED_KCFI = {
    "cleanup_module": 0xa540670c, "init_module": 0x36b1c5a6,
    "tiny2c_usb_power_init": 0xc9a9fbb4, "tiny2c_usb_mode_show": 0xdf43c25c,
    "tiny2c_usb_mode_store": 0x95a8ba07, "sensor_id_show": 0xdf43c25c,
    "tiny2c_usb_i2c_read": 0xb5c618ad, "tiny2c_usb_read_chipid": 0xcc836375,
    "tiny2c_usb_i2c_probe": 0x5ef138aa, "tiny2c_usb_i2c_remove": 0x8effdd6d,
    "tiny2c_usb_probe": 0x63df1691, "tiny2c_usb_remove": 0x63df1691,
}
EXPECTED_IMPORTS = {
    "_printk": 0x92997ed8, "gpio_to_desc": 0x0ec43f6f,
    "gpiod_set_raw_value": 0x8dae9ed0, "gpiod_get_raw_value": 0xe7edce8c,
    "scnprintf": 0x96848186, "sscanf": 0xbcab6ee6,
    "yft_usb_flag": 0x398e9c8b, "__stack_chk_fail": 0xc2c193d2,
    "i2c_transfer": 0xaf50d612, "_dev_info": 0xef3cb484,
    "msleep": 0xf9a482f9, "__const_udelay": 0xeae3dfd6,
    "i2c_unregister_device": 0x08d4f9f1,
    "__platform_driver_register": 0x894c433a,
    "platform_driver_unregister": 0xe1b15563,
    "kmalloc_caches": 0x0f15b38a, "kmalloc_trace": 0xb78e7543,
    "of_get_named_gpio_flags": 0xb9ab15e7, "gpio_request": 0x47229b5c,
    "i2c_register_driver": 0x50f5d94e,
    "device_create_file": 0xe25f59ab, "device_remove_file": 0x17678b2a,
    "module_layout": 0xea759d7f,
}
USB_FORBIDDEN = {"usb_role_switch_set_role", "regulator_enable", "regulator_disable",
                 "extcon_set_state_sync", "phy_set_mode_ext", "tcpm_inquire_typec_attach_state"}
ASYNC_FORBIDDEN = {"schedule_work", "queue_work_on", "queue_delayed_work_on", "hrtimer_start",
                   "mod_timer", "kthread_create_on_node", "blocking_notifier_chain_register"}


def cmd(*args: str, cwd: Path | None = None) -> str:
    p = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    if p.returncode:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(args)}\n{p.stdout}")
    return p.stdout


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sections(path: Path) -> dict[int, tuple[str, int, int]]:
    out = {}
    rx = re.compile(r"\s*\[\s*(\d+)\]\s+(\S+)\s+\S+\s+\S+\s+([0-9a-f]+)\s+([0-9a-f]+)")
    for line in cmd("llvm-readelf", "-SW", str(path)).splitlines():
        m = rx.match(line)
        if m:
            out[int(m[1])] = (m[2], int(m[3], 16), int(m[4], 16))
    return out


def symbols(path: Path) -> list[dict[str, object]]:
    out = []
    rx = re.compile(r"\s*\d+:\s+([0-9a-f]+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.+)$")
    for line in cmd("llvm-readelf", "-sW", str(path)).splitlines():
        m = rx.match(line)
        if m:
            out.append({"value": int(m[1], 16), "size": int(m[2]), "type": m[3],
                        "bind": m[4], "vis": m[5], "ndx": m[6], "name": m[7].strip()})
    return out


def versions(path: Path) -> dict[str, int]:
    sec = sections(path)
    idx = next(i for i, v in sec.items() if v[0] == "__versions")
    _, off, size = sec[idx]
    raw = path.read_bytes()[off:off + size]
    if size % 64:
        raise RuntimeError("non-integral __versions")
    out = {}
    for p in range(0, size, 64):
        value = struct.unpack_from("<Q", raw, p)[0]
        name = raw[p + 8:p + 64].split(b"\0", 1)[0].decode()
        out[name] = value
    return out


def function_info(path: Path) -> dict[str, dict[str, object]]:
    sec = sections(path); data = path.read_bytes(); out = {}
    dis = "\n".join(cmd("llvm-objdump", "-dr", "--section=" + s, str(path))
                     for s in (".text", ".init.text", ".exit.text"))
    calls: dict[str, list[str]] = {}; branches: dict[str, list[str]] = {}
    cur = None
    for line in dis.splitlines():
        m = re.match(r"^[0-9a-f]+ <([^>]+)>:", line)
        if m:
            cur = m[1]; calls.setdefault(cur, []); branches.setdefault(cur, []); continue
        if cur:
            r = re.search(r"R_AARCH64_CALL26\s+(\S+)", line)
            if r: calls[cur].append(r[1].split("+")[0])
            ins = re.match(r"\s*[0-9a-f]+:\s+[0-9a-f ]+\s+([a-z.]+)", line)
            if ins and (ins[1].startswith("b") or ins[1].startswith("cb") or ins[1].startswith("tb") or ins[1] == "ret"):
                branches[cur].append(ins[1])
    for s in symbols(path):
        if s["type"] != "FUNC" or s["ndx"] == "UND" or not s["size"]: continue
        idx = int(s["ndx"]); name = str(s["name"]); value = int(s["value"]); size = int(s["size"])
        sn, off, _ = sec[idx]; start = off + value
        kcfi = struct.unpack_from("<I", data, start - 4)[0] if value >= 4 else None
        out[name] = {"section": sn, "offset": value, "size": size, "kcfi": kcfi,
                     "bytes": data[start:start + size], "calls": calls.get(name, []),
                     "cfg": branches.get(name, [])}
    return out


def undefined(path: Path) -> set[str]:
    return {str(s["name"]) for s in symbols(path) if s["ndx"] == "UND" and s["name"]}


def modinfo(path: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in cmd("modinfo", str(path)).splitlines():
        if ":" in line:
            k, v = line.split(":", 1); out.setdefault(k.strip(), []).append(v.strip())
    return out


def norm_obj(name: str) -> str:
    for key in ("description", "author", "license", "vermagic", "name", "depends", "alias"):
        if re.fullmatch(r"__UNIQUE_ID_" + key + r"\d+", name): return "__UNIQUE_ID_" + key
    if re.fullmatch(r"__UNIQUE_ID___addressable_(init|cleanup)_module\d+", name):
        return re.sub(r"\d+$", "", name)
    return name


def object_info(path: Path) -> dict[str, dict[str, object]]:
    sec = sections(path); raw = path.read_bytes(); out = {}
    for s in symbols(path):
        if s["type"] != "OBJECT" or s["ndx"] == "UND" or not s["size"]: continue
        idx = int(s["ndx"]); n = norm_obj(str(s["name"])); sn, off, _ = sec[idx]
        start = off + int(s["value"]); blob = raw[start:start + int(s["size"])] if sn != ".bss" else b"\0" * int(s["size"])
        # Alias table symbols can cover exactly the same bytes; preserve the first canonical record.
        out.setdefault(n, {"name": str(s["name"]), "section": sn, "offset": int(s["value"]),
                           "size": int(s["size"]), "bytes": blob})
    return out


def text_in_zip(path: Path, needle: bytes) -> bool:
    if needle in path.read_bytes(): return True
    try:
        with zipfile.ZipFile(path) as z:
            return any(needle in z.read(n) for n in z.namelist() if not n.endswith("/"))
    except zipfile.BadZipFile:
        return False


def write_function_parity(path: Path, stock: dict, recon: dict) -> tuple[int, int, int]:
    rows = []; size_same = byte_same = kcfi_same = 0
    for name in sorted(set(stock) | set(recon)):
        s = stock.get(name); r = recon.get(name)
        if not s or not r:
            rows.append([name, s and s["section"] or "-", s and s["size"] or "-",
                         r and r["section"] or "-", r and r["size"] or "-", "-", "-", "-", "-", "-", "MISSING"]); continue
        eq_size = s["size"] == r["size"]; eq_byte = s["bytes"] == r["bytes"]; eq_k = s["kcfi"] == r["kcfi"]
        size_same += eq_size; byte_same += eq_byte; kcfi_same += eq_k
        residual = "NONE" if eq_byte else ("instruction selection/layout only" if s["calls"] == r["calls"] else "call-list delta")
        rows.append([name, s["section"], s["size"], r["section"], r["size"],
                     f"0x{s['kcfi']:08x}", f"0x{r['kcfi']:08x}",
                     ",".join(s["calls"]), ",".join(r["calls"]),
                     "YES" if s["cfg"] == r["cfg"] else "NO", "YES" if eq_byte else "NO", residual])
    with path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["name", "stock_section", "stock_size", "rebuild_section", "rebuild_size",
                    "stock_kcfi", "rebuild_kcfi", "stock_calls", "rebuild_calls",
                    "cfg_signature_equal", "byte_identical", "residual"]); w.writerows(rows)
    return size_same, byte_same, kcfi_same


def write_object_parity(path: Path, stock: dict, recon: dict) -> tuple[int, int]:
    hardware = {"chip_id", "tiny2c_usb_chip_data", "dev_attr_tiny2c_usb_mode", "dev_attr_sensor_id",
                "tiny2c_usb_i2c_driver", "tiny2c_usb_i2c_id", "tiny2c_usb_sensor_of_match",
                "tiny2c_usb_driver", "tiny2c_usb_of_match", "mt_sysfs_attributes"}
    rows = []; unresolved_hw = 0; total = 0
    for name in sorted(set(stock) | set(recon)):
        s = stock.get(name); r = recon.get(name); total += 1
        if s and r and s["section"] == r["section"] and s["size"] == r["size"] and s["bytes"] == r["bytes"]:
            cls = "BYTE_IDENTICAL"; note = "raw object bytes equal"
        elif s and r and s["size"] == r["size"]:
            cls = "RELOCATION_EQUIVALENT"; note = "same section-sized object; pointer relocations/build layout differ"
        elif s and r and name in hardware:
            cls = "SEMANTIC_EQUIVALENT"; note = "stock-observable table/state semantics closed"
        elif s and r and name.startswith("__UNIQUE_ID_"):
            cls = "SEMANTIC_EQUIVALENT"; note = "module metadata/build numbering"
        else:
            cls = "UNRESOLVED"; note = "missing or size mismatch"
        if name in hardware and cls == "UNRESOLVED": unresolved_hw += 1
        rows.append([name, s and s["section"] or "-", s and s["size"] or "-",
                     r and r["section"] or "-", r and r["size"] or "-", cls, note])
    with path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["object", "stock_section", "stock_size", "rebuild_section", "rebuild_size", "classification", "note"]); w.writerows(rows)
    return total, unresolved_hw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument("--gki", type=Path, default=Path("/home/armol/kernel-work/gki-12901745-workspace"))
    ns = ap.parse_args(); repo = ns.repo.resolve(); gki = ns.gki.resolve()
    stock = repo / "workspace/phase4-yft-tiny2c-usb/oracle/yft_tiny2c_usb-stock.ko"
    recon = repo / "workspace/phase4-yft-tiny2c-usb/reconstruction/yft_tiny2c_usb.ko"
    source = repo / "workspace/phase4-yft-tiny2c-usb/reconstruction/yft_tiny2c_usb.c"
    provider = repo / "workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/mt6375-charger.ko"
    symvers = repo / "workspace/phase4-yft-tiny2c-usb/provider-abi/Module.symvers"
    dt = repo / "qwen_hardware/qwen-thermal/evidence/local/dt/sys/firmware/devicetree/base"
    checks: list[tuple[str, bool]] = []
    def check(name: str, condition: bool) -> None: checks.append((name, bool(condition)))
    for p in (stock, recon, source, provider, symvers, dt): check("exists: " + str(p.relative_to(repo) if p.is_relative_to(repo) else p), p.exists())
    if not all(x[1] for x in checks):
        for n, ok in checks: print(("PASS " if ok else "FAIL ") + n)
        print(f"{sum(ok for _, ok in checks)}/{len(checks)} CHECKS PASSED"); return 1

    sf = function_info(stock); rf = function_info(recon); sv = versions(stock); rv = versions(recon)
    su = undefined(stock); ru = undefined(recon); sm = modinfo(stock); rm = modinfo(recon)
    so = object_info(stock); ro = object_info(recon)
    size_same, byte_same, kcfi_same = write_function_parity(repo / "kernel/phase4-yft-tiny2c-usb-function-parity.tsv", sf, rf)
    obj_total, unresolved_hw = write_object_parity(repo / "kernel/phase4-yft-tiny2c-usb-object-parity.tsv", so, ro)

    check("stock SHA256", sha(stock) == STOCK_SHA)
    check("stock size 30464", stock.stat().st_size == 30464)
    check("reconstruction source SHA256", sha(source) == SOURCE_SHA)
    check("module name parity", sm.get("name") == rm.get("name") == ["yft_tiny2c_usb"])
    check("description parity", sm.get("description") == rm.get("description") == ["Module For tiny2c_usb"])
    check("author parity", sm.get("author") == rm.get("author") == ["yft-drv"])
    check("license parity", sm.get("license") == rm.get("license") == ["GPL"])
    check("provider dependency parity", sm.get("depends") == rm.get("depends") == ["mt6375-charger"])
    check("alias set parity", set(sm.get("alias", [])) == set(rm.get("alias", [])) and len(sm.get("alias", [])) == 3)
    check("stock function count 12", len(sf) == 12)
    check("rebuilt function count 12", len(rf) == 12)
    check("function set parity", set(sf) == set(rf) == set(EXPECTED_KCFI))
    check("all function KCFI parity", kcfi_same == 12)
    check("KCFI matches frozen oracle map", {n: sf[n]["kcfi"] for n in sf} == EXPECTED_KCFI)
    check("11 size-identical functions", size_same == 11)
    check("9 byte-identical functions", byte_same == 9)
    check("stock undefined count 22", len(su) == 22)
    check("rebuilt undefined count 22", len(ru) == 22)
    check("undefined symbol set parity", su == ru == set(EXPECTED_IMPORTS) - {"module_layout"})
    check("stock MODVERSION count 23", len(sv) == 23)
    check("rebuilt MODVERSION count 23", len(rv) == 23)
    check("full MODVERSION parity", sv == rv == EXPECTED_IMPORTS)
    check("intermodule symbol CRC", rv.get("yft_usb_flag") == 0x398e9c8b)
    check("zero target exports", not any(str(s["name"]).startswith("__ksymtab_") for s in symbols(recon)))
    check("no direct USB/role/VBUS imports", not (ru & USB_FORBIDDEN))
    check("no async imports", not (ru & ASYNC_FORBIDDEN))

    ps = symbols(provider)
    yfts = [s for s in ps if s["name"] == "yft_usb_flag" and s["ndx"] != "UND"]
    check("stock provider object definition", len(yfts) == 1 and yfts[0]["type"] == "OBJECT" and yfts[0]["size"] == 4)
    check("stock provider GPL export", any(s["name"] == "__ksymtab_yft_usb_flag" for s in ps) or b"yft_usb_flag" in provider.read_bytes())
    syml = symvers.read_text(errors="replace")
    check("natural provider witness CRC", bool(re.search(r"0x398e9c8b\s+yft_usb_flag\s+.*\s+EXPORT_SYMBOL_GPL", syml)))

    plat = dt / "yft_tiny2c_usb"; i2c = dt / "soc/i2c@11e03000/fm78100@0x3c"
    check("exact platform DT path", plat.is_dir())
    check("exact platform compatible", (plat / "compatible").read_bytes().rstrip(b"\0") == b"mediatek,yft_tiny2c_usb")
    check("GPIO 192 flags 0", (plat / "tiny2c_usb_vdd_1v8").read_bytes() == struct.pack(">III", 0x89, 192, 0))
    check("GPIO 191 flags 0", (plat / "tiny2c_usb_vdd_3v3").read_bytes() == struct.pack(">III", 0x89, 191, 0))
    check("GPIO 149 flags 0", (plat / "tiny2c_usb_vddio_3v3").read_bytes() == struct.pack(">III", 0x89, 149, 0))
    check("5V GPIO absent", not (plat / "tiny2c_usb_vdd_5v").exists())
    check("no platform pinctrl properties", not any(p.name.startswith("pinctrl-") for p in plat.iterdir()))
    check("exact I2C DT path", i2c.is_dir())
    check("exact I2C compatible", (i2c / "compatible").read_bytes().rstrip(b"\0") == b"mediatek,tiny2c_usb")
    check("exact I2C address 0x3c", (i2c / "reg").read_bytes() == struct.pack(">I", 0x3c))

    src = source.read_text()
    on = re.search(r"if \(mode == 1\)(.*?)} else if", src, re.S)
    off = re.search(r"else if \(mode == 0\)(.*?)} else", src, re.S)
    check("store parser and invalid-off behavior", 'int mode = 0;' in src and 'sscanf(buf, "%d", &mode);' in src)
    check("power-on raw order", bool(on and [on.group(1).find(x) for x in ("gpio_io3v3", "gpio_5v", "gpio_3v3", "gpio_1v8", "yft_usb_flag = 1")] == sorted(on.group(1).find(x) for x in ("gpio_io3v3", "gpio_5v", "gpio_3v3", "gpio_1v8", "yft_usb_flag = 1"))))
    check("power-off raw order", bool(off and [off.group(1).find(x) for x in ("gpio_io3v3", "gpio_5v", "gpio_3v3", "gpio_1v8", "yft_usb_flag = 0")] == sorted(off.group(1).find(x) for x in ("gpio_io3v3", "gpio_5v", "gpio_3v3", "gpio_1v8", "yft_usb_flag = 0"))))
    check("unsupported mode returns count", 'pr_info("%s: fail: %d\\n", __func__, mode);' in src and 'return count;' in src)
    check("exact sysfs formats", "gpio_1v8=%d,gpio_3v3=%d,gpio_5v=%d,gpio_io3v3:%d\\n" in src and '"0x%x\\n"' in src)
    check("exact sysfs modes", "DEVICE_ATTR(tiny2c_usb_mode, 0644" in src and "DEVICE_ATTR(sensor_id, 0444" in src)
    check("preferred chip ID and retry timing", "chip_id == 0x4c59" in src and "msleep(400);" in src and "mdelay(10);" in src)
    check("three I2C probe reads", "for (i = 0; i < 3; i++)" in src and "chip_id = tiny2c_usb_read_chipid(client);" in src)
    check("five low-level attempts", "int retry = 5;" in src and "while (retry--)" in src)
    check("no GPIO direction setup", "gpio_direction" not in src and not any("direction" in x for x in ru))
    check("lifecycle quirks preserved", "i2c_unregister_device(client);" in src and "gpio_free" not in src and "i2c_del_driver" not in src)
    check("no PM/shutdown callbacks", ".suspend" not in src and ".resume" not in src and ".shutdown" not in src and ".pm" not in src)
    check("hardware objects resolved", unresolved_hw == 0)

    initrc = repo / "workspace/gq5012bf1/stock/partitions/vendor/etc/init/hw/init.yft.rc"
    cil = repo / "workspace/gq5012bf1/stock/partitions/vendor/etc/selinux/vendor_sepolicy.cil"
    check("init chmod ABI", "chmod 0666 /sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode" in initrc.read_text() and "chmod 0666 /sys/devices/platform/yft_tiny2c_usb/sensor_id" in initrc.read_text())
    check("SELinux mode labels", "/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode" in cil.read_text() and "sysfs_yft_file" in cil.read_text())
    dlp = repo / "workspace/gq5012bf1/stock/partitions/system/app/M170infDlp/M170infDlp.apk"
    fac = repo / "workspace/gq5012bf1/stock/partitions/system/app/FactoryMode/FactoryMode.apk"
    services = repo / "workspace/gq5012bf1/stock/partitions/system/framework/services.jar"
    check("M170infDlp power ABI", text_in_zip(dlp, b"tiny2c_usb_mode") and text_in_zip(dlp, b"tiny2c_mode"))
    check("FactoryMode ID ABI", text_in_zip(fac, b"0x4c59") and text_in_zip(fac, b"/sys/devices/platform/yft_tiny2c_usb/sensor_id"))
    check("ActivityManager crash cleanup ABI", text_in_zip(services, b"com.energy.tc2c") and text_in_zip(services, b"tiny2c_usb_mode") and text_in_zip(services, b"tiny2c_mode"))

    result = (repo / "workspace/phase4-yft-tiny2c-usb/build/build-result.txt").read_text()
    check("clean exact-GKI BUILD_RC", "CLEAN_RC=0" in result and "BUILD_RC=0" in result)
    check("zero compiler warnings", "Compiler warnings=0" in result)
    check("zero modpost warnings", "Modpost warnings=0" in result)
    check("zero unresolved symbols", "Unresolved symbols=0" in result)
    head = cmd("git", "rev-parse", "HEAD", cwd=gki / "common").strip()
    check("pinned common commit", head == COMMON_COMMIT)

    passed = sum(ok for _, ok in checks)
    for name, ok in checks: print(("PASS " if ok else "FAIL ") + name)
    print(f"FUNCTION_PARITY stock={len(sf)} rebuild={len(rf)} shared={len(set(sf)&set(rf))} size_identical={size_same} byte_identical={byte_same} kcfi={kcfi_same}/{len(sf)}")
    print(f"OBJECT_PARITY rows={obj_total} unresolved_hardware={unresolved_hw}")
    print(f"{passed}/{len(checks)} CHECKS PASSED")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"VERIFIER ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
