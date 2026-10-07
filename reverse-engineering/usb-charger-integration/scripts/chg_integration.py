#!/usr/bin/env python3
"""Charger framework / type-detect integration checks (offline). One PASS/FAIL line each."""
import os, re, struct, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); PK = os.path.normpath(os.path.join(HERE, ".."))
RR = os.path.normpath(os.path.join(PK, "..", ".."))
if not os.path.isdir(os.path.join(RR, "workspace")): RR = os.path.join(RR, "ulefone-gq5012bf1-research")
sys.path.insert(0, HERE); from elfmini import Elf
W = os.path.join(RR, "workspace"); rd = lambda p: open(p, encoding="utf-8", errors="replace").read()
dts = rd(os.path.join(W, "usmart-audit/dt/live-merged.dts"))
MODS = os.path.join(W, "gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules")
VD = os.path.join(W, "gq5012bf1/stock/partitions/vendor_dlkm/lib/modules")
tp = rd(os.path.join(W, "gq5012bf1/snapshots/live-stock-adb-20260831-115649/thermal-power.txt"))
fails = 0
def check(n, ok, d=""):
    global fails; fails += not ok; print(f"{'PASS' if ok else 'FAIL'}  {n:72s} {d}")
def exports(e):
    out = {}
    for ks, kc in (("__ksymtab", "__kcrctab"), ("__ksymtab_gpl", "__kcrctab_gpl")):
        kt, cc = e.secbyname.get(ks), e.secbyname.get(kc)
        if not kt: continue
        for r in e.relocs.get(kt.idx, []):
            if r.off % 12 == 0: out[e.target(r)[0].name] = struct.unpack_from("<I", e.blob, cc.off + 4 * (r.off // 12))[0]
    return out
def versions(e):
    v = e.secbyname.get("__versions"); out = {}
    if v:
        for i in range(v.size // 64):
            out[e.blob[v.off+64*i+8:v.off+64*i+64].split(b"\0")[0].decode()] = struct.unpack_from("<Q", e.blob, v.off+64*i)[0] & 0xffffffff
    return out
check("DT: /charger compatible mediatek,charger and /mtk-ctd compatible mediatek,mtk_ctd",
      'compatible = "mediatek,charger";' in dts and 'compatible = "mediatek,mtk_ctd";' in dts)
fw = Elf(os.path.join(MODS, "mtk_charger_framework.ko")); ex = exports(fw)
check("framework exports yft_cam_open_flag/yft_long_charger_flag (GPL) + 2 others", {"yft_cam_open_flag", "yft_long_charger_flag", "chr_get_debug_level", "mtk_chg_enable_vbus_ovp"} <= set(ex))
allk = glob.glob(os.path.join(MODS, "*.ko")) + glob.glob(os.path.join(VD, "*.ko"))
for sym in ("yft_cam_open_flag", "yft_long_charger_flag"):
    cons = [os.path.basename(k)[:-3] for k in allk if sym in versions(Elf(k))]
    check(f"{sym}: every stock consumer CRC equals provider", all(versions(Elf(k)).get(sym, ex[sym]) == ex[sym] for k in allk), ",".join(cons) or "(no module consumer)")
cc = exports(Elf(os.path.join(MODS, "charger_class.ko")))
bad = [(os.path.basename(k), s) for k in allk for s, c in versions(Elf(k)).items() if s in cc and cc[s] != c]
check("charger_class: all stock consumer import CRCs equal its exports (incl. charger_dev_is_otg_enabled)", not bad and "charger_dev_is_otg_enabled" in cc, f"{len(cc)} exports")
check("live: mtk-master-charger psy present with PD/PD_PPS usb types", "POWER_SUPPLY_USB_TYPE=[Unknown] SDP DCP CDP PD PD_PPS" in tp)
ml = rd(os.path.join(MODS, "modules.load")).split()
check("load order: charger_class < mtk_chg_type_det, charger_class < mtk_charger_framework",
      ml.index("charger_class.ko") < ml.index("mtk_chg_type_det.ko") and ml.index("charger_class.ko") < ml.index("mtk_charger_framework.ko"))
print(f"\n{'ALL PASS' if not fails else f'{fails} FAIL'}"); sys.exit(1 if fails else 0)
