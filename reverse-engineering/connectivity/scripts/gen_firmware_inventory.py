#!/usr/bin/env python3
"""Connectivity firmware inventory (hash/size only - no blob is copied)."""
import hashlib, os, struct, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ST=Path(os.environ['ST'])
V=ST/'partitions/vendor'; F=ST/'firmware'
def h(b): return hashlib.sha256(b).hexdigest()
rows=[]
def add(path, sub, loader, consumer, when, board, src, cls, note=''):
    p=Path(path); b=p.read_bytes()
    rows.append([p.name, str(p.relative_to(ST)), len(b), h(b), sub, loader, consumer, when, board, src, cls, note])
for img,sub in (('connsys_wifi','wifi'),('connsys_bt','bluetooth'),('connsys_gnss','gnss')):
    p=F/f'{img}.img'; d=p.read_bytes()
    add(p,sub,'LK platform_load_connsys (partition)','CONNSYS MCU','boot (LK)','SKU-specific sub-image chosen by LK','no','PROPRIETARY FIRMWARE','MKIMG container, signed (cert1/cert2)')
    off=0
    while off+512<=len(d) and struct.unpack_from('<I',d,off)[0]==0x58881688:
        size=struct.unpack_from('<I',d,off+4)[0]; name=d[off+8:off+40].split(b'\0')[0].decode(); hs=struct.unpack_from('<I',d,off+0x34)[0]
        body=d[off+hs:off+hs+size]
        if not name.startswith('cert'):
            m=re.search(rb't-neptune[\x20-\x7e]{10,120}',body)
            used='USED (SKU 6637)' if name.endswith('mt6637') or name=='connsys_gnss' else 'not used (other SKU)'
            rows.append([name, f'{p.relative_to(ST)}@0x{off:x}', size, h(body), sub, 'LK', 'CONNSYS MCU', 'boot (LK)', used, 'no', 'PROPRIETARY FIRMWARE', m.group(0).decode() if m else ''])
        off=(off+hs+size+15)&~15
W=V/'firmware'
for n in sorted(os.listdir(W)):
    p=W/n
    if re.match(r'soc7_0_ram_(bt|mcu)',n): add(p,'bluetooth','bt_drv request_firmware (SUPPORT_BIN2IMG=0 only)','BGF MCU','never on 6878 (BIN2IMG=1)','generic','no','PROPRIETARY FIRMWARE','fallback/leftover')
    elif re.match(r'mt6635_fm_v1_',n): add(p,'fm','fmradio request_firmware (connac2x_patch_tbl)','A-die FM DSP','FM power-up','generic (ROM v1)','no','PROPRIETARY FIRMWARE','used for A-die 0x6637 (mapped to 6635 table)')
    elif re.search(r'_fm_',n): add(p,'fm','fmradio request_firmware','A-die FM DSP','never (other chip)','generic','no','PROPRIETARY FIRMWARE','other FM chips (6627/6630/6631/6632/soc)')
    elif n=='BT_FW.cfg': add(p,'bluetooth','btmtk_load_fw_cfg + libbluetooth_mtk','bt_drv/HAL','BT on','board config','text','BOARD CONFIG','coex 0, antswap[6878][6631] (unmatched), tssi')
    elif n=='connfem.cfg': add(p,'connfem','connfem cfg parser','connfem','probe','board config','text','BOARD CONFIG','0 bytes -> DT used')
    elif n=='conninfra.cfg': add(p,'conninfra','conninfra_conf request_firmware','conninfra','probe','board config','text','BOARD CONFIG','co_clock_flag=1')
    elif n=='fm_cust.cfg': add(p,'fm','fm_cust_config_file','fmradio','FM power-up','board config','text','BOARD CONFIG','RSSI thresholds, 50us de-emphasis, 26MHz OSC')
    elif n=='wifi.cfg': add(p,'wifi','wlanCfgParse','gen4m','Wi-Fi on','board config','text','BOARD CONFIG','DisGTKCipherCheck 1')
for p in sorted((V/'etc/wifi/nvram').iterdir()): add(p,'wifi','libwifinvram / wlan_assistant','NVRAM layout','NVRAM init','generic SOC7_0','no','PROPRIETARY DATA','descriptor tables; per-unit data lives in nvdata (not in image)')
add(V/'etc/MNL_Config.xml','gnss','mnld','GNSS engine','mnld start','board config','text','BOARD CONFIG','IFB/GGTO/DCB per chip (6637, 6686)')
hdr=['file','path','size','sha256','subsystem','loader','consumer','when_loaded','board_use','source_exists','class','note']
(ROOT/'firmware').mkdir(exist_ok=True)
with open(ROOT/'firmware/inventory.tsv','w') as o:
    o.write('\t'.join(hdr)+'\n'); [o.write('\t'.join(map(str,r))+'\n') for r in rows]
print(len(rows),'rows')
