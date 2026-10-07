#!/usr/bin/env python3
"""microarray_fp_tee.ko integration checks (static, offline).

Re-derives the DT / provider / live-binding / userspace contract from files in
the research repo and the byte-identical source.  One PASS/FAIL line each.
usage: mafp_integration.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PK = os.path.normpath(os.path.join(HERE, ".."))
RR = os.path.normpath(os.path.join(PK, "..", ".."))
SRC = os.path.join(PK, "source")
DTS = os.path.join(RR, "workspace/usmart-audit/dt/live-merged.dts")
LIVE = os.path.join(RR, "workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649")
PART = os.path.join(RR, "workspace/gq5012bf1/stock/partitions")
MODS = os.path.join(RR, "workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules")
rd = lambda p: open(p, encoding="utf-8", errors="replace").read()  # noqa: E731
fails = 0


def check(name, ok, detail=""):
    global fails
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {name:66s} {detail}")


c = rd(os.path.join(SRC, "madev.c"))
s = rd(os.path.join(SRC, "mtk-settings.c"))
dts = rd(DTS)

# ---- DT
spi = dts[:dts.index('compatible = "mediatek,madev_finger"')]
spi = spi[spi.rindex("spi1@"):]
check("DT: madev_finger@0 under spi1@11011000, controller tee-only",
      spi.startswith("spi1@11011000") and "tee-only;" in spi)
fp = dts[dts.index('compatible = "mediatek,madev_finger"') - 200:dts.index('compatible = "mediatek,madev_finger"') + 200]
check("DT: spi-max-frequency 8 MHz, vfp-supply present", "spi-max-frequency = <0x7a1200>" in fp and "vfp-supply" in fp,
      "driver overrides to 6 MHz")
check("source: spi->max_speed_hz = 6 MHz, regulator 'vfp' 2.8 V",
      "#define SPI_SPEED\t(6*1000000)" in rd(os.path.join(SRC, "madev.h")) and 'regulator_get(dev, "vfp")' in s
      and "2800000, 2800000" in s)
ph = re.search(r"vfp-supply = <(0x[0-9a-f]+)>", fp).group(1)
pos = dts.index(f"phandle = <{ph}>;")
node = dts[dts.rindex("{", 0, pos) - 80:pos]
node = node[node.rindex("\n", 0, node.rindex("{")):]
check("DT: vfp-supply phandle resolves to mt6369_vfp ('mt6377_ldo' in logs is a stale ODM label)",
      'regulator-name = "mt6369_vfp"' in node, f"phandle {ph}")
yft = dts[dts.index("yft_finger {"):]
yft = yft[:yft.index("\n\t};")]
check("DT: yft_finger has interrupts <3 1> (EINT3 rising), int-gpio GPIO3, reset-gpio GPIO30",
      "interrupts = <0x03 0x01 0x03 0x00>" in yft and "int-gpio = <0x89 0x03 0x00>" in yft
      and "reset-gpio = <0x89 0x1e 0x00>" in yft)
check("source: IRQ from of_find_compatible_node('mediatek,yft_finger'), IRQF_TRIGGER_RISING",
      'MA_EINT_DTS_NAME\t"mediatek,yft_finger"' in rd(os.path.join(SRC, "mtk-settings.h"))
      and "IRQF_TRIGGER_RISING, tname" in c)

# ---- providers
mi = open(os.path.join(MODS, "microarray_fp_tee.ko"), "rb").read()
check("stock depends=fingerprint,spi-mt65xx,tkcore", b"depends=fingerprint,spi-mt65xx,tkcore\0" in mi)
crc = rd(os.path.join(PK, "evidence/tkcore-provider-crc.txt"))
check("tee_spi_transfer CRC 0x184ce7da from the public TrustKernel core/ = stock import",
      "imports tee_spi_transfer 0x184ce7da; natural provider 0x184ce7da: MATCH" in crc)
ml = rd(os.path.join(MODS, "modules.load"))
order = [m for m in ("tkcore.ko", "fingerprint.ko", "spi-mt65xx.ko", "microarray_fp_tee.ko") if m in ml]
check("first-stage modules.load lists tkcore, fingerprint, spi-mt65xx before microarray_fp_tee",
      len(order) == 4 and ml.index("microarray_fp_tee.ko") > max(ml.index(m) for m in order[:-1]))

# ---- live
bus = rd(os.path.join(LIVE, "buses.txt"))
blk = bus.split("===/sys/bus/spi/devices/spi1.0===")[1].split("===")[0]
check("live: spi1.0 bound to driver madev (module microarray_fp_tee)",
      "/drivers/madev" in blk and "microarray_fp_tee" in blk)
fpl = rd(os.path.join(LIVE, "fingerprint.txt"))
check("live: /dev/madev0 char 498:0, 0666 system, mafinger_device",
      re.search(r"crw-rw-rw- 1 system system u:object_r:mafinger_device:s0\s+498,\s+0 .*/dev/madev0", fpl) is not None)

# ---- userspace (static)
rc = rd(os.path.join(PART, "vendor/etc/init/hw/init.fingerprint.rc")) if os.path.exists(
    os.path.join(PART, "vendor/etc/init/hw/init.fingerprint.rc")) else ""
check("vendor init.fingerprint.rc sets /dev/madev0 permissions", "/dev/madev0" in rc)
ta = os.path.exists(os.path.join(PART, "vendor/app/t6/edcf9395-3518-9067-614cafae2909775b.ta"))
check("MicroArray TA edcf9395-3518-9067-614cafae2909775b.ta shipped in vendor/app/t6", ta)

# ---- the 80-byte blob is legacy MediaTek mt_chip_conf (donor v4.0.06)
check("smt_conf = struct mt_chip_conf (20 x u32 = 80 B), v4.0.06 TRUSTKERNEL path",
      "sizeof(struct mt_chip_conf)" in c and ".finish_intr = FINISH_INTR_EN" in c and ".high_time = 10" in c)

print(f"\n{'ALL PASS' if not fails else f'{fails} FAIL'}")
sys.exit(1 if fails else 0)
