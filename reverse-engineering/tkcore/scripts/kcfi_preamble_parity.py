#!/usr/bin/env python3
"""Compare the KCFI type-id word preceding every function of stock and rebuilt
tkcore_drv.ko and name each prototype through
reverse-engineering/scripts/ko-kcfi-typeid.py (shared xxHash64 oracle).
usage: kcfi_preamble_parity.py stock.ko rebuilt.ko [out.tsv]"""
import subprocess, sys, re, struct, os, importlib.util
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('k', os.path.join(here, '..', '..', 'scripts', 'ko-kcfi-typeid.py'))
k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
PROTOS = {
 '_ZTSFiP3teeE': 'int (struct tee *)',
 '_ZTSFiP11tee_sessionP7tee_cmdE': 'int (struct tee_session *, struct tee_cmd *)',
 '_ZTSFiP11tee_sessionE': 'int (struct tee_session *)',
 '_ZTSFP7tee_shmP3teemjE': 'struct tee_shm *(struct tee *, size_t, uint32_t)',
 '_ZTSFvP7tee_shmE': 'void (struct tee_shm *)',
 '_ZTSFiP7tee_shmE': 'int (struct tee_shm *)',
 '_ZTSFiP6tee_tzjmmmP19invoke_tee_responseE': 'int (struct tee_tz *, uint32_t, unsigned long, unsigned long, unsigned long, struct invoke_tee_response *)  [invoke_tee_fn]',
 '_ZTSFiP6tee_tzPvmbPmPjE': 'int (struct tee_tz *, void *, size_t, bool, unsigned long *, uint32_t *)  [build_mem_share_handle_fn]',
 '_ZTSFbPvE': 'bool (void *)', '_ZTSFbPviE': 'bool (void *, int)', '_ZTSFiPvE': 'int (void *)',
 '_ZTSFvP6tee_tzP19invoke_tee_responseP21tee_task_cpu_affinityE': 'void (struct tee_tz *, struct invoke_tee_response *, struct tee_task_cpu_affinity *)',
 '_ZTSFivE': 'int (void)', '_ZTSFvvE': 'void (void)', '_ZTSFijE': 'int (unsigned int)',
 '_ZTSFiP10ffa_deviceE': 'int (struct ffa_device *)', '_ZTSFvP10ffa_deviceE': 'void (struct ffa_device *)',
 '_ZTSFiP15platform_deviceE': 'int (struct platform_device *)',
 '_ZTSFP8shm_poolP6devicemPvmE': 'struct shm_pool *(struct device *, size_t, void *, unsigned long)',
 '_ZTSFvP6deviceP8shm_poolE': 'void (struct device *, struct shm_pool *)',
 '_ZTSFPvP6deviceP8shm_poolmE': 'void *(struct device *, struct shm_pool *, unsigned long)',
 '_ZTSFmP6deviceP8shm_poolPvE': 'unsigned long (struct device *, struct shm_pool *, void *)',
 '_ZTSFmP6deviceP8shm_poolmmE': 'unsigned long (struct device *, struct shm_pool *, size_t, size_t)',
 '_ZTSFiP6deviceP8shm_poolmPmE': 'int (struct device *, struct shm_pool *, unsigned long, size_t *)',
 '_ZTSFbP6deviceP8shm_poolmE': 'bool (struct device *, struct shm_pool *, unsigned long)',
 '_ZTSFvP6deviceP8shm_poolbE': 'void (struct device *, struct shm_pool *, bool)',
 '_ZTSFbP8shm_poolE': 'bool (struct shm_pool *)', '_ZTSFvP8shm_poolE': 'void (struct shm_pool *)',
 '_ZTSFvP9handle_dbE': 'void (struct handle_db *)', '_ZTSFiP9handle_dbPvE': 'int (struct handle_db *, void *)',
 '_ZTSFPvP9handle_dbiE': 'void *(struct handle_db *, int)',
}
REV = {k.kcfi(m) & 0xffffffff: (m, d) for m, d in PROTOS.items()}
def info(ko):
    b = open(ko, 'rb').read(); sec = {}
    for l in subprocess.check_output(['llvm-readelf', '-S', '-W', ko]).decode().split('\n'):
        m = re.search(r'\[\s*(\d+)\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+([0-9a-f]+)', l)
        if m: sec[int(m.group(1))] = int(m.group(3), 16)
    out = {}
    for l in subprocess.check_output(['llvm-readelf', '-s', '-W', ko]).decode().split('\n'):
        p = l.split()
        if len(p) >= 8 and p[3] == 'FUNC' and p[6].isdigit():
            v = int(p[1], 16); off = sec[int(p[6])] + v
            w = struct.unpack('<I', b[off - 4:off])[0] if v >= 4 else None
            out[p[7]] = w if (w is not None and w in REV) else (w if w is not None and (w >> 24) not in (0xd6, 0x17, 0x14, 0x94, 0xa9, 0xf9) else None)
    return out
a, b = info(sys.argv[1]), info(sys.argv[2])
rows = ['function\tstock_kcfi\trebuilt_kcfi\tmangled\tprototype\tresult']; n = ok = named = 0
for f in sorted(a):
    ka, kb = a[f], b.get(f)
    if ka is None or ka not in REV:
        rows.append(f'{f}\t-\t-\t-\t(no KCFI preamble: not address-taken / not global)\t{"EXACT" if (kb is None or kb not in REV) else "DIFF"}'); continue
    n += 1; m, d = REV[ka]; named += 1; res = 'EXACT' if ka == kb else 'DIFF'; ok += res == 'EXACT'
    rows.append(f'{f}\t0x{ka:08x}\t' + (f'0x{kb:08x}' if kb is not None else '-') + f'\t{m}\t{d}\t{res}')
txt = '\n'.join(rows) + '\n'
(open(sys.argv[3], 'w').write(txt) if len(sys.argv) > 3 else sys.stdout.write(txt))
print(f'KCFI preambles: {ok}/{n} equal, {named}/{n} named', file=sys.stderr)
