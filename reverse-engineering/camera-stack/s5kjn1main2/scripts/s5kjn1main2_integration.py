#!/usr/bin/env python3
"""S5KJN1MAIN2 integration / reachability checks (static, offline).

Every claim is re-derived from files in the research repo / workspace:
the parity-proven TU source + stock data header, the parity-proven imgsensor
framework source, the stock live DT, the live stock ADB capture and the DONE
CAMERA-EEPROMS layout source.  Prints one PASS/FAIL line per check.

usage: s5kjn1main2_integration.py   (run from anywhere)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CS = os.path.normpath(os.path.join(HERE, "..", ".."))           # camera-stack
RR = os.path.normpath(os.path.join(CS, "..", ".."))             # research repo
WS = os.path.normpath(os.path.join(RR, ".."))                   # workspace
SRC = os.path.join(CS, "reconstruction/imgsensor/src")
TU = os.path.join(SRC, "common/s5kjn1main2_mipi_raw")
LIVE = os.path.join(RR, "workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649")
DTS = os.path.join(RR, "workspace/usmart-audit/dt/live-merged.dts")
EEP = os.path.join(WS, "Reverse Engineer - DONE/CAMERA-EEPROMS/source/mtkcam/cam_cal/src_v4l2/custom/layout/"
                       "s5kjn1main2_cust_eeprom.c")

rd = lambda p: open(p, encoding="utf-8", errors="replace").read()  # noqa: E731
fails = 0


def check(name, ok, detail):
    global fails
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {name:58s} {detail}")


c = rd(os.path.join(TU, "s5kjn1main2mipiraw_Sensor.c"))
d = rd(os.path.join(TU, "s5kjn1main2_stock_data.h"))
sc = d[d.index("static const struct subdrv_static_ctx static_ctx"):]
sc = sc[:sc.index("\n};")]
fld = lambda k: re.search(r"\." + k + r"\s*=\s*([^,\n]+)", sc)  # noqa: E731

# ---- identity / probe
check("static_ctx.sensor_id = 0x38E2", int(fld("sensor_id").group(1)) == 0x38E2, fld("sensor_id").group(1))
check("i2c_addr_table = {0x5A, end} (7-bit 0x2D)", re.search(r"i2c_addr_table = \{90, 255\}", sc) is not None,
      "write-ID 0x5A")
check("probe: low byte +1 (pseudo-ID) in both byte orders",
      c.count("subdrv_i2c_rd_u8(ctx, addr_l) + 1") == 1 and c.count("subdrv_i2c_rd_u8(ctx, addr_h) + 1") == 1,
      "0x38E1 die -> 0x38E2")
check("probe: binds only when !is_yft_cts_board()", c.count("!is_yft_cts_board()") == 2, "CTS gate")
check("output format 35 = RAW_4CELL_BAYER_Gr (tetra-cell)", fld("sensor_output_dataformat").group(1) == "35",
      "kd_imgsensor_define_v4l2.h enum index 35")

# ---- calibration paths
ei = d[d.index("static struct eeprom_info_struct eeprom_info"):]
ei = ei[:ei.index("};\n")]
check("eeprom_info: header 0x77006901, no *_support flag set",
      "1996515585" in ei and "support" not in ei, "qsc_support=0 -> QSC never preloaded or written")
fw = rd(os.path.join(SRC, "adaptor-subdrv-ctrl.c"))
callers = [m.start() for m in re.finditer(r"s_ctx\.s_cali\(", fw)]
fn_of = lambda pos: re.findall(r"\n(?:static )?\w[\w\s\*]*?(\w+)\(struct subdrv_ctx \*ctx[^)]*\)\n\{", fw[:pos])[-1]  # noqa
check("s_cali (set_sensor_cali) called only from common_open",
      [fn_of(p) for p in callers] == ["common_open"], f"callers={[fn_of(p) for p in callers]}")
check("TU ops.open is its own open() (never calls s_cali)",
      re.search(r"\.open = open,", d) is not None and "s_cali" not in c[c.index("static int open("):
                                                                       c.index("static int vsync_notify(")],
      "set_sensor_cali unreachable")
modes = d[d.index("mode_struct"):]
check("no mode has a seamless_switch_group", "seamless_switch_group" not in modes,
      "seamless_switch always returns 'not supported'")
check("feature list: GET_4CELL_DATA -> read_4cell_from_eeprom",
      re.search(r"SENSOR_FEATURE_GET_4CELL_DATA,\s*\.func = read_4cell_from_eeprom", d) is not None, "")
check("4-cell read: EEPROM 0xA0>>1 on the sensor's own adapter",
      c.count("adaptor_i2c_rd_p8(ctx->i2c_client, EEPROM_READ_ID >> 1") == 4, "i2c-2 0x50 = 2-0050")
regions = [(0x0D4F, 3502), (0x1AFD, 768), (0x1DFD, 4000), (0x2D9D, 626)]
check("4-cell regions end at QSC base 0x300F, inside 0x4000",
      regions[-1][0] + regions[-1][1] == 0x300F and "0x300f" in ei, "0x0D4F..0x300F")

# ---- stock defect: user-sized buffer, fixed-size copy
io = rd(os.path.join(SRC, "adaptor-ioctl.c"))
g4 = io[io.index("static int g_4cell_data"):]
g4 = g4[:g4.index("\n}\n")]
check("DEFECT: g_4cell_data kmallocs user-chosen info->size",
      "workbuf_get(&workbuf, info->p_buf, info->size" in g4 and "kmalloc(size, GFP_KERNEL)" in io, "")
check("DEFECT: read_4cell memcpys FOUR_CELL_SIZE+2 (9492) unconditionally",
      "memcpy(data, Four_Cell_Array, FOUR_CELL_SIZE + 2);" in c, "heap overflow if info->size < 9492")
check("DEFECT: EEPROM read results ignored, cache latched",
      "Is_Read_4Cell = 1;" in c and c.count("\t\tadaptor_i2c_rd_p8(") == 4, "partial read cached until reboot")

# ---- framework hooks specific to this slot
ac = rd(os.path.join(SRC, "adaptor-ctrls.c"))
check("only slot-specific framework hook is idx 4 (night LED)",
      re.findall(r"ctx->idx == (\d+)", ac + fw + rd(os.path.join(SRC, "adaptor-drv.c"))) == ["4"],
      "sensor2 has none")

# ---- DT / live binding
dts = rd(DTS)
node = dts[dts.index("sensor2@10 {"):]
node = node[:node.index("port {")]
check("DT sensor2: sensor-names s5kjn1main2, no reindex-to",
      '"s5kjn1main2_mipi_raw"' in node and "reindex" not in node, "idx = 2")
check("DT sensor2 LDO channels dvdd1 avdd4 afvdd6 dovdd7 + avdd1-supply",
      all(x in node for x in ("custom_dvdd = <0x01>", "custom_avdd = <0x04>", "custom_afvdd = <0x06>",
                              "custom_dovdd = <0x07>", "avdd1-supply")), "")
bus = rd(os.path.join(LIVE, "buses.txt"))
blk = lambda dev: bus.split(f"===/sys/bus/i2c/devices/{dev}===")[1].split("===")[0]  # noqa: E731
check("live: 2-0010 bound to imgsensor (of:Nsensor2)",
      "/drivers/imgsensor" in blk("2-0010") and "Nsensor2T" in blk("2-0010"), "")
check("live: 2-0050 bound to camera_eeprom", "camera_eeprom" in blk("2-0050"), "")
check("live: 2-000d bound to main4_vcm (DT placeholder; wire 0x0C)", "main4_vcm" in blk("2-000d"), "")
media = rd(os.path.join(LIVE, "camera-media.txt"))
check("HAL: [02] BACK SENSOR_DRVNAME_S5KJN1MAIN2_MIPI_RAW",
      re.search(r"\[02\] -> .*BACK .*SENSOR_DRVNAME_S5KJN1MAIN2_MIPI_RAW", media) is not None, "chip-ID matched")

# ---- EEPROM layout owner (CAMERA-EEPROMS, DONE)
e = rd(EEP)
check("cam_cal layout: sensor 0x38E2, 0xA0, header 0x77006901, 0x4000",
      all(x in e for x in (".sensor_id = 0x38E2", ".i2c_write_id = 0xA0", "0x77006901", ".max_size = 0x4000")), "")

print(f"\n{'ALL PASS' if not fails else f'{fails} FAIL'}")
sys.exit(1 if fails else 0)
