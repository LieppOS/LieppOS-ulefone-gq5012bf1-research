#!/usr/bin/env python3
"""Offline re-implementation of AOSP libmodprobe insertion order (android14
system/core/libmodprobe: LoadWithAliases / InsmodWithDeps / soft deps / EEXIST)
for the GQ5012BF1 stock module trees. No device access.

usage: modprobe_sim.py <stock-partitions-dir> <vendor_boot-platform-ramdisk-dir> <out.tsv>
Simulates, in boot order:
  1. first-stage init  : /lib/modules, modules.load (normal) [or modules.load.recovery]
  2. insmod_sh pass 1  : modprobe -a -d /system_dlkm/lib/modules $(cat modules.load)
  3. insmod_sh pass 2  : modprobe -a -d /vendor/lib/modules  $(cat modules.load)
  4. init.touch.rc     : modprobe -a -d /vendor/lib/modules <19 names>
  5. rc insmod         : gps_pwr/gps_scp (connsys ready), bt_drv (dup), msync2_* (on boot)
Each modprobe process has its own module_loaded_ set; already-loaded modules
come back from finit_module as EEXIST (counted as loaded, no new insertion).
"""
import os, sys

def canon(p):
    b = os.path.basename(p.strip())
    if b.endswith('.ko'): b = b[:-3]
    return b.replace('-', '_')

class Modprobe:
    def __init__(self, d, real_root, kernel):
        self.d = d; self.root = real_root; self.kernel = kernel
        self.deps = {}; self.pre = []; self.post = []; self.loaded = set(); self.count = 0; self.log = []
        for l in open(os.path.join(real_root, 'modules.dep')):
            if ':' not in l: continue
            k, v = l.split(':', 1)
            self.deps[canon(k)] = [k.strip()] + v.split()
        p = os.path.join(real_root, 'modules.softdep')
        if os.path.exists(p):
            for l in open(p):
                t = l.split()
                if not t or t[0] != 'softdep': continue
                if len(t) < 4: self.log.append(('softdep-malformed', ' '.join(t))); continue
                mod, st = t[1], ''
                for tok in t[2:]:
                    if tok in ('pre:', 'post:'): st = tok; continue
                    if not st: self.log.append(('softdep-malformed', ' '.join(t))); break
                    (self.pre if st == 'pre:' else self.post).append((mod, tok))
    def exists(self, m):
        dep = self.deps.get(m)
        if not dep: return False
        return os.path.isfile(os.path.join(self.root, os.path.basename(dep[0])))
    def insmod(self, path, phase, via):
        c = canon(path)
        if c in self.kernel:      # EEXIST
            self.loaded.add(c); self.log.append(('EEXIST', c, phase, via)); return True
        self.kernel[c] = (phase, len(self.kernel) + 1, path, via)
        self.loaded.add(c); self.count += 1; return True
    def with_deps(self, m, phase, via):
        dep = self.deps.get(m)
        if not dep: return False
        for d in reversed(dep[1:]):
            if not self.load(d, True, phase, 'dep-of:' + m): return False
        for mod, sd in self.pre:
            if mod == m: self.load(sd, False, phase, 'softpre-of:' + m)
        if not self.insmod(dep[0], phase, via): return False
        for mod, sd in self.post:
            if mod == m: self.load(sd, False, phase, 'softpost-of:' + m)
        return True
    def load(self, name, strict, phase, via):
        c = canon(name)
        if c in self.loaded: return True
        ok = False
        if self.exists(c) and self.with_deps(c, phase, via): ok = True
        if strict and not ok: self.log.append(('FAIL', c, phase, via))
        return ok or not strict

def main():
    S, P, out = sys.argv[1:4]
    recovery = len(sys.argv) > 4 and sys.argv[4] == 'recovery'
    kernel = {}
    rd = lambda p: [l.strip() for l in open(p) if l.strip()]
    fs = Modprobe('/lib/modules', P, kernel)
    lst = rd(os.path.join(P, 'modules.load.recovery' if recovery else 'modules.load'))
    for m in lst:
        if not fs.load(m, True, 'first-stage', 'modules.load'): break   # strict=true: stop at first failure
    print('first-stage: listed', len(lst), 'unique', len(set(map(canon, lst))), 'inserted', fs.count)
    logs = fs.log[:]
    if not recovery:
        for part, root in (('system_dlkm', os.path.join(S, 'system_dlkm/lib/modules')),
                           ('vendor', os.path.join(S, 'vendor_dlkm/lib/modules'))):
            m = Modprobe('/%s/lib/modules' % part, root, kernel)
            names = rd(os.path.join(root, 'modules.load'))
            for n in names: m.load(n, True, 'insmod_sh:' + part, 'modules.load')
            print('insmod_sh', part, 'listed', len(names), 'inserted', m.count); logs += m.log
        vd = os.path.join(S, 'vendor_dlkm/lib/modules')
        touch = 'tui-common.ko gt9895.ko ft3518u.ko st61y.ko gt9916.ko nt36672c.ko gt9886.ko synaptics_tcm.ko gt9896s.ko goodix_ts_v1315.ko focaltech_touch_spi_ft3680.ko hynitron.ko focaltech_touch_spi_ft8725.ko synaptics_spi.ko gt9966.ko ilitek.ko ilitek_spi.ko eswin_eph861x_zs1060.ko chipone_tddi.ko'.split()
        m = Modprobe('/vendor/lib/modules', vd, kernel)
        for n in touch: m.load(n, True, 'init.touch.rc', 'exec_background modprobe')
        print('init.touch.rc inserted', m.count, 'missing', sum(1 for x in m.log if x[0] == 'FAIL')); logs += m.log
        for n, trig in (('gps_pwr', 'init.gps_pwr.rc vendor.connsys.driver.ready=yes'), ('gps_scp', 'init.gps_scp.rc vendor.connsys.driver.ready=yes'),
                        ('bt_drv_6878', 'init.bt_drv.rc connsys ready'), ('msync2_dms', 'init.mt6878.rc on boot'), ('msync2_frd', 'init.mt6878.rc on boot')):
            path = os.path.join(vd, n + '.ko')
            if not os.path.exists(path): logs.append(('ENOENT', n, 'init-insmod', trig)); continue
            if n in kernel: logs.append(('EEXIST', n, 'init-insmod', trig)); continue
            kernel[n] = ('init-insmod', len(kernel) + 1, '/vendor/lib/modules/' + n + '.ko', trig)
    with open(out, 'w') as f:
        f.write('seq\tmodule\tphase\tpath\tpulled_in_by\n')
        for c, (ph, seq, path, via) in sorted(kernel.items(), key=lambda x: x[1][1]):
            f.write('%d\t%s\t%s\t%s\t%s\n' % (seq, c, ph, path, via))
    print('total inserted', len(kernel))
    for e in logs:
        if e[0] != 'EEXIST': print(*e, sep='\t')
    print('EEXIST events', sum(1 for e in logs if e[0] == 'EEXIST'))
    for e in logs:
        if e[0] == 'EEXIST' and e[2] in ('init-insmod',): print(*e, sep='\t')

if __name__ == '__main__':
    main()
