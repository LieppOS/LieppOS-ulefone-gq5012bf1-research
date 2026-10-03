#!/usr/bin/env python3
"""ELF NEEDED + kernel-interface map for modem/telephony userspace (no decompilation).
Binaries that link the generic CCCI node-name table (libccci_util) contain every /dev/ccci*
string; those are collapsed to 'CCCI_NODE_TABLE' so only specific references remain."""
import os, re, subprocess, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ST=Path(os.environ['ST']); P=ST/'partitions'
items=[
('ccci-infra','vendor/bin/ccci_mdinit'),('ccci-infra','vendor/bin/ccci_rpcd'),('ccci-infra','vendor/lib64/libccci_util.so'),
('ccci-infra','system_ext/lib64/libccci_util_sys.so'),('ccci-infra','vendor/bin/md_monitor'),('ccci-infra','vendor/bin/muxreport'),
('ril','vendor/bin/hw/mtkfusionrild'),('ril','vendor/lib64/libmtk-ril.so'),('ril','vendor/lib64/libmtkmipc-ril.so'),('ril','vendor/lib64/librilfusion.so'),
('ril','vendor/lib64/libmipc.so'),('ril','vendor/lib64/libmtkrilutils.so'),('ril','vendor/lib64/libril.so'),('ril','vendor/lib64/libviamipc-ril.so'),
('ril','vendor/lib64/libvia-ril.so'),('ril','vendor/lib64/libgwsdv3-ril.so'),('ril','vendor/lib64/libwpfa.so'),('ril','vendor/lib64/libcarrierconfig.so'),
('sim','vendor/lib64/libsimlock.so'),('sim','vendor/lib64/libsimmelock.so'),('sim','vendor/bin/bip_ap'),
('at','vendor/bin/atcid'),
('ims','vendor/bin/volte_clientapi_ua'),('ims','vendor/bin/rcs_volte_stack'),('ims','vendor/bin/volte_rcs_ua'),('ims','vendor/lib64/librcs_volte_core.so'),
('ims','vendor/lib64/libipsec_ims_shr.so'),('ims','vendor/bin/ipsec_mon'),('ims','vendor/bin/hw/vtservice_aidl'),('ims','system_ext/bin/vtservice'),
('ims','system_ext/lib64/libvt_avsync.so'),('ims','system_ext/lib64/libimsma.so'),
('nvram','vendor/bin/nvram_daemon'),('nvram','vendor/bin/hw/vendor.mediatek.hardware.nvram-service'),
('gnss','vendor/bin/mnld'),('gnss','vendor/bin/mtk_agpsd'),('thermal','vendor/bin/thermal_core'),
('logging','system_ext/bin/mdlogger'),('logging','system_ext/bin/emdlogger'),('logging','system_ext/lib64/libterservice.so'),
('audio','vendor/lib64/hw/audio.primary.mediatek.so'),('audio','vendor/lib64/libMtkSpeechEnh.so'),('audio','vendor/lib64/libspeech_enh_lib.so'),
('factory','vendor/bin/meta_tst'),('factory','vendor/bin/factory'),
]
rx=re.compile(r'/dev/(?:ccci|ttyC|ccmni|eemcs|emd|block/by-name/(?:md|nv|protect|proinfo))[A-Za-z0-9_./-]*|/sys/kernel/ccci/\w+|/proc/ccci\w*|/mnt/vendor/(?:nvdata|nvcfg|protect_[fs])[A-Za-z0-9_/]*|ccmni\d+')
with open(ROOT/'userspace/dependency-map.tsv','w') as o:
    o.write('subsystem\tpath\tsha256_16\tneeded\tkernel_interfaces\n')
    for sub,rel in items:
        f=P/rel
        if not f.exists(): o.write(f'{sub}\t{rel}\tMISSING\t\t\n'); continue
        need=re.findall(r'\[(.+?)\]',subprocess.run(['readelf','-d',str(f)],capture_output=True,text=True).stdout)
        need=[n for n in need if n.endswith('.so')]
        s=subprocess.run(['strings',str(f)],capture_output=True,text=True).stdout
        k=sorted(set(rx.findall(s)))
        if sum(1 for x in k if x.startswith('/dev/ccci'))>40:
            k=['CCCI_NODE_TABLE']+[x for x in k if not (x.startswith('/dev/ccci') or x.startswith('/dev/eemcs') or x.startswith('/dev/emd') or re.match(r'/dev/ttyC\d$',x))]
        if sum(1 for x in k if x.startswith('ccmni'))>10:
            k=[x for x in k if not x.startswith('ccmni')]+['CCMNI_NAME_TABLE']
        h=hashlib.sha256(f.read_bytes()).hexdigest()[:16]
        o.write(f"{sub}\t{rel}\t{h}\t{','.join(need)}\t{','.join(k)}\n")
print('ok')
