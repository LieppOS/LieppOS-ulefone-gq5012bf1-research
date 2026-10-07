#!/usr/bin/env python3
"""fingerprint.ko (YFT fingerprint glue) integration checks — static, offline.

Re-derives the DT / export / consumer / load / live / userspace contract from
files in the research repo and the byte-identical source.  One PASS/FAIL line each.
usage: fp_integration.py   (works from the research repo or a copied status pack)
"""
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

SRC = os.path.join(PK, "source", "fingerprint.c")
DTS = os.path.join(RR, "workspace/usmart-audit/dt/live-merged.dts")
MODS = os.path.join(RR, "workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules")
PART = os.path.join(RR, "workspace/gq5012bf1/stock/partitions")
PROC = os.path.join(RR, "workspace/phase4-tkcore-island/phase3g/device-before/proc-modules.txt")
rd = lambda p: open(p, encoding="utf-8", errors="replace").read()  # noqa: E731
fails = 0


def check(name, ok, detail=""):
    global fails
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {name:70s} {detail}")


c = rd(SRC)
dts = rd(DTS)
node = dts[dts.index("\tyft_finger {"):]
node = node[:node.index("\n\t};")]

# ---- DT
names = re.search(r'pinctrl-names = ([^;]*);', node).group(1)
names = re.findall(r'"([^"]+)"', names)
looked = re.findall(r'pinctrl_lookup_state\(yft_finger_pinctrl,\s*"([^"]+)"\)', c)
check("DT /yft_finger compatible mediatek,yft_finger, status okay",
      'compatible = "mediatek,yft_finger"' in node and 'status = "okay"' in node)
check("DT pinctrl-names: 16 states, all 13 driver lookups present",
      len(names) == 16 and len(looked) == 13 and set(looked) <= set(names),
      f"unused by driver: {sorted(set(names) - set(looked))}")
check("finger_power_en0/1 in DT but never looked up (stock logs 'no need finger_power_en')",
      {"finger_power_en0", "finger_power_en1"} <= set(names) - set(looked)
      and "no need finger_power_en" in c)
check("DT int-gpio GPIO3 / reset-gpio GPIO30 = source of_get_named_gpio names",
      "int-gpio = <0x89 0x03 0x00>" in node and "reset-gpio = <0x89 0x1e 0x00>" in node
      and '"int-gpio"' in c and '"reset-gpio"' in c)
check("DT interrupts <3 1> (EINT3 rising) consumed via irq_of_parse_and_map",
      "interrupts = <0x03 0x01 0x03 0x00>" in node and "irq_of_parse_and_map(node, 0)" in c)

# ---- exports vs consumer
F = Elf(os.path.join(MODS, "fingerprint.ko"))
kt, kc = F.secbyname["__ksymtab"], F.secbyname["__kcrctab"]
ent = {}
for r in F.relocs.get(kt.idx, []):
    if r.off % 12 == 0:
        ent[r.off // 12] = F.target(r)[0].name
exp = {ent[i]: struct.unpack_from("<I", F.blob, kc.off + 4 * i)[0] for i in range(kt.size // 12)}
check("stock exports: 10 EXPORT_SYMBOL", len(exp) == 10 and len(re.findall(r"^EXPORT_SYMBOL\(", c, re.M)) == 10)
M = Elf(os.path.join(MODS, "microarray_fp_tee.ko"))
v = M.secbyname["__versions"]
imp = {}
for i in range(v.size // 64):
    crc, = struct.unpack_from("<Q", M.blob, v.off + 64 * i)
    nm = M.blob[v.off + 64 * i + 8:v.off + 64 * i + 64].split(b"\0")[0].decode()
    if nm in exp:
        imp[nm] = crc
check("microarray_fp_tee imports 4 yft_finger_* symbols, CRCs equal provider",
      len(imp) == 4 and all(exp[k] == imp[k] for k in imp), ",".join(sorted(imp)))

# ---- load / live
ml = rd(os.path.join(MODS, "modules.load")).split()
check("first-stage modules.load: fingerprint.ko before microarray_fp_tee.ko",
      ml.index("fingerprint.ko") < ml.index("microarray_fp_tee.ko"))
pm = rd(PROC)
check("captured /proc/modules: fingerprint Live, used by microarray_fp_tee",
      re.search(r"^fingerprint \d+ 1 microarray_fp_tee, Live", pm, re.M) is not None)

# ---- userspace
bp = rd(os.path.join(PART, "system/build.prop"))
check("system build.prop persist.vendor.fingerprint.chip=microarray_tee_back",
      "persist.vendor.fingerprint.chip=microarray_tee_back" in bp)
yrc = rd(os.path.join(PART, "vendor/etc/init/hw/init.yft.rc"))
check("init.yft.rc tplcd_pattern line is stale: module has no sysfs/attribute code",
      "yft_finger/tplcd_pattern" in yrc and "tplcd" not in c and "sysfs" not in c
      and b"tplcd" not in F.blob)

print(f"\n{'ALL PASS' if not fails else f'{fails} FAIL'}")
sys.exit(1 if fails else 0)
