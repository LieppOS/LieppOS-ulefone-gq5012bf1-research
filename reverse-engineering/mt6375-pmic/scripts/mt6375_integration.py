#!/usr/bin/env python3
"""MT6375 PMIC charger-side modules: static integration checks (offline).

DT / module-alias / load-order / live-binding / provider-and-consumer CRC edges /
YFT hook edges.  One PASS/FAIL line each.   usage: mt6375_integration.py [B1-dir]
"""
import glob
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PK = os.path.normpath(os.path.join(HERE, ".."))
RR = os.path.normpath(os.path.join(PK, "..", ".."))
if not os.path.isdir(os.path.join(RR, "workspace")):
    RR = os.path.join(RR, "ulefone-gq5012bf1-research")
sys.path.insert(0, HERE)
from elfmini import Elf  # noqa: E402

DTS = os.path.join(RR, "workspace/usmart-audit/dt/live-merged.dts")
MODS = os.path.join(RR, "workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules")
VD = os.path.join(RR, "workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules")
LIVE = os.path.join(RR, "workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/buses.txt")
B1 = sys.argv[1] if len(sys.argv) > 1 else "/home/armol/kernel-work/gki-12901745-workspace/lieppos/mt6375-pmic-b1b2/B1"
OURS = ["mt6375", "mt6375-adc", "mt6375-auxadc", "mt6375-charger", "mt6375-battery"]
rd = lambda p: open(p, encoding="utf-8", errors="replace").read()  # noqa: E731
fails = 0


def check(name, ok, detail=""):
    global fails
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {name:72s} {detail}")


def versions(e):
    v = e.secbyname.get("__versions")
    out = {}
    if v:
        for i in range(v.size // 64):
            crc, = struct.unpack_from("<Q", e.blob, v.off + 64 * i)
            out[e.blob[v.off + 64 * i + 8:v.off + 64 * i + 64].split(b"\0")[0].decode()] = crc & 0xffffffff
    return out


def exports(e):
    out = {}
    for ks, kc in (("__ksymtab", "__kcrctab"), ("__ksymtab_gpl", "__kcrctab_gpl")):
        kt, cc = e.secbyname.get(ks), e.secbyname.get(kc)
        if not kt:
            continue
        for r in e.relocs.get(kt.idx, []):
            if r.off % 12 == 0:
                out[e.target(r)[0].name] = struct.unpack_from("<I", e.blob, cc.off + 4 * (r.off // 12))[0] if cc else None
    return out


def modinfo(e):
    s = e.secbyname[".modinfo"]
    return [x.decode() for x in e.blob[s.off:s.off + s.size].split(b"\0") if x]


dts = rd(DTS)
node = dts[dts.index("mt6375@34 {"):]
node = node[:node.index("rt6160@75")]
parent = dts[:dts.index("mt6375@34 {")]
parent = parent[parent.rindex("i2c@"):]
check("DT: mt6375@34 on i2c@11280000, compatible mediatek,mt6375, okay",
      parent.startswith("i2c@11280000") and 'compatible = "mediatek,mt6375";' in node and 'status = "okay"' in node)
check("DT: EINT15 IRQ_TYPE_LEVEL_LOW, interrupt-controller, wakeup-source",
      "interrupts = <0x0f 0x08>" in node and "interrupt-controller;" in node and "wakeup-source;" in node)
comps = re.findall(r'compatible = ([^;]*);', node)
comps = {c for x in comps for c in re.findall(r'"([^"]+)"', x)}

stock = {m: Elf(os.path.join(MODS, m + ".ko")) for m in OURS}
want = {"mt6375": "mediatek,mt6375", "mt6375-adc": "mediatek,mt6375-adc", "mt6375-auxadc": "mediatek,mt6375-auxadc",
        "mt6375-charger": "mediatek,mt6375-chg", "mt6375-battery": "mediatek,mt6375-gauge"}
for m, c in want.items():
    al = [x for x in modinfo(stock[m]) if x.startswith("alias=of:")]
    check(f"{m}: OF alias matches DT child compatible {c}", c in comps and any(("C" + c) in a for a in al))

ml = rd(os.path.join(MODS, "modules.load")).split()
pos = {m: ml.index(m + ".ko") for m in OURS}
check("first-stage modules.load: mt6375 (MFD) before adc/auxadc/charger/battery",
      all(pos["mt6375"] < pos[m] for m in OURS[1:]), str(pos))

live = rd(LIVE)
check("live: 5-0034 bound to i2c driver mt6375",
      re.search(r"===/sys/bus/i2c/devices/5-0034===\n/sys/bus/i2c/drivers/mt6375\n", live) is not None)
tp = rd(os.path.join(os.path.dirname(LIVE), "thermal-power.txt"))
check("live: power_supply battery (mtk-gauge) and primary_chg (chg) under 5-0034",
      "5-0034/11280000.i2c:mt6375@34:mtk-gauge/power_supply/battery" in tp
      and "5-0034/11280000.i2c:mt6375@34:chg/power_supply/primary_chg" in tp)
dm = rd(os.path.join(os.path.dirname(LIVE), "dmesg.txt"))
check("live dmesg: mt6375-chg periodic register dump (CC/AICR/MIVR/IEOC/CV)",
      re.search(r"mt6375-chg 11280000.i2c:mt6375@34:chg.*mt6375_dump_registers CC = \d+mA", dm) is not None)

# CRC edges against every stock module (ramdisk + vendor_dlkm)
allk = {}
for p in glob.glob(os.path.join(MODS, "*.ko")) + glob.glob(os.path.join(VD, "*.ko")):
    allk.setdefault(os.path.basename(p)[:-3], p)
prov = {}
for n, p in allk.items():
    try:
        for s, c in exports(Elf(p)).items():
            prov.setdefault(s, (n, c))
    except Exception:
        pass
for m in OURS:
    rb = Elf(os.path.join(B1, m + ".stripped.ko"))
    v = versions(rb)
    inter = {s: c for s, c in v.items() if s in prov}
    bad = [s for s, c in inter.items() if prov[s][1] != c]
    check(f"{m}: rebuilt intermodule imports match stock provider CRCs",
          not bad, f"{len(inter) - len(bad)}/{len(inter)} via {sorted({prov[s][0] for s in inter})}")

ex = exports(Elf(os.path.join(B1, "mt6375-charger.stripped.ko")))
cons = [n for n, p in allk.items() if "yft_usb_flag" in versions(Elf(p))]
check("yft_usb_flag: rebuilt EXPORT_SYMBOL_GPL CRC = stock = consumer import",
      "yft_usb_flag" in ex and ex["yft_usb_flag"] == exports(stock["mt6375-charger"])["yft_usb_flag"]
      and all(versions(Elf(allk[c]))["yft_usb_flag"] == ex["yft_usb_flag"] for c in cons) and cons, ",".join(cons))
sh = open(os.path.join(MODS, "sh366003_fg.ko"), "rb").read()
src = rd(os.path.join(PK, "source/gq5012bf1-over-alps-5e415e059253.patch"))
check("3rd-gauge proxy: deltas read psy \"3rd-gauge\", registered by sh366003_fg.ko",
      b"3rd-gauge\0" in sh and src.count('power_supply_get_by_name("3rd-gauge")') >= 3)
check("PD notifier: mt6375-charger imports register_tcp_dev_notifier/tcpc_dev_get_by_name from tcpc_class",
      prov.get("register_tcp_dev_notifier", ("",))[0] == "tcpc_class"
      and {"register_tcp_dev_notifier", "tcpc_dev_get_by_name"} <= set(versions(stock["mt6375-charger"])))

print(f"\n{'ALL PASS' if not fails else f'{fails} FAIL'}")
sys.exit(1 if fails else 0)
