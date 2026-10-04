#!/usr/bin/env python3
"""Object composition of mediatek-drm.ko.

usage: objmap.py STOCK.ko BUILD_DIR PARITY_DIR OUT_DIR

* link order = mediatek-drm.mod (kbuild), per-object defined FUNC/OBJECT symbols from the
  rebuilt .o files (B);
* stock (A) .text addresses: every A function is assigned to the object that defines a
  function of the same name in B; A-only functions are assigned to the object of the
  nearest preceding A function (link order is preserved without LTO);
* emits object-map.tsv (A .text range, object, confidence, funcs, data, donor path) and
  per-object parity rollup (object-groups.tsv) from PARITY_DIR/function-parity.tsv and
  data-parity.tsv.
"""
import os, sys, subprocess, re, collections

A, BD, PD, OUT = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)


def syms(path):
    out = subprocess.run(['llvm-readelf', '-s', '-W', path], capture_output=True, text=True).stdout
    secs = {}
    sh = subprocess.run(['llvm-readelf', '-S', '-W', path], capture_output=True, text=True).stdout
    for m in re.finditer(r'\[\s*(\d+)\]\s+(\S+)', sh):
        secs[m.group(1)] = m.group(2)
    res = []
    for l in out.splitlines():
        p = l.split()
        if len(p) >= 8 and p[3] in ('FUNC', 'OBJECT') and p[6] not in ('UND', 'ABS'):
            res.append((p[7], p[3], int(p[1], 16), int(p[2], 0) if not p[2].startswith('0x') else int(p[2], 16), secs.get(p[6], p[6]), p[4]))
    return res


mod = open(os.path.join(BD, 'mediatek-drm.mod')).read().split()
objs = [os.path.relpath(o, BD) for o in mod]
fn2obj, obj2fn, obj2data = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(list)
dat2obj = {}
norm = lambda n: re.sub(r'__UNIQUE_ID_(\w+?)\d+$', r'__UNIQUE_ID_\1N', n)
for o in objs:
    for name, typ, addr, size, sec, bind in syms(os.path.join(BD, o)):
        if typ == 'FUNC':
            if o not in fn2obj[name]: fn2obj[name].append(o)
        else:
            dat2obj.setdefault(norm(name), o)

asyms = syms(A)
afuncs = sorted([s for s in asyms if s[1] == 'FUNC' and s[4] == '.text'], key=lambda s: s[2])
cur = None
assign = []
for name, typ, addr, size, sec, bind in afuncs:
    if name in fn2obj:
        ci = objs.index(cur) if cur else 0
        cands = [x for x in fn2obj[name] if objs.index(x) >= ci]
        o = cands[0] if cands else fn2obj[name][0]; conf = 'symbol' if cands else 'symbol (out-of-order!)'
        cur = o
    else:
        o = cur; conf = 'A-only (neighbour)'
    assign.append((name, addr, size, o, conf))

fp = {}
for l in open(os.path.join(PD, 'function-parity.tsv')).read().splitlines()[1:]:
    c = l.split('\t'); fp[c[0]] = c[3]
dp = {}
for l in open(os.path.join(PD, 'data-parity.tsv')).read().splitlines()[1:]:
    c = l.split('\t'); dp[norm(c[0])] = c

by = collections.OrderedDict((o, dict(funcs=[], lo=None, hi=0, conf=set())) for o in objs)
for name, addr, size, o, conf in assign:
    d = by[o]; d['funcs'].append(name); d['conf'].add(conf.split(' ')[0])
    d['lo'] = addr if d['lo'] is None else min(d['lo'], addr); d['hi'] = max(d['hi'], addr + size)
for name, typ, addr, size, sec, bind in asyms:
    if typ == 'OBJECT':
        o = dat2obj.get(norm(name))
        if o:
            obj2data[o].append(norm(name))

with open(os.path.join(OUT, 'object-map.tsv'), 'w') as f:
    f.write('stock_text_range\tobject\tconfidence\tfunctions\tdata_objects\tdonor_path\tstatus\n')
    for o, d in by.items():
        rng = f'0x{d["lo"]:06x}-0x{d["hi"]:06x}' if d['lo'] is not None else '-'
        src = 'drivers/gpu/drm/mediatek/mediatek_v2/' + o.replace('.o', '.c')
        conf = 'proven (symbol names, link order)' if d['conf'] <= {'symbol'} else 'proven + ' + ','.join(sorted(d['conf'] - {'symbol'}))
        f.write(f'{rng}\t{o}\t{conf}\t{len(d["funcs"])}\t{len(obj2data[o])}\t{src}\t\n')

with open(os.path.join(OUT, 'object-groups.tsv'), 'w') as f:
    f.write('object\tstock_funcs\tbyte_identical\tlayout_only\tsize_equal_diff\tsize_diff\tone_sided\tstock_data\tdata_bytes_equal\tdiffering_functions\n')
    for o, d in by.items():
        st = collections.Counter(fp.get(n, 'ONE-SIDED') for n in d['funcs'])
        # .modinfo entries (__UNIQUE_ID_author/license/<param>type...) are compared positionally
        # by the parity tool's modinfo check, not as data objects -> excluded here
        dd = [n for n in obj2data[o] if n in dp]
        de = sum(1 for n in dd if dp[n][-1] == 'EXACT')
        diff = [n for n in d['funcs'] if fp.get(n) not in ('BYTE-IDENTICAL',)]
        f.write('\t'.join(map(str, [o, len(d['funcs']), st['BYTE-IDENTICAL'], st['LAYOUT-ONLY'], st['SIZE-EQUAL'], st['SIZE-DIFF'], st['ONE-SIDED'],
                                    len(dd), de, ' '.join(diff[:40]) + (' …' if len(diff) > 40 else '')])) + '\n')
print('objects', len(objs), 'A funcs', len(afuncs), 'out-of-order', sum(1 for a in assign if 'out-of-order' in a[4]),
      'A-only', sum(1 for a in assign if a[4].startswith('A-only')))
