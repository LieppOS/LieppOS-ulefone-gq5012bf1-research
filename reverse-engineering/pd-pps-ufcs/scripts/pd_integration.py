#!/usr/bin/env python3
"""PD/PPS/UFCS static integration checks (offline). One PASS/FAIL line each."""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PK = os.path.normpath(os.path.join(HERE, ".."))
RR = os.path.normpath(os.path.join(PK, "..", ".."))
if not os.path.isdir(os.path.join(RR, "workspace")): RR = os.path.join(RR, "ulefone-gq5012bf1-research")
W = os.path.join(RR, "workspace"); rd = lambda p: open(p, encoding="utf-8", errors="replace").read()
dts = rd(os.path.join(W, "usmart-audit/dt/live-merged.dts"))
MODS = os.path.join(W, "gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules")
VD = os.path.join(W, "gq5012bf1/stock/partitions/vendor_dlkm/lib/modules")
tp = rd(os.path.join(W, "gq5012bf1/snapshots/live-stock-adb-20260831-115649/thermal-power.txt"))
fails = 0
def check(n, ok, d=""):
    global fails; fails += not ok; print(f"{'PASS' if ok else 'FAIL'}  {n:72s} {d}")
check("DT: every support-ta list is exactly pca_ta_pps + pd_adapter (3 nodes incl. /pe5)",
      dts.count('support-ta = "pca_ta_pps", "pd_adapter";') == 3 and len(re.findall(r"support-ta =", dts)) == 3)
check("DT: /pe5 compatible mediatek,charger,pe5 and /pd-adapter adapter-name pd_adapter",
      'compatible = "mediatek,charger,pe5";' in dts and 'adapter-name = "pd_adapter";' in dts)
check("DT: no UFCS node/property anywhere", "ufcs" not in dts.lower())
ko = glob.glob(os.path.join(MODS, "*.ko")) + glob.glob(os.path.join(VD, "*.ko"))
check("stock module sets: no *ufcs* module shipped (mtk_ufcs_adapter built by ALPS Makefile, not shipped)",
      not [k for k in ko if "ufcs" in os.path.basename(k)])
ml = rd(os.path.join(MODS, "modules.load")).split()
need = ["adapter_class.ko", "mtk_pd_adapter.ko", "mtk_charger_algorithm_class.ko", "mtk_pd_charging.ko", "mtk_pep.ko", "mtk_pep40.ko", "mtk_pep50.ko"]
present = [m for m in need if m in ml]
check("first-stage modules.load ships the PD/PPS policy modules", len(present) >= 5, f"{present}")
check("live: mtk-master-charger USB types = Unknown SDP DCP CDP PD PD_PPS (no UFCS)",
      "POWER_SUPPLY_USB_TYPE=[Unknown] SDP DCP CDP PD PD_PPS" in tp and "UFCS" not in tp)
print(f"\n{'ALL PASS' if not fails else f'{fails} FAIL'}"); sys.exit(1 if fails else 0)
