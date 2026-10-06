#!/usr/bin/env python3
"""Inventory every module-loading metadata file of the GQ5012BF1 stock build.
usage: module_metadata.py <stock-partitions-dir> <vendor_boot-platform-ramdisk-root> > module-metadata.tsv"""
import hashlib, os, sys
S, P = sys.argv[1], sys.argv[2]
roots = [
 ('vendor_boot (platform ramdisk fragment)', '/lib/modules', os.path.join(P, 'lib/modules'),
  'first-stage init (init_boot /init, libmodprobe LoadListedModules strict)', 'first-stage init, before first_stage_mount'),
 ('system_dlkm', '/system_dlkm/lib/modules', os.path.join(S, 'system_dlkm/lib/modules'),
  'insmod_sh: /vendor/bin/modprobe -a -d /system_dlkm/lib/modules $(cat modules.load)', 'second-stage early-init (insmod_sh service, async)'),
 ('vendor_dlkm', '/vendor_dlkm/lib/modules (= /vendor/lib/modules symlink)', os.path.join(S, 'vendor_dlkm/lib/modules'),
  'insmod_sh: /vendor/bin/modprobe -a -d /vendor/lib/modules $(cat modules.load); init.touch.rc modprobe; rc insmod', 'second-stage early-init/init/boot/property'),
 ('odm_dlkm', '/odm_dlkm', os.path.join(S, 'odm_dlkm'), 'none (no lib/modules)', '-'),
]
sem = {
 'modules.load': 'ordered list; each name loaded via LoadWithAliases(strict) -> hard deps (modules.dep, reverse order) -> soft pre -> module -> soft post',
 'modules.load.recovery': 'used instead of modules.load when first-stage BootMode==RECOVERY (androidboot.force_normal_boot!=1)',
 'modules.dep': 'hard dependency closure, absolute paths; module must be listed here to be loadable (ModuleExists/InsmodWithDeps)',
 'modules.alias': 'alias->module fnmatch expansion inside LoadWithAliases; no uevent modalias autoload (ueventd modalias_handling off, kernel.modprobe empty)',
 'modules.softdep': 'softdep <mod> pre:/post: <name>; non-strict loads around the module',
 'modules.options': 'per-module default params',
 'modules.blocklist': 'blocklist (only honoured by modprobe -b / first-stage); stock never passes -b',
 'modules.order': 'not consumed by Android libmodprobe',
}
print('file\tpartition\truntime_path\tentries\tsha256\tordering_semantics\tconsumer\tboot_phase\tused_by_stock')
for part, rpath, d, consumer, phase in roots:
    for name in ['modules.load', 'modules.load.recovery', 'modules.dep', 'modules.alias', 'modules.softdep', 'modules.options', 'modules.blocklist', 'modules.order']:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            b = open(p, 'rb').read(); n = sum(1 for l in b.decode().splitlines() if l.strip())
            used = 'yes'
            if name == 'modules.load.recovery': used = 'recovery boots only'
            if name == 'modules.alias' and part != 'vendor_boot (platform ramdisk fragment)': used = 'parsed; matches only explicit names'
            print('\t'.join([name, part, rpath + '/' + name, str(n), hashlib.sha256(b).hexdigest(), sem[name], consumer, phase, used]))
        else:
            print('\t'.join([name, part, rpath + '/' + name, '-', '-', sem[name], consumer, phase, 'ABSENT']))
    if os.path.isdir(d):
        kos = [f for r, _, fs in os.walk(d) for f in fs if f.endswith('.ko')]
        print('\t'.join(['*.ko', part, rpath, str(len(kos)), '-', 'module objects', consumer, phase, 'yes' if kos else 'no modules']))
