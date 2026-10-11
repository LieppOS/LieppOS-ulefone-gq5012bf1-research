#!/usr/bin/env python3
"""Compare existing B1/B2 object, config, symvers and source-tree evidence.
Writes no original operands. Debug stripping uses explicit outputs on rebuilt objects.
Usage: compare-build-inputs.py FAMILY WS1 WS2 REPORT_JSON
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

family, a, b, report = sys.argv[1:]
a, b, report = Path(a).resolve(), Path(b).resolve(), Path(report).resolve()
assert family in ('cmdq', 'connectivity', 'thermal')
oa, ob = a/'out/B1', b/'out/B2'

def parse_hashes(p):
    return {line.split(None, 1)[1].lstrip('./'): line.split(None, 1)[0]
            for line in p.read_text().splitlines()}

def locate(ws, path):
    if family != 'connectivity':
        return ws/'src/kdm'/path
    prefix, suffix = path.split('/', 1)
    return {'kdm': ws/'src/kdm', 'native': ws/'native-kout',
            'nkm': ws/'o/vendor/mediatek/kernel_modules/connectivity'}[prefix]/suffix

ha, hb = parse_hashes(oa/'INTERMEDIATE-SHA256SUMS'), parse_hashes(ob/'INTERMEDIATE-SHA256SUMS')
assert set(ha) == set(hb), 'different intermediate object inventories'
results = []
with tempfile.TemporaryDirectory(prefix='allc-object-compare-') as temp:
    for name in sorted(ha):
        pa, pb = locate(a, name), locate(b, name)
        assert hashlib.sha256(pa.read_bytes()).hexdigest() == ha[name], name
        assert hashlib.sha256(pb.read_bytes()).hexdigest() == hb[name], name
        if ha[name] == hb[name]:
            results.append(dict(object=name, raw_identical=True, strip_debug_identical=True))
            continue
        da, db = Path(temp)/'a.o', Path(temp)/'b.o'
        for source, output in ((pa, da), (pb, db)):
            subprocess.run(['llvm-strip', '--strip-debug', '-o', str(output), str(source)], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        results.append(dict(object=name, raw_identical=False,
                            strip_debug_identical=da.read_bytes() == db.read_bytes()))
configs = []
for relative in (['o/kout/.config','native-kout/.config','btfbase/out/.config']
                 if family == 'connectivity' else ['kout/.config'] +
                 (['native-kout/.config','btfbase/out/.config'] if family == 'thermal' else [])):
    pa, pb = a/relative, b/relative
    assert pa.read_bytes() == pb.read_bytes(), relative
    configs.append(dict(path=relative, sha256=hashlib.sha256(pa.read_bytes()).hexdigest(), identical=True))
symvers = []
for pa in sorted(oa.glob('*symvers*')):
    if 'sha256' in pa.name or not pa.is_file(): continue
    pb = ob/pa.name
    def clean(p, ws):
        return p.read_text().replace(str(ws), '<WORKSPACE>')
    assert pb.exists() and clean(pa,a) == clean(pb,b), pa.name
    symvers.append(dict(path=pa.name, identical_after_workspace_path_normalization=True))
source_trees = []
for name in ['TARGET-SOURCE-TREE', 'SOURCE-TREES.tsv']:
    if (oa/name).exists() and (ob/name).exists():
        same = (oa/name).read_bytes() == (ob/name).read_bytes()
        assert same, name
        source_trees.append(dict(path=name, identical=True))
result = dict(family=family, objects=results, configurations=configs, symvers=symvers,
              source_trees=source_trees,
              raw_identical_objects=sum(x['raw_identical'] for x in results),
              strip_debug_identical_objects=sum(x['strip_debug_identical'] for x in results),
              objects_with_non_debug_difference=[x['object'] for x in results if not x['strip_debug_identical']])
# Native ADC intermediates are a separate recorded inventory.
if family == 'thermal':
    hna, hnb = parse_hashes(oa/'NATIVE-INTERMEDIATE-SHA256SUMS'), parse_hashes(ob/'NATIVE-INTERMEDIATE-SHA256SUMS')
    assert hna.keys() == hnb.keys()
    result['native_intermediates'] = {}
    with tempfile.TemporaryDirectory(prefix='allc-native-compare-') as temp:
        for key in hna:
            pa, pb = a/'native-kout'/key, b/'native-kout'/key
            assert hashlib.sha256(pa.read_bytes()).hexdigest() == hna[key], key
            assert hashlib.sha256(pb.read_bytes()).hexdigest() == hnb[key], key
            da, db = Path(temp)/'a.o', Path(temp)/'b.o'
            for source, output in ((pa, da), (pb, db)):
                subprocess.run(['llvm-strip', '--strip-debug', '-o', str(output), str(source)], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            result['native_intermediates'][key] = dict(raw_identical=hna[key] == hnb[key],
                strip_debug_identical=da.read_bytes() == db.read_bytes(),
                B1_sha256=hna[key], B2_sha256=hnb[key])
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(json.dumps(result, indent=2)+'\n')
print(family, len(results), 'objects;', result['raw_identical_objects'], 'raw identical;',
      result['strip_debug_identical_objects'], 'strip-debug identical;', len(configs), 'configs;', len(symvers), 'symvers')
print('non-debug object differences:', result['objects_with_non_debug_difference'])
