#!/usr/bin/env python3
"""Fail-closed static verifier for the GQ5012BF1 Hynitron reconstruction."""
from pathlib import Path
import csv, hashlib, re, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "workspace/phase4-hynitron"
K = ROOT / "kernel"
checks = []

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ok(name, cond, detail=""):
    if not cond:
        raise AssertionError(f"FAIL {name}: {detail}")
    checks.append(name)
def tsv(path, key):
    return {r[key]: r for r in csv.DictReader(open(path), delimiter="\t")}
def modversions(path):
    out = subprocess.check_output(["modprobe", "--dump-modversions", str(path)], text=True)
    d = {}
    for line in out.splitlines():
        if "\t" in line:
            crc, sym = line.split("\t", 1); d[sym] = crc.lower()
    return d

def main():
    stock=P/"oracle/hynitron.stock.ko"; rebuild=P/"rebuild/hynitron.ko"; src=P/"reconstruction-source/hynitron.c"
    ok("frozen stock SHA", sha(stock)=="860f28409fdd59458640cd067fec6eb83f3e5ec00ca12782c0e152323a351fb6")
    ok("reconstruction source SHA", sha(src)=="c7ba141d7951252b907aa36494b9e49c39cd22086513aa957d6418a71c68c8d1")
    sf=tsv(K/"phase4-hynitron-functions.tsv","function"); rf=tsv(P/"rebuild/inventory/rebuild-functions.tsv","function")
    ok("function count",len(sf)==len(rf)==65)
    ok("function set",set(sf)==set(rf))
    kcfi_na={"hyn_find_fw_idx","hyn_check_gesture"}
    ok("KCFI applicable parity",all(sf[n]["kcfi_id"]==rf[n]["kcfi_id"] for n in sf if n not in kcfi_na))
    si=tsv(K/"phase4-hynitron-imports.tsv","symbol");ri=tsv(P/"rebuild/inventory/rebuild-imports.tsv","symbol")
    ok("54-import set",len(si)==len(ri)==54 and set(si)==set(ri))
    ok("MODVERSION map",all(si[n]["crc"].lower()==ri[n]["crc"].lower() for n in si))
    yft={"second_touch_fw_version":"0x7198d58d","yft_touchpanel_device_add":"0xf5ba4446","yft_set_touch_device_used":"0x0a0f3b69"}
    ok("three stock yft edges",all(ri[n]["crc"].lower()==c for n,c in yft.items()))
    se=tsv(K/"phase4-hynitron-exports.tsv","symbol");rexp=tsv(P/"rebuild/inventory/rebuild-exports.tsv","symbol")
    expected={"tiny_tp_gesture_contorl":"0x4e4b7919","tiny_tp_power_contorl":"0xfcc94fc7"}
    ok("two export names",set(se)==set(rexp)==set(expected))
    ok("natural export CRCs",all(rexp[n]["crc"].lower()==c for n,c in expected.items()))
    ok("export KCFI",all(rexp[n]["kcfi_id"].lower()=="0x019c0cac" for n in expected))
    cv=modversions(P/"oracle/spi_tiny_co5300_lcd.ko")
    ok("stock consumer compatibility",all(cv.get(n)==c for n,c in expected.items()))
    text=src.read_text()
    ok("module identity",all(x in text for x in ['HYN_NAME "hyn_ts"','MODULE_DESCRIPTION("Hynitron Touchscreen Driver")','MODULE_AUTHOR("Hynitron Driver Team")','MODULE_LICENSE("GPL v2")']))
    ok("OF compatible",'HYN_COMPAT "hynitron,hyn_ts"' in text)
    dt=(K/"phase4-hynitron-dt-contract.md").read_text()
    ok("I2C bus/address",'I2C0/0x15' in dt or ('i2c@11c20000' in dt and 'reg = <0x15>' in dt))
    ok("GPIO mapping",all(x in dt for x in ['GPIO 11','GPIO 32','GPIO 119']))
    ok("IRQ behavior",'IRQF_TRIGGER_FALLING | IRQF_ONESHOT' in text and 'request_threaded_irq' in text)
    ok("controller identity",all(x in text for x in ['chip_type = 0x00b7','hyn_i2c_write_bytes(0xa001','hyn_i2c_read_bytes(0xa003','cmd != 0x55']) and 'CST820' in (K/"phase4-hynitron-controller-identity.md").read_text())
    ok("touch decode",all(x in text for x in ['b[1] & 0x0f','(b[2] & 0xf) << 8','b[4] >> 4','(b[4] & 0xf) << 8']))
    ok("input ABI",all(x in text for x in ['ABS_MT_TRACKING_ID','ABS_MT_POSITION_X','ABS_MT_POSITION_Y','ABS_MT_TOUCH_MAJOR','ABS_MT_WIDTH_MAJOR','BTN_TOUCH']))
    ok("gesture state machine",all(x in text for x in ['CST_REG_GESTURE 0xd3','CST_REG_GESTURE_ENABLE 0xec','hyn_gesture_suspend','irq_set_irq_wake']))
    ok("power export state machine",all(x in text for x in ['tiny_tp_power_contorl','CST_REG_DEEP_SLEEP 0xe5','hyn_release_all_finger']))
    ok("YFT semantics",all(x in text for x in ['yft_touchpanel_device_add(&hynitron_i2c_driver, 0)','yft_set_touch_device_used(HYN_NAME, 1)','Vno: %x. %x. %x. %x.']))
    fw1=P/"firmware/cst8xx_fw.bin";fw2=P/"firmware/cst816t_fw.bin"
    ok("firmware image 1",len(fw1.read_bytes())==15419 and sha(fw1)=="0566ea7799d6f8bbce026639d9dbb89f0e629ab533d1d90e4901c81d5611e1d8")
    ok("firmware image 2",len(fw2.read_bytes())==15410 and sha(fw2)=="0d02fde67223c1e7aa6c4ce1d1e522bcbe79d4d58decf1aa79b865cb2e504de3")
    def incbytes(name): return bytes(int(x,16) for x in re.findall(r"0x([0-9a-fA-F]{2})",(P/f"reconstruction-source/{name}").read_text()))
    ok("embedded firmware parity",incbytes("firmware_cst8xx.inc")==fw1.read_bytes() and incbytes("firmware_cst816t.inc")==fw2.read_bytes())
    ok("update selection",all(x in text for x in ['hyn_find_fw_idx(1)','hyn_find_fw_idx(0)','selected_fw']))
    ok("programming gate default off",'#define HYNITRON_ALLOW_FW_PROGRAMMING 0' in text and '-DHYNITRON_ALLOW_FW_PROGRAMMING=0' in (P/"reconstruction-source/Makefile").read_text())
    ok("no invented programmer",'return -ENOSYS;' in text and not re.search(r'\b(?:flash_erase|program_block|write_flash)\s*\(', text))
    ok("userspace ABI",all(x in text for x in ['hyntpfwver','hynfwupdate','hyntprwreg','hynfwupgradeapp','hyntpfactorytest','hyn_gesture_mode','hyn_gesture_buf']))
    ok("PM export coordination",'.pm = NULL' in text and 'tiny_tpgesture_status' in text)
    ok("lifecycle",all(x in text for x in ['module_init','module_exit','hyn_remove','free_irq','flush_workqueue']))
    log=(P/"rebuild/build.log").read_text(errors="replace")
    ok("clean exact-GKI build",sha(rebuild)=="26522dc090fc6a57cf45ed841755a8ef267c83f43f511433439f1392e2ba438a" and 'Build completed successfully' in log and not re.search(r'(^|\s)warning:',log,re.I|re.M))
    ok("no unresolved symbols",set(si)==set(ri))
    print(f"{len(checks)}/{len(checks)} CHECKS PASSED")

if __name__ == "__main__":
    try: main()
    except Exception as e:
        print(e,file=sys.stderr);sys.exit(1)
