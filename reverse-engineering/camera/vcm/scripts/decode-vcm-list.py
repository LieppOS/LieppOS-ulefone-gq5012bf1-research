#!/usr/bin/env python3
"""decode-vcm-list.py libcameracustom.lens.so [--tsv]

Decode the vcm_list_N tables of the stock MTK lens custom library.

Record layout (0x108 bytes) derived from the stock disassembly of
GetVcmDriverName(int,int,int,int*,char*,VcmDriverConfig*):
  +0x00 u32 sensor_id     matched against arg1
  +0x04 u32 module_id     0 = wildcard, else matched against arg2
  +0x08 u32 lens_id       -> *arg3
  +0x0C char name[32]     -> arg4 (kernel subdev name: main_vcm, ...)
  +0x2C 12 bytes          not read by GetVcmDriverName
  +0x38 VcmDriverConfig   208 bytes -> arg5, copied verbatim to the kernel by
                          VIDIOC_MTK_S_LENS_INFO (layout = kernel struct)
VcmDriverConfig (kernel main_vcm.c, arm64 natural alignment):
  +0   u32 ctrl_delay_us
  +4   u8  wr_table[16][3]    {cmd, reg, val}; cmd 1=write 2=poll-until 3=mdelay 4=read
  +52  u32 slave_addr         8-bit form; kernel uses >>1
  +56  u8  I2CSendNum
  +57  I2Cfmt[4] x 26 bytes: Addr[4] AddrNum CtrlData[4] BitR[4] Mask1[4] BitL[4] Mask2[4] DataNum
  +164 u32 origin_focus_pos
  +168 u32 move_steps
  +172 u32 move_delay_us
  +176 u8  wr_rls_table[8][3]
  +200 s32 vcm_bits
  +204 s32 af_calib_bits
"""
import struct, subprocess, sys, os

RE = os.environ.get('LLVM_READELF', 'llvm-readelf')


def syms(path):
    out = {}
    for l in subprocess.run([RE, '-sW', '--dyn-syms', path], capture_output=True, text=True).stdout.splitlines():
        f = l.split()
        if len(f) >= 8 and f[0].rstrip(':').isdigit() and f[3] == 'OBJECT':
            out[f[7]] = (int(f[1], 16), int(f[2]))
    return out


def vaddr_to_off(path):
    segs = []
    for l in subprocess.run([RE, '-lW', path], capture_output=True, text=True).stdout.splitlines():
        f = l.split()
        if f and f[0] == 'LOAD':
            segs.append((int(f[2], 16), int(f[1], 16), int(f[5], 16)))
    return lambda va: next(o + va - v for v, o, sz in segs if v <= va < v + sz)


def table(t):
    rows = []
    for i in range(0, len(t), 3):
        c, r, v = t[i:i + 3]
        if c == 0:
            break
        rows.append({1: f'W {r:#04x}={v:#04x}', 2: f'POLL {r:#04x}=={v:#04x}', 3: f'DELAY {r}ms',
                     4: f'READ {r:#04x}x{v}'}.get(c, f'?{c}:{r:#x}:{v:#x}'))
    return rows


def cfg(b):
    ctrl, = struct.unpack_from('<I', b, 0)
    wr = b[4:52]
    slave, = struct.unpack_from('<I', b, 52)
    n = b[56]
    fm = []
    for k in range(min(n, 4)):
        o = 57 + 26 * k
        addr, an = b[o:o + 4], b[o + 4]
        ctl, br, m1, bl, m2 = (b[o + 5 + 4 * j:o + 9 + 4 * j] for j in range(5))
        dn = b[o + 25]
        parts = [f'addr={"".join(f"{x:02x}" for x in addr[:an])}']
        for j in range(dn):
            parts.append(f'd{j}=((pos>>{br[j]})&{m1[j]:#x})<<{bl[j]}&{m2[j]:#x}|{ctl[j]:#x}')
        fm.append(' '.join(parts))
    org, steps, mdly = struct.unpack_from('<III', b, 164)
    rls = b[176:200]
    vb, ab = struct.unpack_from('<ii', b, 200)
    return dict(ctrl_delay_us=ctrl, init=table(wr), slave_addr8=slave, slave_addr7=slave >> 1, move=fm,
                origin=org, move_steps=steps, move_delay_us=mdly, release=table(rls), vcm_bits=vb, af_calib_bits=ab)


def main():
    p = sys.argv[1]
    raw = open(p, 'rb').read()
    s = syms(p); v2o = vaddr_to_off(p)
    tsv = '--tsv' in sys.argv
    if tsv:
        print('list\tindex\tsensor_id\tmodule_id\tlens_id\tname\tslave_addr7\tinit\tmove\torigin\tmove_steps\tmove_delay_us\trelease\tvcm_bits\taf_calib_bits\tctrl_delay_us')
    for name in sorted(k for k in s if k.startswith('vcm_list_')):
        va, size = s[name]
        off = v2o(va)
        for i in range(size // 0x108):
            r = raw[off + i * 0x108: off + (i + 1) * 0x108]
            sid, mid, lid = struct.unpack_from('<III', r, 0)
            nm = r[12:44].split(b'\0')[0].decode('latin1')
            if not (sid or mid or lid or nm):
                continue
            c = cfg(r[0x38:0x108])
            if tsv:
                print('\t'.join(map(str, [name, i, f'{sid:#x}', f'{mid:#x}', f'{lid:#x}', nm, f'{c["slave_addr7"]:#04x}',
                                          '; '.join(c['init']), ' | '.join(c['move']), c['origin'], c['move_steps'],
                                          c['move_delay_us'], '; '.join(c['release']), c['vcm_bits'], c['af_calib_bits'],
                                          c['ctrl_delay_us']])))
            else:
                print(f'{name}[{i}] sensor={sid:#x} module={mid:#x} lens={lid:#x} name={nm} '
                      f'gap={r[44:56].hex()} {c}')


if __name__ == '__main__':
    main()
