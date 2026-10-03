#!/usr/bin/env python3
"""firmware/inventory.tsv: modem firmware + carrier/config payloads (hashes/sizes only, nothing copied)."""
import hashlib, os, re, struct, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; ST = Path(os.environ['ST']); FW = ST/'firmware'; V = ST/'partitions/vendor'
rows = []
def h(b): return hashlib.sha256(b).hexdigest()
img = (FW/'modem.img').read_bytes()
rows.append(('modem_a/modem_b (md1img)', 'firmware/modem.img', 'MKIMG container', len(img), h(img), 'LK (ccci tags) -> MD1 EMI 0xd0000000', 'signed (cert1/cert2 per sub-image, verified by LK/secure boot)', 'MD1'))
cons = {'md1rom': 'MD1 ARM/NR baseband ROM+RAM image (CHECK_HEADER v6, MT6878_S00, NLWCG_6878, MOLY.NR17.R1.MP5.RC.MP.V23.9.P1, 2025/10/22 22:04, TK_MD)',
        'md1drdi': 'DRDI RF-setting database (per-SKU RF/band parameter sets; opaque/compressed)', 'md1dsp': 'MD DSP image (loaded to 0xed780000, 0x880000)',
        'cert1md': 'MD signing certificate', 'cert1': 'signing certificate', 'cert2': 'signing certificate',
        'md1_filter': 'logging filter (catcher_filter.bin)', 'md1_emfilter': 'EM filter', 'md1_dbginfo': 'symbol/debug info (xz) for MD crash decoding',
        'md1_dbginfodsp': 'DSP debug info (xz)', 'md1_mddb': 'MD trace database (EDB)', 'md1_mddbmetaodb': 'META ODB (XML.GZ)', 'md1_mdmlayout': 'mdm_layout_desc.dat (MD monitor layout)', 'md1_file_map': 'name -> file map (text)'}
off = 0
while off + 0x200 <= len(img):
    m, dsz, name = struct.unpack_from('<II32s', img, off)
    if m != 0x58881688: break
    hsz = struct.unpack_from('<I', img, off + 0x34)[0] or 0x200
    name = name.split(b'\0')[0].decode()
    body = img[off + hsz: off + hsz + dsz]
    key = name if name in cons else re.sub(r'_\d.*|_PLS.*|_Low.*', '', name)
    rows.append((f'  {name}', f'modem.img @0x{off:x}', 'sub-image', dsz, h(body), 'LK', 'cert-covered', cons.get(name, cons.get(key, 'filter variant'))))
    off = (off + hsz + dsz + 15) & ~15
mo = (FW/'mcf_ota.img').read_bytes()
rows.append(('mcf_ota_a/mcf_ota_b', 'firmware/mcf_ota.img', 'ext4', len(mo), h(mo), 'ccci_mdinit/MD MCF (modem configuration framework) over ccci_fs', 'no AVB footer; platform verification unknown; contents MD-parsed', 'MCF: MTK_OTA*.mcfota, MTK_OPOTA_SBPID_*.mcfopota (49), MTK_NWOTA_SBPID_*.mcfnwota (28), HW_CONFIG_SAR_Type0_Set1_MMRF.mcfrawota; custom/ empty'))
for sub in ('md', 'mdota'):
    d = V/'etc'/sub
    files = sorted(p for p in d.rglob('*') if p.is_file())
    hh = hashlib.sha256()
    tot = 0
    for p in files: b = p.read_bytes(); tot += len(b); hh.update(p.relative_to(d).as_posix().encode()); hh.update(h(b).encode())
    rows.append((f'vendor/etc/{sub}', f'partitions/vendor/etc/{sub}', f'{len(files)} files', tot, hh.hexdigest(), 'MD via ccci_fs / mdinit', 'vendor (dm-verity)',
                 'apncfg/ (504 IMS/emergency APN conf per MCC_MNC), cacerts/ikev2 (19), cacerts/tls (20), plmn/TS25 (217)' if sub == 'md' else 'empty'))
with open(ROOT/'firmware/inventory.tsv', 'w') as o:
    o.write('item\tlocation\ttype\tsize\tsha256\tloader\tsigned\tcontent/consumer\n')
    for r in rows: o.write('\t'.join(map(str, r)) + '\n')
print(len(rows))
