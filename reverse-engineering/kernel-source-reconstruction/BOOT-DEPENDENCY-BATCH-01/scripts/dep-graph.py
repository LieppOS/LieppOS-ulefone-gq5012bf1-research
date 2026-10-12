#!/usr/bin/env python3
"""Read-only stock ELF import/export census for the frozen BOOT-DEPENDENCY-BATCH-01 targets.

usage: dep-graph.py <stock-root> <gki-vmlinux.symvers> <out-dir>
Reads stock .ko files only (never writes them). Every import (__versions name+CRC) is resolved to the
vendor_boot module exporting it (exact CRC compared) or to GKI 12901745 vmlinux.symvers.
"""
import csv, json, struct, sys, collections
from pathlib import Path

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
STOCK, SYMVERS, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)


class KO:
    def __init__(self, path):
        self.b = b = Path(path).read_bytes()
        assert b[:4] == b'\x7fELF' and b[4] == 2
        shoff, = struct.unpack_from('<Q', b, 0x28)
        shentsize, shnum, shstrndx = struct.unpack_from('<HHH', b, 0x3a)
        self.secs = []
        for i in range(shnum):
            n, t, fl, a, off, size, link, info, al, es = struct.unpack_from('<IIQQQQIIQQ', b, shoff + i * shentsize)
            self.secs.append(dict(name=n, type=t, flags=fl, off=off, size=size, link=link, info=info))
        so = self.secs[shstrndx]['off']
        for s in self.secs:
            s['n'] = self.cstr(so + s['name'])
        self.by = {s['n']: s for s in self.secs}
        st = next(s for s in self.secs if s['type'] == 2)
        strs = self.secs[st['link']]['off']
        self.syms = []
        for i in range(st['size'] // 24):
            nm, info, oth, shn, val, size = struct.unpack_from('<IBBHQQ', b, st['off'] + i * 24)
            self.syms.append(dict(n=self.cstr(strs + nm), info=info, shndx=shn, val=val, size=size))

    def cstr(self, o):
        return self.b[o:self.b.index(b'\0', o)].decode(errors='replace')

    def versions(self):
        s = self.by.get('__versions')
        out = {}
        if s:
            for i in range(s['size'] // 64):
                crc, = struct.unpack_from('<Q', self.b, s['off'] + i * 64)
                out[self.b[s['off'] + i * 64 + 8:s['off'] + (i + 1) * 64].split(b'\0')[0].decode()] = crc & 0xffffffff
        return out

    def exports(self):
        out = {}
        ns = {y['n'][len('__kstrtabns_'):]: y for y in self.syms if y['n'].startswith('__kstrtabns_')}
        for y in self.syms:
            if not y['n'].startswith('__ksymtab_') or y['shndx'] in (0, 0xfff1) or y['shndx'] >= len(self.secs):
                continue
            name = y['n'][len('__ksymtab_'):]
            sec = self.secs[y['shndx']]['n']
            lic = 'EXPORT_SYMBOL_GPL' if sec == '__ksymtab_gpl' else 'EXPORT_SYMBOL'
            cs = self.by.get(sec.replace('__ksymtab', '__kcrctab'))
            crc = struct.unpack_from('<I', self.b, cs['off'] + y['val'] // 12 * 4)[0] if cs else None
            space = ''
            if name in ns and ns[name]['shndx'] < len(self.secs):
                space = self.cstr(self.secs[ns[name]['shndx']]['off'] + ns[name]['val'])
            target = next((z for z in self.syms if z['n'] == name and 0 < z['shndx'] < 0xff00), None)
            out[name] = dict(licence=lic, crc=crc, namespace=space, symbol_type={2: 'FUNC', 1: 'OBJECT'}.get(target['info'] & 15, 'OTHER') if target else 'UNDEF')
        return out

    def modinfo(self):
        s = self.by['.modinfo']
        return dict(x.split('=', 1) for x in self.b[s['off']:s['off'] + s['size']].decode(errors='replace').split('\0') if '=' in x)


audit = {r['stock_paths'].split(';')[0]: r for r in csv.DictReader((R / 'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv').open(), delimiter='\t')}
by_path = {}
for r in audit.values():
    for p in r['stock_paths'].split(';'):
        by_path[p] = r
manifest = list(csv.DictReader((P / 'BATCH-MANIFEST.tsv').open(), delimiter='\t'))
gki = {}
for l in SYMVERS.read_text().splitlines():
    c, s, m, lic, *ns = l.split('\t')
    gki[s] = dict(crc=int(c, 16), module=m, licence=lic, namespace=ns[0] if ns else '')
VB = 'workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/'
exporters = collections.defaultdict(list)
for f in sorted((STOCK / 'vendor-ramdisks/platform-extracted/lib/modules').glob('*.ko')):
    k = KO(f)
    for s, e in k.exports().items():
        exporters[s].append(dict(e, module=f.name, row=by_path[VB + f.name]))
graph, summary = [], {}
for m in manifest:
    k = KO(STOCK / m['stock_path'].removeprefix('workspace/gq5012bf1/stock/'))
    mi = k.modinfo()
    deps = [d for d in mi.get('depends', '').split(',') if d]
    imports = k.versions()
    undefined = sorted(y['n'] for y in k.syms if y['shndx'] == 0 and y['n'])
    counts = collections.Counter()
    for s in sorted(set(imports) | set(undefined)):
        crc = imports.get(s)
        if s in exporters:
            assert len(exporters[s]) == 1, (s, [e['module'] for e in exporters[s]])
            e = exporters[s][0]
            row = e['row']
            kind = 'VENDOR_BOOT_MODULE'
            prov, lic, ns, pcrc = e['module'], e['licence'], e['namespace'], e['crc']
            pcls, prepo, pcommit = row['source_status'], row['source_repo'], row['source_commit']
        elif s in gki:
            g = gki[s]
            kind = 'GKI_VMLINUX'
            prov, lic, ns, pcrc, pcls, prepo, pcommit = 'vmlinux', g['licence'], g['namespace'], g['crc'], 'GKI', 'android.googlesource.com/kernel/common', '6b18f0b574ab3267615ae6ce642d5a7c3c21ac09 (GKI 12901745 symvers)'
        else:
            kind = 'UNRESOLVED'
            prov = lic = ns = pcls = prepo = pcommit = ''
            pcrc = None
        counts[kind] += 1
        graph.append(dict(target=m['filename'], target_module_id=m['module_id'], symbol=s,
                          import_crc=f'0x{crc:08x}' if crc is not None else 'NO_VERSIONS_ENTRY',
                          provider_kind=kind, provider=prov,
                          provider_crc=f'0x{pcrc:08x}' if pcrc is not None else '',
                          crc_consistent='yes' if crc is not None and crc == pcrc else ('n/a' if crc is None else 'NO'),
                          licence=lic, namespace=ns, provider_class=pcls, provider_source_repo=prepo, provider_source_commit=pcommit,
                          modinfo_depends='yes' if prov.removesuffix('.ko') in deps else ('n/a' if kind != 'VENDOR_BOOT_MODULE' else 'NO')))
    exp = k.exports()
    summary[m['filename']] = dict(depends=deps, imports=len(imports), undefined=len(undefined), import_kinds=dict(counts),
                                  vendor_providers=sorted({g['provider'] for g in graph if g['target'] == m['filename'] and g['provider_kind'] == 'VENDOR_BOOT_MODULE'}),
                                  exports=len(exp), export_licences=dict(collections.Counter(e['licence'] for e in exp.values())),
                                  export_namespaces=sorted({e['namespace'] for e in exp.values() if e['namespace']}),
                                  reverse_importers=sorted({e2 for s in exp for e2 in []}),
                                  intree=mi.get('intree', ''), srcversion=mi.get('srcversion', ''), vermagic=mi.get('vermagic', ''))
# reverse importers among all vendor_boot modules
for f in sorted((STOCK / 'vendor-ramdisks/platform-extracted/lib/modules').glob('*.ko')):
    k = KO(f)
    v = set(k.versions())
    for m in manifest:
        if f.name == m['filename']:
            continue
        mine = set(KO(STOCK / m['stock_path'].removeprefix('workspace/gq5012bf1/stock/')).exports())
        if v & mine:
            summary[m['filename']]['reverse_importers'].append(f'{f.name}({len(v & mine)})')
with (OUT / 'BOOT-DEPENDENCY-GRAPH.tsv').open('w') as fh:
    w = csv.DictWriter(fh, list(graph[0]), delimiter='\t', lineterminator='\n')
    w.writeheader()
    w.writerows(graph)
(OUT / 'dependency-summary.json').write_text(json.dumps(summary, indent=1, sort_keys=True) + '\n')
bad = [g for g in graph if g['crc_consistent'] == 'NO' or g['provider_kind'] == 'UNRESOLVED' or g['modinfo_depends'] == 'NO']
print('edges', len(graph), 'inconsistent/unresolved', len(bad))
for g in bad[:20]:
    print(' ', g['target'], g['symbol'], g['provider_kind'], g['provider'], g['import_crc'], g['provider_crc'], g['modinfo_depends'])
for n, s in summary.items():
    print(n, s['import_kinds'], s['vendor_providers'], 'exp', s['exports'], s['export_namespaces'], 'rev', s['reverse_importers'])
