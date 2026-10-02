#!/usr/bin/env python3
"""Stock imgsensor.ko oracle: decode every compiled sensor sub-driver.

Walks   <name>_mipi_raw_entry -> subdrv_ops -> init_ctx() -> static_ctx
        -> mode_struct[] -> setting tables / frame_desc / pd_info / csi_param
using only the symbol table + RELA relocations of the stock module, with the
struct layout recovered (pahole/DWARF) from the Nothing MT6878 mtkcam headers
(sizes verified equal to the stock objects: mode=440, static_ctx=800,
entry=40, pw_seq=12).

Usage:
  imgsensor_oracle.py <imgsensor.ko> <outdir>

Writes:
  <outdir>/sensors.tsv              one row per compiled sub-driver
  <outdir>/modes.tsv                one row per (sensor, mode)
  <outdir>/frame-desc.tsv           one row per (sensor, mode, VC entry)
  <outdir>/pw-seq.tsv               power sequences
  <outdir>/settings/<sym>.tsv       every u16 register table as addr/value
  <outdir>/hw-id-names.tsv          stock HW_ID enum order (from string table)
  <outdir>/oracle.json              everything above, machine readable
Read-only on the input.
"""
from __future__ import annotations

import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from elfmini import Elf  # noqa: E402

MODE_SZ = 440
SCTX_SZ = 800

SCENARIO = ["preview", "capture", "normal_video", "hs_video", "slim_video"] + [f"custom{i}" for i in range(1, 40)]

# kd_imgsensor_define_v4l2.h (bit flags in the v4l2 framework)
HDR_MODE = {0: "NONE", 1: "RAW", 2: "CAMSV", 4: "RAW_ZHDR", 8: "MultiCAMSV", 16: "RAW_STAGGER",
            32: "RAW_DCG_RAW", 64: "RAW_DCG_COMPOSE", 128: "RAW_LBMF"}
LANES = {0: 1, 1: 2, 2: 3, 3: 4}
PHY = {0: "MIPI_OPHY_NCSI2(D-PHY)", 1: "MIPI_OPHY_CSI2(D-PHY)", 2: "MIPI_CPHY"}
PDAF = {0: "NA", 1: "RAW", 2: "CAMSV", 3: "CAMSV_LEGACY", 4: "RAW_DUALPD", 5: "CAMSV_DUALPD", 6: "RAW_LEGACY",
        7: "CAMSV_QPD", 8: "CAMSV_RGBW"}


def u(fmt, b, o):
    return struct.unpack_from("<" + fmt, b, o)[0]


DUP = set()


def uname(s):
    """Unique printable name: static symbols that occur in several translation
    units get an @<section-offset> suffix."""
    return f"{s.name}@{s.value:x}" if s.name in DUP else s.name


def sym_name(t):
    if t is None:
        return ""
    s, off = t
    return uname(s) + (f"+0x{off:x}" if off else "")


def decode_static_ctx(elf, sc):
    b = elf.bytes_of(sc)
    d = {
        "sensor_id": f"0x{u('I', b, 0):x}",
        "reg_addr_sensor_id": [f"0x{u('H', b, 4 + 2 * i):04x}" for i in range(3)],
        "i2c_addr_table": [f"0x{x:02x}" for x in b[10:15]],
        "i2c_burst_write_support": u('I', b, 16),
        "i2c_transfer_data_type": u('I', b, 20),
        "eeprom_info": sym_name(elf.ptr_at(sc, 24)),
        "eeprom_num": u('I', b, 32),
        "resolution": [u('H', b, 36), u('H', b, 38)],
        "mirror": b[40], "mclk": b[41], "isp_driving_current": b[42],
        "sensor_interface_type": b[43], "mipi_sensor_type": PHY.get(b[44], b[44]),
        "mipi_lane_num": LANES.get(b[45], b[45]),
        "ob_pedestal": u('I', b, 48), "sensor_output_dataformat": b[52],
        "ana_gain_def": u('I', b, 56), "ana_gain_min": u('I', b, 60), "ana_gain_max": u('I', b, 64),
        "ana_gain_type": u('I', b, 68), "ana_gain_step": u('I', b, 72),
        "ana_gain_table": sym_name(elf.ptr_at(sc, 80)), "ana_gain_table_size": u('I', b, 88),
        "min_gain_iso": u('I', b, 92),
        "exposure_def": u('I', b, 96), "exposure_min": u('I', b, 100), "exposure_max": u('I', b, 104),
        "exposure_step": u('I', b, 108), "exposure_margin": b[112],
        "dig_gain_min": u('I', b, 116), "dig_gain_max": u('I', b, 120), "dig_gain_step": u('I', b, 124),
        "saturation_info": sym_name(elf.ptr_at(sc, 128)),
        "frame_length_max": u('I', b, 136), "ae_effective_frame": b[140], "frame_time_delay_frame": b[141],
        "start_exposure_offset": u('I', b, 144), "start_exposure_offset_custom": u('I', b, 148),
        "pdaf_type": PDAF.get(u('I', b, 152), u('I', b, 152)), "hdr_type": u('I', b, 156), "rgbw_support": u('I', b, 160),
        "seamless_switch_support": b[164], "seamless_switch_type": u('I', b, 168),
        "seamless_switch_hw_re_init_time_ns": u('I', b, 172),
        "seamless_switch_prsh_hw_fixed_value": b[176], "seamless_switch_prsh_length_lc": u('I', b, 180),
        "reg_addr_prsh_length_lines": [f"0x{u('H', b, 184 + 2 * i):04x}" for i in range(3)],
        "reg_addr_prsh_mode": f"0x{u('H', b, 190):04x}",
        "temperature_support": b[192],
        "g_temp": sym_name(elf.ptr_at(sc, 200)), "g_gain2reg": sym_name(elf.ptr_at(sc, 208)),
        "g_cali": sym_name(elf.ptr_at(sc, 216)), "s_gph": sym_name(elf.ptr_at(sc, 224)),
        "s_cali": sym_name(elf.ptr_at(sc, 232)), "s_streaming_control": sym_name(elf.ptr_at(sc, 240)),
        "s_data_rate_global_timing_phy_ctrl": sym_name(elf.ptr_at(sc, 248)),
        "s_pwr_seq_reset_view_to_sensing": sym_name(elf.ptr_at(sc, 256)),
        "reg_addr_stream": f"0x{u('H', b, 264):04x}", "reg_addr_mirror_flip": f"0x{u('H', b, 266):04x}",
        "reg_addr_exposure": [[f"0x{u('H', b, 268 + 6 * k + 2 * i):04x}" for i in range(3)] for k in range(5)],
        "long_exposure_support": u('H', b, 328), "reg_addr_exposure_lshift": f"0x{u('H', b, 330):04x}",
        "reg_addr_ana_gain": [[f"0x{u('H', b, 332 + 6 * k + 2 * i):04x}" for i in range(3)] for k in range(5)],
        "reg_addr_dig_gain": [[f"0x{u('H', b, 392 + 6 * k + 2 * i):04x}" for i in range(3)] for k in range(5)],
        "reg_addr_frame_length": [f"0x{u('H', b, 452 + 2 * i):04x}" for i in range(3)],
        "reg_addr_temp_en": f"0x{u('H', b, 488):04x}", "reg_addr_temp_read": f"0x{u('H', b, 490):04x}",
        "reg_addr_auto_extend": f"0x{u('H', b, 492):04x}", "reg_addr_frame_count": f"0x{u('H', b, 494):04x}",
        "reg_addr_fast_mode": f"0x{u('H', b, 496):04x}", "reg_addr_dcg_ratio": f"0x{u('H', b, 498):04x}",
        "init_setting_table": sym_name(elf.ptr_at(sc, 504)), "init_setting_len": u('I', b, 512),
        "mode": sym_name(elf.ptr_at(sc, 520)), "sensor_mode_num": u('I', b, 528),
        "list": sym_name(elf.ptr_at(sc, 536)), "list_len": u('I', b, 544),
        "chk_s_off_sta": b[548], "chk_s_off_end": b[549], "checksum_value": f"0x{u('I', b, 552):x}",
        "aov_sensor_support": b[556], "aov_csi_clk": u('I', b, 560), "sensor_mode_ops": u('I', b, 564),
        "init_in_open": b[572], "streaming_ctrl_imp": b[573],
        "custom_stream_ctrl_delay": u('Q', b, 576),
        "glp_dt": [u('I', b, 784 + 4 * i) for i in range(4)],
    }
    return d


def decode_mode(elf, ms, i):
    o = i * MODE_SZ
    b = elf.bytes_of(ms, o, MODE_SZ)
    w = [u('H', b, 100 + 2 * k) for k in range(16)]
    csi = b[172:200]
    m = {
        "idx": i, "scenario": SCENARIO[i] if i < len(SCENARIO) else f"m{i}",
        "setting": sym_name(elf.ptr_at(ms, o + 0)), "setting_len": u('I', b, 8),
        "setting_md": sym_name(elf.ptr_at(ms, o + 16)), "setting_md_len": u('I', b, 24),
        "seamless_group": u('I', b, 28),
        "seamless_setting": sym_name(elf.ptr_at(ms, o + 32)), "seamless_len": u('I', b, 40),
        "hdr_mode": HDR_MODE.get(u('I', b, 44), u('I', b, 44)), "raw_cnt": u('I', b, 48), "exp_cnt": u('I', b, 52),
        "pclk": u('Q', b, 56), "linelength": u('I', b, 64), "framelength": u('I', b, 68),
        "max_framerate": u('H', b, 72), "mipi_pixel_rate": u('I', b, 76), "readout_length": u('I', b, 80),
        "read_margin": b[84], "framelength_step": u('I', b, 88), "coarse_integ_step": u('I', b, 92),
        "min_exposure_line": u('I', b, 96),
        "winsize": w,
        "rgbw_output_mode": u('I', b, 132), "aov_mode": b[136], "rosc_mode": b[137],
        "s_dummy_support": b[138], "ae_ctrl_support": u('I', b, 140),
        "pdaf_cap": b[144], "pd_info": sym_name(elf.ptr_at(ms, o + 152)),
        "ae_binning_ratio": u('I', b, 160), "fine_integ_line": struct.unpack_from('<i', b, 164)[0],
        "delay_frame": b[168],
        "csi_param": {
            "dphy_trail": u('I', csi, 0), "dphy_data_settle": u('I', csi, 4), "dphy_clk_settle": u('I', csi, 8),
            "cphy_settle": u('I', csi, 12), "legacy_phy": csi[16], "not_fixed_trail_settle": csi[17],
            "dphy_csi2_resync_dmy_cycle": u('I', csi, 20), "not_fixed_dphy_settle": csi[24],
            "dphy_init_deskew_support": csi[25], "cphy_lrte_support": csi[26]},
        "frame_desc": sym_name(elf.ptr_at(ms, o + 200)), "num_entries": u('I', b, 208),
        "sensor_output_dataformat": b[212], "cell_type": u('I', b, 216),
        "ana_gain_min": u('I', b, 220), "ana_gain_max": u('I', b, 224),
        "dig_gain_min": u('I', b, 228), "dig_gain_max": u('I', b, 232), "dig_gain_step": u('I', b, 236),
        "dpc_enabled": b[360], "pdc_enabled": b[361],
        "saturation_info": sym_name(elf.ptr_at(ms, o + 368)),
        "dcg_mode": u('I', b, 376), "dcg_gain_mode": u('I', b, 380), "dcg_gain_base": u('I', b, 384),
        "dcg_ratio_min": u('I', b, 388), "dcg_ratio_max": u('I', b, 392),
        "dcg_gain_table": sym_name(elf.ptr_at(ms, o + 400)),
        "exposure_order_in_lbmf": u('I', b, 432), "mode_type_in_lbmf": u('I', b, 436),
    }
    # frame descriptor entries
    fd = elf.ptr_at(ms, o + 200)
    m["vc"] = []
    if fd:
        fs, foff = fd
        for k in range(m["num_entries"]):
            e = elf.bytes_of(fs, foff + 20 * k, 20)
            m["vc"].append({"ch": e[0], "dt": f"0x{e[1]:02x}", "hsize": u('H', e, 4), "vsize": u('H', e, 6),
                            "user_data_desc": u('H', e, 8), "pre_latch": e[10],
                            "tsrec_exp_id": u('I', e, 12), "valid_bit": u('H', e, 16),
                            "active_line": e[18], "ebd_parsing": e[19]})
    return m


def find_static_ctx(elf, initfn):
    for r in elf.relocs_in(initfn):
        t, off = elf.target(r)
        if t.name == "static_ctx":
            return t
    return None


def hw_id_names(elf):
    """Recover the stock HW_ID enum order from the pointer table of names."""
    best = None
    for s in elf.symbols:
        if s.type != 1 or not s.shndx or s.size < 64:
            continue
        names = []
        for r in elf.relocs_in(s):
            t, off = elf.target(r)
            try:
                st = elf.cstring_at(r.sym.shndx, r.sym.value + r.addend)
            except Exception:
                st = ""
            names.append(st)
        if names and names[0] == "HW_ID_AVDD":
            best = (s, names)
            break
    if best is None:
        # pointer table may be an anonymous .data region; scan all .data relocs
        for secidx, lst in elf.relocs.items():
            for i, r in enumerate(lst):
                try:
                    st = elf.cstring_at(r.sym.shndx, r.sym.value + r.addend)
                except Exception:
                    continue
                if st == "HW_ID_AVDD":
                    names = []
                    j = i
                    while j < len(lst):
                        try:
                            n = elf.cstring_at(lst[j].sym.shndx, lst[j].sym.value + lst[j].addend)
                        except Exception:
                            break
                        if not n.startswith("HW_ID_"):
                            break
                        names.append(n)
                        j += 1
                    if len(names) > 5:
                        return names
        return []
    return best[1]


def main():
    ko, out = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.join(out, "settings"), exist_ok=True)
    elf = Elf(ko)
    seen = {}
    for sy in elf.symbols:
        if sy.type == 1 and sy.shndx:
            seen[sy.name] = seen.get(sy.name, 0) + 1
    DUP.update(k for k, v in seen.items() if v > 1)
    hwids = hw_id_names(elf)
    with open(os.path.join(out, "hw-id-names.tsv"), "w") as f:
        f.write("id\tname\n")
        for i, n in enumerate(hwids):
            f.write(f"{i}\t{n}\n")

    entries = [s for s in elf.symbols if s.type == 1 and s.name.endswith("_mipi_raw_entry") and s.shndx]
    result = {"module": ko, "hw_id_names": hwids, "sensors": []}
    dumped = set()
    for e in sorted(entries, key=lambda s: s.name):
        b = elf.bytes_of(e)
        nm = elf.ptr_at(e, 0)
        name = elf.cstring_at(nm[0].shndx, nm[0].value + nm[1]) if nm and nm[0].type != 1 else ""
        if nm and not name:
            r = [r for r in elf.relocs_in(e) if r.off == e.value][0]
            name = elf.cstring_at(r.sym.shndx, r.sym.value + r.addend)
        sid = u('I', b, 8)
        pw = elf.ptr_at(e, 16)
        ops = elf.ptr_at(e, 24)
        pwcnt = u('i', b, 32)
        sens = {"entry": e.name, "name": name, "id": f"0x{sid:x}", "pw_seq_cnt": pwcnt, "pw_seq": []}
        if pw:
            ps, poff = pw
            for k in range(pwcnt):
                hid, val, dly = struct.unpack_from("<iii", elf.bytes_of(ps, poff + 12 * k, 12))
                sens["pw_seq"].append({"hw_id": hid, "hw_name": hwids[hid] if hid < len(hwids) else str(hid),
                                       "val": val, "delay": dly})
        opsd = {}
        if ops:
            os_, ooff = ops
            for fi, fname in enumerate(["get_id", "init_ctx", "open", "get_info", "get_resolution",
                                        "feature_control", "control", "close", "get_frame_desc", "get_temp",
                                        "vsync_notify", "update_sof_cnt", "get_csi_param", "power_on",
                                        "power_off", "parse_ebd_line", "set_ctrl_locker"]):
                t = elf.ptr_at(os_, ooff + 8 * fi)
                opsd[fname] = (t[0].name + (f"@0x{t[0].value:x}" if t[0].bind == 0 else "")) if t else ""
            initfn = elf.ptr_at(os_, ooff + 8)
            sens["ops"] = opsd
            sc = find_static_ctx(elf, initfn[0]) if initfn else None
        else:
            sc = None
        if sc is None:
            sens["static_ctx"] = None
            result["sensors"].append(sens)
            continue
        sens["static_ctx_addr"] = f"0x{sc.value:x}"
        sens["static_ctx"] = decode_static_ctx(elf, sc)
        # sensor feature-control list
        msym = elf.ptr_at(sc, 520)
        sens["modes"] = []
        if msym:
            ms = msym[0]
            for i in range(sens["static_ctx"]["sensor_mode_num"]):
                sens["modes"].append(decode_mode(elf, ms, i))
        # dump setting tables
        tables = set()
        tables.add(sens["static_ctx"]["init_setting_table"])
        for m in sens["modes"]:
            tables.add(m["setting"])
            tables.add(m["seamless_setting"])
        for t in sorted(x for x in tables if x):
            base = t.split("+")[0]
            cand = [s for s in elf.symbols if uname(s) == base and s.type == 1 and s.shndx]
            if not cand or base in dumped:
                continue
            dumped.add(base)
            s = cand[0]
            raw = elf.bytes_of(s)
            vals = struct.unpack_from("<%dH" % (len(raw) // 2), raw)
            with open(os.path.join(out, "settings", base + ".tsv"), "w") as f:
                f.write("addr\tvalue\n")
                for k in range(0, len(vals) - 1, 2):
                    f.write(f"0x{vals[k]:04x}\t0x{vals[k + 1]:04x}\n")
        result["sensors"].append(sens)

    # TSVs
    with open(os.path.join(out, "sensors.tsv"), "w") as f:
        cols = ["name", "id", "static_ctx_addr", "i2c_addr_table", "reg_addr_sensor_id", "resolution", "mclk",
                "mipi_lane_num", "sensor_interface_type", "mipi_sensor_type", "sensor_output_dataformat",
                "ob_pedestal", "ana_gain_min", "ana_gain_max", "exposure_min", "exposure_margin",
                "frame_length_max", "pdaf_type", "hdr_type", "seamless_switch_support", "temperature_support",
                "eeprom_info", "eeprom_num", "init_setting_table", "init_setting_len", "sensor_mode_num",
                "reg_addr_stream", "reg_addr_mirror_flip", "reg_addr_frame_length", "reg_addr_temp_en",
                "reg_addr_temp_read", "g_temp", "g_cali", "s_cali", "s_streaming_control", "aov_sensor_support"]
        f.write("\t".join(cols) + "\n")
        for s in result["sensors"]:
            sc = s.get("static_ctx") or {}
            row = []
            for c in cols:
                v = s.get(c, sc.get(c, ""))
                row.append(json.dumps(v) if isinstance(v, (list, dict)) else str(v))
            f.write("\t".join(row) + "\n")
    with open(os.path.join(out, "modes.tsv"), "w") as f:
        cols = ["sensor", "idx", "scenario", "setting", "setting_len", "seamless_group", "seamless_setting",
                "hdr_mode", "exp_cnt", "pclk", "linelength", "framelength", "max_framerate", "mipi_pixel_rate",
                "readout_length", "full_w", "full_h", "out_w", "out_h", "pdaf_cap", "pd_info", "ae_binning_ratio",
                "fine_integ_line", "delay_frame", "dphy_trail", "dphy_data_settle", "cphy_settle", "legacy_phy",
                "num_entries", "ana_gain_min", "ana_gain_max", "dcg_mode", "dpc", "pdc", "cell_type"]
        f.write("\t".join(cols) + "\n")
        for s in result["sensors"]:
            for m in s.get("modes", []):
                w = m["winsize"]
                c = m["csi_param"]
                vals = [s["name"], m["idx"], m["scenario"], m["setting"], m["setting_len"], m["seamless_group"],
                        m["seamless_setting"], m["hdr_mode"], m["exp_cnt"], m["pclk"], m["linelength"],
                        m["framelength"], m["max_framerate"], m["mipi_pixel_rate"], m["readout_length"],
                        w[0], w[1], w[14], w[15], m["pdaf_cap"], m["pd_info"], m["ae_binning_ratio"],
                        m["fine_integ_line"], m["delay_frame"], c["dphy_trail"], c["dphy_data_settle"],
                        c["cphy_settle"], c["legacy_phy"], m["num_entries"], m["ana_gain_min"], m["ana_gain_max"],
                        m["dcg_mode"], m["dpc_enabled"], m["pdc_enabled"], m["cell_type"]]
                f.write("\t".join(str(v) for v in vals) + "\n")
    with open(os.path.join(out, "frame-desc.tsv"), "w") as f:
        f.write("sensor\tmode\tscenario\tvc_idx\tchannel\tdata_type\thsize\tvsize\tuser_data_desc\tvalid_bit\n")
        for s in result["sensors"]:
            for m in s.get("modes", []):
                for k, v in enumerate(m["vc"]):
                    f.write(f"{s['name']}\t{m['idx']}\t{m['scenario']}\t{k}\t{v['ch']}\t{v['dt']}\t{v['hsize']}\t"
                            f"{v['vsize']}\t{v['user_data_desc']}\t{v['valid_bit']}\n")
    with open(os.path.join(out, "pw-seq.tsv"), "w") as f:
        f.write("sensor\tstep\thw_id\thw_name\tval\tdelay_ms\n")
        for s in result["sensors"]:
            for k, p in enumerate(s["pw_seq"]):
                f.write(f"{s['name']}\t{k}\t{p['hw_id']}\t{p['hw_name']}\t{p['val']}\t{p['delay']}\n")
    with open(os.path.join(out, "oracle.json"), "w") as f:
        json.dump(result, f, indent=1)
    print(f"{len(result['sensors'])} sub-drivers decoded; {len(dumped)} register tables dumped")


if __name__ == "__main__":
    main()
