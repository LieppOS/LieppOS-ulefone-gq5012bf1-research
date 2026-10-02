#!/usr/bin/env python3
"""Compare a stock imgsensor oracle sub-driver with a donor-source oracle.

Usage: compare_oracles.py <stock_oracle_dir> <stock_name> <donor_oracle_dir> <donor_name> [--rename a=b]

Both directories are produced by imgsensor_oracle.py (stock from imgsensor.ko,
donor from the donor sub-driver object compiled against the same headers).
Prints a markdown report: static_ctx field deltas, mode-table deltas,
per-register-table equality (exact / same-addresses / differing pairs).
"""
from __future__ import annotations

import csv
import json
import os
import sys

IGN_SC = {"static_ctx_addr"}
MODE_KEYS = ["setting_len", "seamless_group", "seamless_len", "hdr_mode", "raw_cnt", "exp_cnt", "pclk",
             "linelength", "framelength", "max_framerate", "mipi_pixel_rate", "readout_length", "read_margin",
             "framelength_step", "coarse_integ_step", "min_exposure_line", "winsize", "pdaf_cap",
             "ae_binning_ratio", "fine_integ_line", "delay_frame", "csi_param", "num_entries", "vc",
             "ana_gain_min", "ana_gain_max", "dig_gain_min", "dig_gain_max", "dcg_mode", "dcg_gain_mode",
             "dpc_enabled", "pdc_enabled", "cell_type", "aov_mode", "ae_ctrl_support", "rgbw_output_mode",
             "sensor_output_dataformat", "exposure_order_in_lbmf", "mode_type_in_lbmf"]


def load(d, name):
    j = json.load(open(os.path.join(d, "oracle.json")))
    for s in j["sensors"]:
        if s["name"] == name:
            return s
    raise SystemExit(f"{name} not in {d}")


def table(d, sym):
    p = os.path.join(d, "settings", sym.split("+")[0] + ".tsv")
    if not sym or not os.path.exists(p):
        return None
    with open(p) as f:
        r = list(csv.reader(f, delimiter="\t"))[1:]
    return [(a, v) for a, v in r]


def tcmp(a, b):
    if a is None or b is None:
        return "missing"
    if a == b:
        return f"IDENTICAL ({len(a)} pairs)"
    aa = [x for x, _ in a]
    ba = [x for x, _ in b]
    if aa == ba:
        nd = sum(1 for x, y in zip(a, b) if x != y)
        diffs = [f"{x[0]}:{x[1]}->{y[1]}" for x, y in zip(b, a) if x != y][:8]
        return f"SAME_ADDR_SEQ, {nd}/{len(a)} values differ: " + ", ".join(diffs)
    sa, sb = set(a), set(b)
    return (f"DIFFERENT (stock {len(a)} pairs, donor {len(b)} pairs; "
            f"{len(sa & sb)} common pairs, {len(set(aa) ^ set(ba))} addr not shared)")


def main():
    sd, sn, dd, dn = sys.argv[1:5]
    ren = {}
    for a in sys.argv[5:]:
        if a.startswith("--rename"):
            continue
        if "=" in a:
            k, v = a.split("=", 1)
            ren[k] = v
    s, d = load(sd, sn), load(dd, dn)
    print(f"# {sn} (stock) vs {dn} (donor)\n")
    print(f"* sensor id: stock {s['id']} / donor {d['id']}")
    print(f"* pw_seq: stock {[(p['hw_name'], p['val'], p['delay']) for p in s['pw_seq']]}")
    print(f"* pw_seq: donor {[(p['hw_name'], p['val'], p['delay']) for p in d['pw_seq']]}\n")
    print("## static_ctx field deltas\n\n| field | stock | donor |\n|---|---|---|")
    sc, dc = s["static_ctx"], d["static_ctx"]
    same = 0
    for k in sc:
        if k in IGN_SC:
            continue
        a, b = sc[k], dc.get(k)
        if isinstance(b, str):
            for x, y in ren.items():
                b = b.replace(x, y)
        if a != b:
            print(f"| {k} | `{a}` | `{b}` |")
        else:
            same += 1
    print(f"\n{same} static_ctx fields identical.\n")
    print("## Mode table\n")
    print(f"stock modes: {len(s['modes'])}, donor modes: {len(d['modes'])}\n")
    print("| idx | scenario | stock out | donor out | identical fields | differing fields | reg table |\n|---|---|---|---|---|---|---|")
    for i in range(max(len(s["modes"]), len(d["modes"]))):
        sm = s["modes"][i] if i < len(s["modes"]) else None
        dm = d["modes"][i] if i < len(d["modes"]) else None
        if sm is None or dm is None:
            m = sm or dm
            print(f"| {i} | {m['scenario']} | {'—' if sm is None else sm['winsize'][14:16]} | "
                  f"{'—' if dm is None else dm['winsize'][14:16]} | | only in {'donor' if sm is None else 'stock'} | |")
            continue
        diff = [k for k in MODE_KEYS if sm.get(k) != dm.get(k)]
        st = table(sd, sm["setting"])
        dt = table(dd, dm["setting"])
        tc = tcmp(st, dt)
        dd_ = ", ".join(f"{k}: {sm.get(k)}→{dm.get(k)}" if not isinstance(sm.get(k), (list, dict)) else k
                        for k in diff)
        print(f"| {i} | {sm['scenario']} | {sm['winsize'][14]}x{sm['winsize'][15]} | "
              f"{dm['winsize'][14]}x{dm['winsize'][15]} | {len(MODE_KEYS) - len(diff)} | {dd_ or '—'} | {tc} |")
    print("\n## Init / seamless tables\n")
    st = table(sd, sc["init_setting_table"])
    dt = table(dd, dc["init_setting_table"])
    print(f"* init: {tcmp(st, dt)}")
    for i in range(min(len(s["modes"]), len(d["modes"]))):
        a, b = s["modes"][i]["seamless_setting"], d["modes"][i]["seamless_setting"]
        if a or b:
            print(f"* mode {i} seamless `{a}` vs `{b}`: {tcmp(table(sd, a), table(dd, b))}")


if __name__ == "__main__":
    main()
