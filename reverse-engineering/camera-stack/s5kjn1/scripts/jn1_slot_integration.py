#!/usr/bin/env python3
"""Camera-1 slot (DT sensor1: s5kjn1 / ov32b40 / s5kjn1cts) integration checks.

Static, offline. Every line is re-derived from the parity-proven TU sources and
stock-data headers, the parity-proven imgsensor framework, the stock live DT,
the live stock ADB capture, the stock vendor partition and the DONE
CAMERA-EEPROMS layout source.

usage: jn1_slot_integration.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CS = os.path.normpath(os.path.join(HERE, "..", ".."))
RR = os.path.normpath(os.path.join(CS, "..", ".."))
WS = os.path.normpath(os.path.join(RR, ".."))
SRC = os.path.join(CS, "reconstruction/imgsensor/src")
COM = os.path.join(SRC, "common")
LIVE = os.path.join(RR, "workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649")
DTS = os.path.join(RR, "workspace/usmart-audit/dt/live-merged.dts")
VEND = os.path.join(RR, "workspace/gq5012bf1/stock/partitions/vendor/lib64/mt6878")
EEP = os.path.join(WS, "Reverse Engineer - DONE/CAMERA-EEPROMS/source/mtkcam/cam_cal/src_v4l2/custom/layout/"
                       "s5kjn1_cust_eeprom.c")

rd = lambda p: open(p, encoding="utf-8", errors="replace").read()  # noqa: E731
fails = 0


def check(name, ok, detail=""):
    global fails
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {name:64s} {detail}")


def tu(name):
    c = rd(os.path.join(COM, f"{name}_mipi_raw/{name}mipiraw_Sensor.c"))
    d = rd(os.path.join(COM, f"{name}_mipi_raw/{name}_stock_data.h"))
    sc = d[d.index("static const struct subdrv_static_ctx static_ctx"):]
    return c, d, sc[:sc.index("\n};")]


jc, jd, js = tu("s5kjn1")
cc, cd, cs = tu("s5kjn1cts")
oc, od, os_ = tu("ov32b40")
fld = lambda sc, k: (re.search(r"\." + k + r"\s*=\s*([^,\n]+)", sc) or [None, None])[1]  # noqa: E731

# ---- slot composition / probe order
dts = rd(DTS)
node = dts[dts.index("sensor1@10 {"):]
node = node[:node.index("port {")]
check("DT sensor1 sensor-names order: s5kjn1, ov32b40, s5kjn1cts",
      'sensor-names = "s5kjn1_mipi_raw", "ov32b40_mipi_raw", "s5kjn1cts_mipi_raw"' in node, "probe order")
check("DT sensor1: no reindex-to; dvdd1 avdd4 dovdd7 + avdd1-supply; no afvdd",
      "reindex" not in node and all(x in node for x in ("custom_dvdd = <0x01>", "custom_avdd = <0x04>",
                                                        "custom_dovdd = <0x07>", "avdd1-supply"))
      and "custom_afvdd" not in node, "idx = 1, fixed focus")
drv = rd(os.path.join(SRC, "adaptor-drv.c"))
loop = drv[drv.index("for (i = 0; i < subdrvs_cnt; i++) {"):]
check("search_sensor stops at the first sub-driver whose get_id succeeds",
      re.search(r"ret = subdrv_call\(ctx, get_id, &sensor_id\);.*?if \(!ret\) \{.*?return 0;", loop, re.S)
      is not None, "later names are never probed once one binds")

# ---- identities and CTS gate
check("s5kjn1: sensor_id 0x38E1, write-ID 0x7A (7-bit 0x3D)",
      fld(js, "sensor_id") == "14561" and "i2c_addr_table = {122, 255}" in js)
check("s5kjn1: binds only if !is_yft_cts_board()", jc.count("!is_yft_cts_board()") == 2
      and "|| is_yft_cts_board())" in jc)
check("s5kjn1cts: sensor_id 0x38E0 = die-1, binds only if is_yft_cts_board()==1",
      fld(cs, "sensor_id") == "14560" and cc.count("is_yft_cts_board() == 1") == 2 and ") - 1;" in cc)
check("ov32b40: 0x563242 via regs 0x300A-C, write-ID 0x6C, common_get_imgsensor_id (no CTS gate)",
      fld(os_, "sensor_id") == "5648962" and "i2c_addr_table = {108, 255}" in os_
      and ".get_id = common_get_imgsensor_id" in od and "is_yft_cts_board" not in oc)
mc = rd(os.path.join(COM, "s5kjn1main2_mipi_raw/s5kjn1main2mipiraw_Sensor.c"))
check("is_yft_cts_board()==0 on this unit (s5kjn1 + s5kjn1main2 bound, both need !cts)",
      "!is_yft_cts_board()" in mc and "!is_yft_cts_board()" in jc, "=> s5kjn1cts can never bind here")

# ---- live
bus = rd(os.path.join(LIVE, "buses.txt"))
blk = lambda dev: bus.split(f"===/sys/bus/i2c/devices/{dev}===")[1].split("===")[0]  # noqa: E731
check("live: 4-0010 bound to imgsensor (of:Nsensor1)",
      "/drivers/imgsensor" in blk("4-0010") and "Nsensor1T" in blk("4-0010"))
check("live: 4-0050 bound to camera_eeprom", "camera_eeprom" in blk("4-0050"))
media = rd(os.path.join(LIVE, "camera-media.txt"))
check("HAL: [01] FRONT SENSOR_DRVNAME_S5KJN1_MIPI_RAW (=> s5kjn1 matched first)",
      re.search(r"\[01\] -> .*FRONT .*SENSOR_DRVNAME_S5KJN1_MIPI_RAW", media) is not None,
      "ov32b40 / s5kjn1cts never probed")

# ---- s5kjn1 behaviour
check("s5kjn1: output format 35 RAW_4CELL_BAYER_Gr; no PDAF, no eeprom_info",
      fld(js, "sensor_output_dataformat") == "35" and "pdaf_type" not in js and "eeprom_info" not in jd
      and "pdaf_cap" not in jd)
check("s5kjn1: no reg_addr_stream; SUSPEND/RESUME -> custom 0x0100 + 10 ms",
      "reg_addr_stream" not in js and "subdrv_i2c_wr_u8(ctx, 0x0100, enable);" in jc
      and re.search(r"SET_STREAMING_SUSPEND,\s*\.func = streaming_control_off", jd)
      and re.search(r"SET_STREAMING_RESUME,\s*\.func = streaming_control_on", jd))
fw = rd(os.path.join(SRC, "adaptor-subdrv-ctrl.c"))
check("QUIRK: close = common_close -> streaming_control(FALSE) -> wr_u8(reg_addr_stream=0x0000, 0)",
      ".close = common_close" in jd and "subdrv_i2c_wr_u8(ctx, ctx->s_ctx.reg_addr_stream, 0x00);" in fw
      and re.search(r"int common_close\(struct subdrv_ctx \*ctx\)\n\{\n\tstreaming_control\(ctx, FALSE\);", fw)
      is not None, "stream-off on close lands on chip-ID reg, not 0x0100")
check("s5kjn1: 4-cell read via sensor adapter (i2c-4) EEPROM 0x50, 4 windows",
      jc.count("adaptor_i2c_rd_p8(ctx->i2c_client, EEPROM_READ_ID >> 1") == 4 and "#define EEPROM_READ_ID\t\t0xA0" in jc,
      "4-0050")
check("DEFECT (shared with s5kjn1main2): fixed 9492 B copy into user-sized buffer",
      "memcpy(data, Four_Cell_Array, FOUR_CELL_SIZE + 2);" in jc
      and "workbuf_get(&workbuf, info->p_buf, info->size" in rd(os.path.join(SRC, "adaptor-ioctl.c")))
check("s5kjn1: seamless switch inert (no seamless_switch_group)",
      "seamless_switch_group" not in jd[jd.index("mode_struct"):])
check("s5kjn1/s5kjn1cts: hs/slim carry IMX989 placeholder pclk 4390400000/4352000000",
      all(x in d for d in (jd, cd) for x in ("4390400000", "4352000000")))
e = rd(EEP)
check("cam_cal layout s5kjn1: sensor 0x38E1, 0xA0, header 0x77006901",
      all(x in e for x in (".sensor_id = 0x38E1", ".i2c_write_id = 0xA0", "0x77006901")))

# ---- alternates
check("s5kjn1cts: output format 2 (plain Bayer), no 4-cell / seamless handlers",
      fld(cs, "sensor_output_dataformat") == "2" and "GET_4CELL_DATA" not in cd and "SEAMLESS" not in cd)
check("ov32b40: common_open + eeprom_info xtalk 0x800@0x150F, mode tables 10-pair placeholders",
      ".open = common_open" in od and "xtalk_support = 1" in od and "addr_data_pair_preview[20]" in od)
lib = open(os.path.join(VEND, "libcameracustom.imgsensor.core.so"), "rb").read()
check("HAL tuning blobs: s5kjn1, s5kjn1cts, ov32b40 *_tuning.so present",
      all(os.path.exists(os.path.join(VEND, f"{n}_mipi_raw_tuning.so")) for n in ("s5kjn1", "s5kjn1cts", "ov32b40")))
check("HAL imgsensor.core: sensor-list entries s5kjn1/s5kjn1cts, ov32b40 only as IdxMgr .so",
      b"\0s5kjn1_mipi_raw\0" in lib and b"\0s5kjn1cts_mipi_raw\0" in lib
      and b"\0ov32b40_mipi_raw\0" not in lib and b"ov32b40_mipi_raw_IdxMgr.so" in lib, "ov32b40 = dormant option")

print(f"\n{'ALL PASS' if not fails else f'{fails} FAIL'}")
sys.exit(1 if fails else 0)
