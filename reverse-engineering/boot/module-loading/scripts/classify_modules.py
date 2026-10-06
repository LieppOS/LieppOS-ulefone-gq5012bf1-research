#!/usr/bin/env python3
"""Classify every shipped .ko by how stock loads it (phase 12) and summarise
subsystem positions in the resolved order (phase 11).
usage: classify_modules.py <stock-partitions> <vb-ramdisk-root> <resolved-load-order.tsv> <proc-modules.txt|->"""
import os, re, sys
S, P, R, PM = sys.argv[1:5]
c = lambda x: os.path.basename(x.strip()).replace('.ko', '').replace('-', '_')
rd = lambda p: [c(l) for l in open(p) if l.strip()]
vbl, vbr = rd(P + '/lib/modules/modules.load'), rd(P + '/lib/modules/modules.load.recovery')
vdl = rd(S + '/vendor_dlkm/lib/modules/modules.load'); sdl = rd(S + '/system_dlkm/lib/modules/modules.load')
res = {r.split('\t')[1]: r.rstrip('\n').split('\t') for r in list(open(R))[1:]}
loaded = None
if PM != '-':
    loaded = set(l.split()[0] for l in open(PM) if len(l.split()) >= 6)
ship = {}
for part, d in (('vendor_boot', P + '/lib/modules'), ('vendor_dlkm', S + '/vendor_dlkm/lib/modules'), ('system_dlkm', S + '/system_dlkm/lib/modules')):
    for r_, _, fs in os.walk(d):
        for f in fs:
            if f.endswith('.ko'): ship.setdefault(c(f), []).append(part)
rcload = {'tui_common': 'init.touch.rc modprobe', 'focaltech_touch_spi_ft3680': 'init.touch.rc modprobe', 'hynitron': 'init.touch.rc modprobe (also dep of spi_tiny_co5300_lcd in vendor modules.load)',
          'gps_pwr': 'init.gps_pwr.rc insmod on vendor.connsys.driver.ready=yes', 'gps_scp': 'init.gps_scp.rc insmod on vendor.connsys.driver.ready=yes',
          'msync2_frd': 'init.mt6878.rc insmod on boot', 'bt_drv_6878': 'vendor modules.load AND init.bt_drv.rc insmod (EEXIST)'}
print('module\tshipped_in\tvb_load\tvb_recovery\tsd_load\tvd_load\tresolved_phase\tresolved_seq\tpulled_in_by\tclass\tloaded_in_capture')
for m in sorted(ship):
    flags = [m in vbl, m in vbr, m in sdl, m in vdl]
    r = res.get(m, ['', '', '', '', ''])
    if r[2]:
        if r[2] == 'first-stage': cl = 'first-stage listed' if m in vbl else 'first-stage dependency-only'
        elif r[2].startswith('insmod_sh'):
            lst = sdl if 'system' in r[2] else vdl
            cl = ('second-stage listed' if m in lst else 'second-stage dependency-only')
        else: cl = 'rc/service loaded (' + rcload.get(m, r[4]) + ')'
        if len(ship[m]) > 1: cl += '; duplicate copy also in ' + ','.join(p for p in ship[m] if not r[3].startswith('/' + p) and not (p == 'vendor_boot' and r[3].startswith('/lib')))
        if m == 'hynitron': cl = 'rc/service OR dependency (race: init.touch.rc modprobe vs vendor pass; runtime bootprof shows touch modprobe pid)'
    else:
        if m in vbr: cl = 'recovery-only (modules.load.recovery)'
        elif re.match(r'met($|_)', m) or m in ('cmdq_test', 'emi_fake_eng', 'scheduler_ext'): cl = 'never loaded: debug/eng baggage (MET profiler / test / fake-eng)'
        else: cl = 'never loaded'
    print('\t'.join([m, ','.join(ship[m]), *('y' if f else '' for f in flags), r[2], r[0], r[4], cl, '' if loaded is None else ('y' if m in loaded else 'n')]))
