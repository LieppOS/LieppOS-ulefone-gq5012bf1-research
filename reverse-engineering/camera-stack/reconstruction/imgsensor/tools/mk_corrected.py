#!/usr/bin/env python3
"""Derive the CORRECTED representation from a STOCK-PARITY sensor data header.

The stock GQ5012BF1 sub-drivers contain modes whose frame descriptor (the CSI
virtual-channel layout reported to seninf/cam-mux) does not match the mode's
TG output window -- the ODM reordered setting tables / windows but kept the
donor descriptors.  The parity build must reproduce that byte-for-byte; this
tool emits a *separate* header with the inconsistency fixed:

  * every mode whose RAW image entries (CSI data type 0x2a..0x2d) have
    hsize/vsize != imgsensor_winsize_info.{w2_tg_size,h2_tg_size} gets a new
    frame_desc array `<orig>__m<idx>` that is a copy of the stock one with the
    RAW entries resized to the TG window; the mode points at the new array;
  * PDAF / embedded entries are left untouched (their geometry is not derived
    from the TG window) and are listed in the report for manual review;
  * stock arrays are kept (other, consistent modes may share them).

Selection: the sensor .c includes <v>_corrected_data.h only when
GQ5012BF1_CAM_CORRECTED is defined; the parity build never defines it.

Authority: the output size actually programmed by the mode's register table
(Sony 0x034C-0x034F, Samsung 0x034C/0x034E, OmniVision 0x3808-0x380B).
  * RAW VC entries that disagree with it are resized;
  * a TG window that disagrees with it is rebuilt from the register crop /
    binning (Samsung only: 0x0344-0x034A, 0x0900); other families are
    reported as UNDETERMINED;
  * modes whose table does not program an output size (e.g. ov32b40's
    10-pair PLL stubs) are reported as UNDETERMINED and left as stock.

usage: mk_corrected.py <family sony|samsung|ov> <v>_stock_data.h <v>_corrected_data.h [report.tsv]
"""
import re
import sys

RAW_DT = {0x2a, 0x2b, 0x2c, 0x2d}


def num(s):
    return int(s, 0)


def parse_tables(src):
    arrs = {}
    for m in re.finditer(r"static u(?:8|16) (\w+)\[\d+\] = \{\n(.*?)\n\};", src, re.S):
        v = [int(x, 0) for x in re.findall(r"0x[0-9a-fA-F]+|\b\d+\b", m.group(2))]
        arrs[m.group(1)] = dict(zip(v[0::2], v[1::2]))
    return arrs


def reg_output(fam, d):
    if fam == "samsung" and 0x034C in d and 0x034E in d:
        return d[0x034C], d[0x034E]
    if fam == "sony" and all(k in d for k in (0x034C, 0x034D, 0x034E, 0x034F)):
        return (d[0x034C] << 8) | d[0x034D], (d[0x034E] << 8) | d[0x034F]
    if fam == "ov" and all(k in d for k in (0x3808, 0x3809, 0x380A, 0x380B)):
        return (d[0x3808] << 8) | d[0x3809], (d[0x380A] << 8) | d[0x380B]
    return None


def samsung_winsize(d, out):
    """Rebuild winsize fields from Samsung crop/binning registers."""
    try:
        xs, ys, xe, ye = d[0x0344], d[0x0346], d[0x0348], d[0x034A]
    except KeyError:
        return None
    b = d.get(0x0900, 0)
    bx, by = ((b >> 4) & 0xF, b & 0xF) if (b >> 8) & 1 else (1, 1)
    w0, h0 = xe - xs + 1, ye - ys + 1
    sw, sh = w0 // max(bx, 1), h0 // max(by, 1)
    ow, oh = out
    if ow > sw or oh > sh:
        return None
    return {"x0_offset": xs, "y0_offset": ys, "w0_size": w0, "h0_size": h0,
            "scale_w": sw, "scale_h": sh, "x1_offset": (sw - ow) // 2, "y1_offset": (sh - oh) // 2,
            "w1_size": ow, "h1_size": oh, "x2_tg_offset": 0, "y2_tg_offset": 0,
            "w2_tg_size": ow, "h2_tg_size": oh}


def set_winsize(body, fields):
    m = re.search(r"(\.imgsensor_winsize_info = \{\n)(.*?)(\n\t\t\},)", body, re.S)
    lines = dict(re.findall(r"\.(\w+) = (\w+),", m.group(2)))
    for k, v in fields.items():
        lines[k] = f"{v:#x}"
    order = ["full_w", "full_h", "x0_offset", "y0_offset", "w0_size", "h0_size", "scale_w", "scale_h",
             "x1_offset", "y1_offset", "w1_size", "h1_size", "x2_tg_offset", "y2_tg_offset",
             "w2_tg_size", "h2_tg_size"]
    txt = "\n".join(f"\t\t\t.{k} = {lines[k]}," for k in order if k in lines and lines[k] not in ("0", "0x0"))
    return body[:m.start()] + m.group(1) + txt + m.group(3) + body[m.end():]


def parse_frame_descs(src):
    fds = {}
    for m in re.finditer(r"static struct mtk_mbus_frame_desc_entry (\w+)\[(\d+)\] = \{\n(.*?)\n\};\n", src, re.S):
        name, body = m.group(1), m.group(3)
        ents = []
        for e in re.finditer(r"\.bus = \{\.csi2 = \{(.*?)\}\}", body, re.S):
            f = dict((k, v) for k, v in re.findall(r"\.(\w+) = ([^,\n]+),", e.group(1)))
            ents.append(f)
        fds[name] = (m.start(), m.end(), m.group(0), ents)
    return fds


def parse_modes(src):
    m = re.search(r"static struct subdrv_mode_struct mode_struct\[(\d+)\] = \{\n", src)
    if not m:
        return None, []
    i = m.end()
    modes = []
    depth = 0
    start = None
    while i < len(src):
        c = src[i]
        if c == "{":
            if depth == 0:
                start = i
            depth += 1
        elif c == "}":
            if depth == 0:
                break
            depth -= 1
            if depth == 0:
                modes.append((start, i + 1))
        i += 1
    return m.start(), modes


def main():
    fam, sin, sout = sys.argv[1], sys.argv[2], sys.argv[3]
    rep = sys.argv[4] if len(sys.argv) > 4 else None
    src = open(sin).read()
    fds = parse_frame_descs(src)
    tabs = parse_tables(src)
    mstart, modes = parse_modes(src)
    out = src
    new_arrays, report, edits = [], [], []
    for idx, (a, b) in enumerate(modes):
        body = src[a:b]
        fm = re.search(r"\.frame_desc = (\w+),", body)
        tm = re.search(r"\.mode_setting_table = (\w+),", body)
        tw = re.search(r"\.w2_tg_size = (\w+),", body)
        th = re.search(r"\.h2_tg_size = (\w+),", body)
        if not (fm and tw and th) or fm.group(1) not in fds:
            continue
        fd = fm.group(1)
        tg = (num(tw.group(1)), num(th.group(1)))
        ents = fds[fd][3]
        raw = [k for k, e in enumerate(ents) if num(e.get("data_type", "0")) in RAW_DT]
        rawsz = [(num(ents[k]["hsize"]), num(ents[k]["vsize"])) for k in raw]
        regs = tabs.get(tm.group(1), {}) if tm else {}
        truth = reg_output(fam, regs)
        consistent = all(sz == tg for sz in rawsz)
        if truth is None:
            if not consistent:
                report.append((idx, fd, tm.group(1) if tm else "-", "?", f"{tg[0]}x{tg[1]}",
                               ";".join(f"{w}x{h}" for w, h in rawsz), "UNDETERMINED(no output-size registers)"))
            continue
        bad = [k for k, sz in zip(raw, rawsz) if sz != truth]
        nb = body
        actions = []
        if tg != truth:
            ws = samsung_winsize(regs, truth) if fam == "samsung" else None
            if ws:
                nb = set_winsize(nb, ws)
                actions.append("TG-rebuilt-from-registers")
            else:
                actions.append("TG-mismatch-UNDETERMINED")
        if bad:
            w, h = truth
            nn = f"{fd}__m{idx}"
            arr = fds[fd][2].replace(f" {fd}[", f" {nn}[", 1)
            k = -1

            def fix(mo):
                nonlocal k
                k += 1
                blk = mo.group(0)
                if k in bad:
                    blk = re.sub(r"\.hsize = \w+,", f".hsize = {w:#x},", blk)
                    blk = re.sub(r"\.vsize = \w+,", f".vsize = {h:#x},", blk)
                return blk
            arr = re.sub(r"\.bus = \{\.csi2 = \{.*?\}\}", fix, arr, flags=re.S)
            new_arrays.append(f"/* CORRECTED: mode {idx} registers program {w}x{h}; stock {fd} RAW VC {rawsz} */\n" + arr)
            nb = nb.replace(f".frame_desc = {fd},", f".frame_desc = {nn},")
            actions.append("VC-resized")
        if actions:
            edits.append((a, b, nb))
            report.append((idx, fd, tm.group(1), f"{truth[0]}x{truth[1]}", f"{tg[0]}x{tg[1]}",
                           ";".join(f"{w}x{h}" for w, h in rawsz), "+".join(actions)))
    for a, b, nb in sorted(edits, reverse=True):
        out = out[:a] + nb + out[b:]
    if new_arrays:
        out = out[:mstart] + "\n".join(new_arrays) + "\n" + out[mstart:]
    hdr = ("/* CORRECTED representation generated by mk_corrected.py from the\n"
           " * STOCK-PARITY header; NOT used by the parity build. */\n")
    open(sout, "w").write(hdr + out)
    cols = "mode\tstock_frame_desc\tsetting_table\tregister_output\tstock_tg\tstock_raw_vc\taction\n"
    if rep:
        with open(rep, "w") as f:
            f.write(cols)
            for r in report:
                f.write("\t".join(map(str, r)) + "\n")
    for r in report:
        print("\t".join(map(str, r)))


if __name__ == "__main__":
    main()
