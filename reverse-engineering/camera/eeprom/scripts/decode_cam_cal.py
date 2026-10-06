#!/usr/bin/env python3
"""Decode the camera_eeprom_v4l2.ko calibration tables directly from the stock binary.

Outputs (TSV) into <outdir>:
  cam-cal-list.tsv      g_camCalList[]  (sensor -> EEPROM 8-bit address, read/write hooks, size)
  cam-cal-configs.tsv   cam_cal_config_list[] order + every STRUCT_CAM_CAL_CONFIG_STRUCT
  cam-cal-layouts.tsv   every layout table: header addr/id, data_ver, 9 command items

Struct layouts are those of the stock ABI (proven by the byte-identical rebuild):
  stCAM_CAL_LIST_STRUCT            32 B {u32 sensorID, u32 slaveID, fn read, u32 maxEepromSize, fn write}
  STRUCT_CAM_CAL_CONFIG_STRUCT     64 B {name, check_layout_function, read_function, layout,
                                         u32 sensor_id, i2c_write_id, max_size, enable_preload,
                                         preload_size, has_stored_data, base_address}
  STRUCT_CALIBRATION_LAYOUT_STRUCT 232 B {u32 header_addr, header_id, data_ver, pad,
                                         9 x {u16 Include, u32 start_addr, u32 block_size, fn}}
usage: decode_cam_cal.py <stock camera_eeprom_v4l2.ko> <kd_imgsensor.h> <outdir>
"""
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from elfko import Ko  # noqa: E402

CMDS = ['MODULE_VERSION', 'PART_NUMBER', 'SHADING_TABLE', '3A_GAIN', 'PDAF',
        'STEREO_DATA', 'DUMP', 'LENS_ID', 'SHADING_TABLE_16_9']
DATAVER = {0: 'SINGLE_EEPROM', 1: 'DOUBLE_EEPROM', 2: 'SINGLE_OTP', 3: 'TYPE_NUM'}


def sensor_names(hdr):
    ids = {}
    for m in re.finditer(r'#define\s+(\w+)_SENSOR_ID\s+(0x[0-9A-Fa-f]+|\d+)', open(hdr, errors='replace').read()):
        ids.setdefault(int(m.group(2), 0), []).append(m.group(1).lower())
    return ids


def fn(p):
    if p is None:
        return '-'
    return p.split('@')[0]


def main():
    ko, hdr, out = sys.argv[1:4]
    k = Ko(ko)
    names = sensor_names(hdr)
    sn = lambda v: ','.join(names.get(v, ['?']))
    d = k.data('.data')
    os.makedirs(out, exist_ok=True)

    cfg_ids = {s['name']: struct.unpack_from('<I', d, s['value'] + 32)[0] for s in k.syms
               if s['type'] == 1 and s['bind'] == 1 and s['size'] == 64 and s['sec'] == '.data'}
    g = [s for s in k.syms if s['name'] == 'g_camCalList'][0]
    with open(os.path.join(out, 'cam-cal-list.tsv'), 'w') as f:
        f.write('index\tsensor_id\tkd_imgsensor_h_name\tmatching_configs\tslave_id_8bit\tslave_id_7bit\tread_hook\tmax_eeprom_size\twrite_hook\n')
        for i in range(g['size'] // 32):
            o = g['value'] + i * 32
            sid, slave = struct.unpack_from('<II', d, o)
            (mx,) = struct.unpack_from('<I', d, o + 16)
            mc = ','.join(c for c in cfg_ids if cfg_ids[c] == sid) or '-'
            f.write(f"{i}\t0x{sid:x}\t{sn(sid) if sid else 'SENTINEL'}\t{mc if sid else '-'}\t0x{slave:02x}\t0x{slave >> 1:02x}\t"
                    f"{fn(k.describe_ptr('.data', o + 8))}\t{mx if mx else '0 (default 0x2000)'}\t"
                    f"{fn(k.describe_ptr('.data', o + 24))}\n")

    lst = [s for s in k.syms if s['name'] == 'cam_cal_config_list'][0]
    order = []
    for i in range(lst['size'] // 8):
        order.append(k.describe_ptr('.rodata', lst['value'] + i * 8).split('@')[0])
    cfgs = {s['name']: s for s in k.syms if s['type'] == 1 and s['bind'] == 1 and s['size'] == 64
            and s['sec'] == '.data'}
    with open(os.path.join(out, 'cam-cal-configs.tsv'), 'w') as fc, \
            open(os.path.join(out, 'cam-cal-layouts.tsv'), 'w') as fl:
        fc.write('list_index\tconfig\tstock_addr\tname_string\tsensor_id\tkd_imgsensor_h_name\tcheck_layout\tread_function\t'
                 'i2c_write_id_8bit\ti2c_7bit\tmax_size\tenable_preload\tpreload_size\thas_stored_data\tbase_address\t'
                 'layout_addr\theader_addr\theader_id\tdata_ver\tenabled_items\n')
        fl.write('config\tsensor_id\titem\tcommand\tinclude\tstart_addr\tblock_size\tend_addr_excl\tparser\n')
        for i, c in enumerate(order):
            s = cfgs[c]
            o = s['value']
            sid, i2c, mx, pre, psz, stored, base = struct.unpack_from('<7I', d, o + 32)
            lay = k.describe_ptr('.data', o + 24)
            laddr = int(lay.split(':')[-1], 16)
            ha, hid, dv = struct.unpack_from('<III', d, laddr)
            en = []
            for j in range(9):
                io = laddr + 16 + j * 24
                (inc,) = struct.unpack_from('<H', d, io)
                st, bs = struct.unpack_from('<II', d, io + 4)
                p = fn(k.describe_ptr('.data', io + 16))
                if inc:
                    en.append(CMDS[j])
                fl.write(f"{c}\t0x{sid:x}\t{j}\t{CMDS[j]}\t{inc}\t0x{st:x}\t0x{bs:x}\t0x{st + bs:x}\t{p}\n")
            fc.write(f"{i}\t{c}\t0x{o:x}\t{k.describe_ptr('.data', o)[4:]}\t0x{sid:x}\t{sn(sid)}\t"
                     f"{fn(k.describe_ptr('.data', o + 8))}\t{fn(k.describe_ptr('.data', o + 16))}\t"
                     f"0x{i2c:02x}\t0x{i2c >> 1:02x}\t0x{mx:x}\t{pre}\t0x{psz:x}\t{stored}\t0x{base:x}\t"
                     f"0x{laddr:x}\t0x{ha:x}\t0x{hid:08x}\t{DATAVER.get(dv, dv)}\t{','.join(en) or '-'}\n")


if __name__ == '__main__':
    main()
