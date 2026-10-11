#!/usr/bin/env python3
"""Object-level NFC search under the reproduced historical compile command.
No module acceptance: no metadata fabrication or changes to stock/historical inputs.
"""
from pathlib import Path
import hashlib
import importlib.util
import itertools
import json
import subprocess
import sys

root = Path('/home/armol/kernel-work/allc/st21')
repos = [root.parent / 'nothing-kdm.git', root.parent / 'micode-kdm.git']
paths = ['drivers/misc/mediatek/nfc/st21nfc/st21nfc.c',
         'drivers/misc/mediatek/nfc/st21nfc/st21nfc.h']
stock_path = root.parent / 'stock-ops/vendor_boot_platform/st21nfc.ko'
parity = Path('/home/armol/androido_dalykai/LieppOS custom ROM/Reverse Engineer - DONE/ST21NFC/binary-analysis/ko-pair-parity.py')
spec = importlib.util.spec_from_file_location('kpp', parity)
kpp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kpp)

def functions(path):
    ko = kpp.KO(str(path))
    return {s['n']: ko.b[ko.secs[s['shndx']]['off'] + s['val']:
                           ko.secs[s['shndx']]['off'] + s['val'] + s['size']]
            for s in ko.syms if s['info'] & 15 == 2 and 0 < s['shndx'] < len(ko.secs)}

stock = functions(stock_path)
original = functions(Path('/home/armol/kernel-work/gki-12901745-workspace/lieppos/nfc/kernel_device_modules-6.1/drivers/misc/mediatek/nfc/st21nfc/st21nfc.o'))
assert functions(root/'historic-baseline.o') == original, 'baseline not reproduced'
versions = [{}, {}]
snapshots = []
for repo in repos:
    def git(*args):
        return subprocess.check_output(['git', '--git-dir', str(repo), *args])
    for commit in git('log', '--all', '--format=%H', '--', *paths).decode().split():
        ids = []
        for i, path in enumerate(paths):
            try:
                blob = git('rev-parse', f'{commit}:{path}').decode().strip()
                data = git('cat-file', 'blob', blob)
            except subprocess.CalledProcessError:
                ids = []
                break
            ids.append(blob)
            entry = versions[i].setdefault(blob, dict(data=data, provenance=[]))
            entry['provenance'].append(dict(repo=str(repo), commit=commit, path=path))
        if ids:
            snapshots.append(dict(repo=str(repo), commit=commit, blobs=ids))
results = []
probe_dir = root / 'history-inputs'
probe_dir.mkdir(exist_ok=True)
for n, (c, h) in enumerate(itertools.product(*[sorted(v) for v in versions]), 1):
    d = probe_dir / f'{c[:12]}-{h[:12]}'
    d.mkdir(exist_ok=True)
    (d/'st21nfc.c').write_bytes(versions[0][c]['data'])
    (d/'st21nfc.h').write_bytes(versions[1][h]['data'])
    obj = d/'st21nfc.o'
    run = subprocess.run(['nice', '-n', '19', sys.executable,
        str(root/'historical-object-probe.py'), str(d/'st21nfc.c'), str(obj)],
        capture_output=True, text=True)
    item = dict(c_blob=c, h_blob=h, compiler_exit=run.returncode,
                coherent=[s for s in snapshots if s['blobs'] == [c,h]],
                c_provenance=versions[0][c]['provenance'], h_provenance=versions[1][h]['provenance'])
    if run.returncode == 0:
        rebuilt = functions(obj)
        item.update(functions=len(rebuilt), shared=len(set(stock)&set(rebuilt)),
                    byte_exact=sum(stock[k] == rebuilt.get(k) for k in stock),
                    differences={k: dict(stock_size=len(stock[k]), build_size=len(rebuilt[k]),
                        differing_bytes=sum(a!=b for a,b in zip(stock[k],rebuilt[k])) + abs(len(stock[k])-len(rebuilt[k])))
                        for k in stock if k in rebuilt and stock[k] != rebuilt[k]},
                    missing=sorted(set(stock)-set(rebuilt)), extra=sorted(set(rebuilt)-set(stock)),
                    object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest())
    else:
        item['compiler_tail'] = run.stdout[-1800:] + run.stderr[-1800:]
    results.append(item)
    print(n, c[:12], h[:12], run.returncode, item.get('byte_exact'), flush=True)
(root/'public-history-object-scan.json').write_text(json.dumps(dict(
    scope='Object-level candidates only, not module acceptance',
    baseline='24/24 raw functions identical to preserved historical object',
    distinct_blobs=[len(v) for v in versions], snapshots=snapshots, results=results), indent=2)+'\n')
print('tested',len(results),'best',max(r.get('byte_exact',0) for r in results),flush=True)
