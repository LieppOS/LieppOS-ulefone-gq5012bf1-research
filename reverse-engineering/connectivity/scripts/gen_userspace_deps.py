#!/usr/bin/env python3
"""ELF NEEDED + device-node map for connectivity userspace (no decompilation)."""
import os, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ST=Path(os.environ['ST']); P=ST/'partitions'
items=[
('wifi','vendor/bin/hw/android.hardware.wifi-service-lazy'),('wifi','vendor/lib64/libwifi-hal.so'),
('wifi','vendor/bin/hw/wpa_supplicant'),('wifi','vendor/bin/hw/hostapd'),('wifi','vendor/bin/wlan_assistant'),
('wifi','vendor/lib64/libwifinvram.so'),('wifi','vendor/bin/wifi_dump'),
('bluetooth','vendor/bin/hw/android.hardware.bluetooth-service-mediatek'),('bluetooth','vendor/bin/hw/android.hardware.bluetooth@1.1-service-mediatek'),
('bluetooth','vendor/lib64/libbluetooth_mtk.so'),('bluetooth','vendor/lib64/libbluetooth_mtk_pure.so'),('bluetooth','vendor/lib64/android.hardware.bluetooth.audio-impl-mediatek.so'),
('bluetooth','vendor/bin/bt_dump'),
('gnss','vendor/bin/hw/android.hardware.gnss-service.mediatek'),('gnss','vendor/bin/hw/vendor.mediatek.hardware.gnss-service'),
('gnss','vendor/bin/mnld'),('gnss','vendor/lib64/libmnl.so'),('gnss','vendor/bin/mtk_agpsd'),('gnss','vendor/bin/mtk_lbs_service'),('gnss','vendor/bin/gps_dump'),
('fm','system_ext/lib64/libyftfmjni.so'),('fm','system_ext/app/YftFmRadio/lib/arm64/libyftfmjni.so'),('fm','vendor/lib64/hw/audio.primary.mediatek.so'),
('conninfra','vendor/bin/conninfra_loader'),('conninfra','vendor/bin/wmt_loader'),('conninfra','vendor/bin/wmt_launcher'),('connfem','vendor/lib64/libconnfem.so'),
]
rx=re.compile(r'/dev/[A-Za-z0-9_./-]+|/proc/(?:driver|stpbt)/[A-Za-z0-9_/-]+|/vendor/firmware/[A-Za-z0-9_.%/-]+|/mnt/vendor/nvdata/[A-Za-z0-9_/]+')
with open(ROOT/'userspace/dependency-map.tsv','w') as o:
    o.write('subsystem\tpath\tsha256_16\tneeded\tkernel_interfaces\n')
    for sub,rel in items:
        f=P/rel
        if not f.exists(): o.write(f'{sub}\t{rel}\tMISSING\t\t\n'); continue
        need=re.findall(r'\[(.+?)\]',subprocess.run(['readelf','-d',str(f)],capture_output=True,text=True).stdout)
        need=[n for n in need if n.endswith('.so')]
        s=subprocess.run(['strings',str(f)],capture_output=True,text=True).stdout
        k=sorted(set(rx.findall(s)))
        import hashlib; h=hashlib.sha256(f.read_bytes()).hexdigest()[:16]
        o.write(f"{sub}\t{rel}\t{h}\t{','.join(need)}\t{','.join(k)}\n")
print('ok')
